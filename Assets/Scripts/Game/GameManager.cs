using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    // ── Lock-on reticle (world-space canvas, drawn over the locked target) ────
    GameObject reticleCanvasGO;
    GameObject reticleGO;
    Texture2D  reticleTex;
    Transform  lockTarget;   // set by PlayerController via OnLockTargetChanged

    // "You are targeted" halo — shown over the player while an enemy is locked on.
    GameObject haloCanvasGO;
    GameObject haloGO;

    // ── HUD bars (Canvas) ─────────────────────────────────────────────────────
    GameObject hudBarsGO;
    Image      healthFillImage;
    Text       formText;
    Text       notifLabel;

    // ── Menu / death screens (Canvas) ─────────────────────────────────────────
    GameObject menuPanelGO;
    GameObject deathPanelGO;
    Text       deathScoreText;

    // ── Notification (Canvas, fades out) ──────────────────────────────────────
    float _notifTimer = 0f;

    // ── Scene references ──────────────────────────────────────────────────────
    PlayerController player;
    EcosystemManager ecosystem;
    Camera           cam;
    Morphivore.World.BiomeTerrain terrain;

    // Seeds this run's world. One seed per run reproduces a whole world exactly,
    // which is what §4.10's debugging story and §3.3's generator invariants need.
    int runSeed;

    bool gameStarted  = false;
    bool deathHandled = false;

    // ─────────────────────────────────────────────────────────────────────────

    void Start()
    {
        // Load the generated world content up front so a missing or malformed
        // file reports itself at boot rather than on the first spawn. Failure is
        // non-fatal — the ecosystem falls back to the prototype tables.
        Morphivore.Content.ContentDatabase.Load();

        // One seed per run. Logged so a bad world can be reproduced exactly
        // rather than hunted for (§4.10).
        runSeed = Random.Range(int.MinValue, int.MaxValue);
        Debug.Log($"[Run] seed {runSeed}");

        BuildScene();
        BuildUI();
    }

    // ── Scene ─────────────────────────────────────────────────────────────────

    void BuildScene()
    {
        cam = Camera.main;
        if (cam == null)
        {
            var camGO = new GameObject("Main Camera");
            camGO.tag = "MainCamera";
            cam = camGO.AddComponent<Camera>();
            camGO.AddComponent<AudioListener>();
        }
        cam.backgroundColor = new Color(0.067f, 0.067f, 0.067f);
        cam.clearFlags      = CameraClearFlags.SolidColor;
        cam.farClipPlane    = 500f;

        var existingLight = FindAnyObjectByType<Light>();
        if (existingLight == null)
        {
            var ambientGO = new GameObject("Ambient Light");
            var ambient   = ambientGO.AddComponent<Light>();
            ambient.type      = LightType.Directional;
            ambient.intensity = 0.6f;
        }

        var sunGO = new GameObject("Sun");
        var sun   = sunGO.AddComponent<Light>();
        sun.type      = LightType.Directional;
        sun.intensity = 0.8f;
        sun.color     = Color.white;
        sunGO.transform.rotation = Quaternion.Euler(45f, 45f, 0f);
        sun.shadows   = LightShadows.Soft;

        // The ground is a seeded procedural island (§2.7), not a plane. The old
        // plane survives only as the fallback if generation fails, so a terrain
        // problem costs a flat world rather than a world with no floor.
        var biomeVisuals = GameConfig.VisualsForBiome("prairies", "Prairies");
        terrain = Morphivore.World.BiomeTerrain.Build(
            runSeed,
            Morphivore.World.BiomeTerrain.TerrainProfile.Prairies(biomeVisuals.groundColor),
            // Props are placed, not walked, so they can only be positioned once
            // the mesh exists. Creatures need no callback — they sample the ground
            // every frame and settle onto it as soon as there is one.
            ScatterProps);

        // The player hatches as the blank: white, rank 1, no family (§2.4).
        var playerGO = new GameObject("Player");
        playerGO.tag = "Player";
        player = playerGO.AddComponent<PlayerController>();
        player.OnNotification      = ShowNotification;
        player.OnLockTargetChanged = UpdateLockReticle;
        playerGO.transform.position = new Vector3(0f, 1f, 0f);

        var ecoGO = new GameObject("Ecosystem");
        ecosystem                = ecoGO.AddComponent<EcosystemManager>();
        ecosystem.player         = player;
        ecosystem.OnBiomeChanged = ApplyBiome;
        ecosystem.OnBossSpawned  = name => ShowNotification(string.IsNullOrEmpty(name)
            ? "!! APEX PREDATOR DETECTED !!"
            : $"!! {name.ToUpper()} !!");
        ecosystem.OnMateSpawned  = () => ShowNotification("!! MATE DETECTED !!");
    }

    // ── UI — charge meter only on Canvas; everything else via IMGUI ───────────

    void BuildUI()
    {
        var canvasGO = new GameObject("Canvas");
        var canvas   = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;
        var scaler = canvasGO.AddComponent<CanvasScaler>();
        scaler.uiScaleMode        = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);
        scaler.screenMatchMode    = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
        scaler.matchWidthOrHeight = 0.5f;
        canvasGO.AddComponent<GraphicRaycaster>();

        EnsureDesktopPointer();

        // Canvas buttons need an EventSystem to receive clicks. A UI input
        // module created at runtime has no input actions assigned, so we must
        // wire up the default set or pointer clicks are never detected.
        var esGO = new GameObject("EventSystem");
        esGO.AddComponent<EventSystem>();
        var uiModule = esGO.AddComponent<InputSystemUIInputModule>();
        uiModule.AssignDefaultActions();

        CreateLockReticle();
        CreateThreatHalo();
        CreateHudBars(canvasGO);
        CreateMenuPanels(canvasGO);
    }

    // This is a desktop game (WASD + mouse). If the Input System has the Mouse
    // or Pen device disabled — e.g. a lingering "Simulate Touch Input From Mouse
    // or Pen" toggle in the editor — Canvas UI clicks route to a dead phantom
    // Touchscreen and no button responds (IMGUI didn't hit this because it reads
    // OS events directly). Make sure the mouse is the active pointer.
    static void EnsureDesktopPointer()
    {
        foreach (var device in InputSystem.devices)
        {
            if ((device is Mouse || device is Pen) && !device.enabled)
                InputSystem.EnableDevice(device);
            else if (device is Touchscreen && device.enabled && Mouse.current != null)
                InputSystem.DisableDevice(device);
        }
    }

    // ── Per-frame ─────────────────────────────────────────────────────────────

    void Update()
    {
        if (player == null) return;

        if (_notifTimer > 0f) _notifTimer -= Time.deltaTime;

        if (!gameStarted) return;

        UpdateHudBars();

        if (player.isDead && !deathHandled)
        {
            deathHandled = true;
            StartCoroutine(ShowDeathScreen());
        }
    }

    void UpdateHudBars()
    {
        if (healthFillImage != null)
            healthFillImage.fillAmount = player.maxHealth > 0
                ? Mathf.Clamp01(player.health / player.maxHealth) : 1f;

        // Who you currently are: rank is your body, the family + intensity are
        // what your limbs are holding, and the name is the form they resolve to.
        if (formText != null)
            formText.text = string.IsNullOrEmpty(player.family)
                ? $"RANK {player.rank}   |   {player.FormName.ToUpper()}"
                : $"RANK {player.rank}   |   " +
                  $"{GameConfig.Intensities[player.intensity].name.ToUpper()} {player.family.ToUpper()}   |   " +
                  $"{player.FormName.ToUpper()}";

        // Fade the notification out over its remaining lifetime.
        if (notifLabel != null)
        {
            var c = notifLabel.color;
            c.a = Mathf.Clamp01(_notifTimer);
            notifLabel.color = c;
        }
    }

    // Camera follows in LateUpdate so it always runs after player movement.
    void LateUpdate()
    {
        if (cam == null || player == null) return;

        Vector3 target = player.transform.position + new Vector3(0f, 6f, -10f);
        cam.transform.position = Vector3.Lerp(cam.transform.position, target, 8f * Time.deltaTime);
        cam.transform.LookAt(player.transform.position + Vector3.up);

        // Lock-on reticle hovers above the currently locked target, billboarded.
        if (reticleCanvasGO != null && lockTarget != null)
        {
            float heightAbove = lockTarget.localScale.y * 0.5f + 1.2f;
            reticleCanvasGO.transform.position = lockTarget.position + Vector3.up * heightAbove;
            reticleCanvasGO.transform.rotation = cam.transform.rotation;
        }

        // Threat halo pulses over the player while an enemy has us locked.
        if (haloGO != null)
        {
            bool threatened = player.IsThreatened;
            haloGO.SetActive(threatened);
            if (threatened)
            {
                float h = player.transform.localScale.y * 0.5f + 1.6f;
                haloCanvasGO.transform.position = player.transform.position + Vector3.up * h;
                haloCanvasGO.transform.rotation = cam.transform.rotation;
                float pulse = 1f + Mathf.Sin(Time.time * 10f) * 0.15f;
                haloGO.transform.localScale = Vector3.one * pulse;
            }
        }
    }

    // Solid props, placed on the ground. Called once the terrain mesh exists.
    // Imported art first; the old primitives remain as the fallback so a missing
    // or renamed asset costs a plainer world, never an empty one.
    void ScatterProps()
    {
        var propRoot = new GameObject("Props").transform;
        if (Morphivore.World.PropScatter.Scatter("prairies", propRoot)) return;

        ScatterPrimitiveProps(propRoot);
    }

    void ScatterPrimitiveProps(Transform parent)
    {
        float r = Morphivore.World.BiomeTerrain.Radius * 0.85f;
        Color[] palette = { GameConfig.Colors.Red, GameConfig.Colors.Blue, GameConfig.Colors.Grey,
                            GameConfig.Colors.Yellow, GameConfig.Colors.White, GameConfig.Colors.Purple };

        for (int i = 0; i < 30; i++)
        {
            var crystal = GameObject.CreatePrimitive(PrimitiveType.Cube);
            crystal.transform.SetParent(parent, true);
            float cx = Random.Range(-r, r);
            float cz = Random.Range(-r, r);
            float h  = Random.Range(2f, 5f);

            crystal.transform.localScale = new Vector3(1f, h, 1f);
            crystal.transform.position   = new Vector3(
                cx, Morphivore.World.BiomeTerrain.HeightAt(cx, cz) + h * 0.35f, cz);
            crystal.transform.rotation   = Quaternion.Euler(0f, Random.Range(0f, 360f), 0f);

            var mat = crystal.GetComponent<Renderer>().material;
            mat.color = palette[Random.Range(0, palette.Length)];
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", mat.color * 0.2f);
            // Keep the collider and mark it solid so the player can't pass through.
            crystal.AddComponent<Obstacle>();
        }
    }

    void OnStartClicked()
    {
        gameStarted           = true;
        deathHandled          = false;
        player.gameStarted    = true;
        ecosystem.gameStarted = true;
        ecosystem.Init();
        if (menuPanelGO != null) menuPanelGO.SetActive(false);
        if (hudBarsGO != null) hudBarsGO.SetActive(true);
        UpdateHudBars();
    }

    IEnumerator ShowDeathScreen()
    {
        yield return new WaitForSeconds(2f);
        if (deathScoreText != null)
            deathScoreText.text = $"Lineage terminated.\nScore: {player.score}";
        if (hudBarsGO != null) hudBarsGO.SetActive(false);
        if (deathPanelGO != null) deathPanelGO.SetActive(true);
    }

    // ── Biome ─────────────────────────────────────────────────────────────────

    void ApplyBiome(GameConfig.BiomeData biome)
    {
        if (cam)    cam.backgroundColor = biome.groundColor;
        if (terrain) terrain.SetGroundColor(biome.groundColor);
        RenderSettings.fogColor         = biome.fogColor;
        RenderSettings.fog              = true;
        RenderSettings.fogStartDistance = 40f;
        RenderSettings.fogEndDistance   = 150f;
        ShowNotification($"ENTERING {biome.name}");
    }

    // ── Notification ──────────────────────────────────────────────────────────

    void ShowNotification(string text)
    {
        _notifTimer = 2f;
        if (notifLabel != null) notifLabel.text = text;
    }

    // ── Lock-on reticle (world-space red ring drawn over the locked target) ───

    void CreateLockReticle()
    {
        const int S = 128;
        reticleTex = new Texture2D(S, S, TextureFormat.RGBA32, false);
        reticleTex.filterMode = FilterMode.Bilinear;
        var pixels = new Color[S * S];
        float half  = S * 0.5f;
        float outer = half - 0.5f;
        float inner = half * 0.64f; // ring thickness (annulus)
        for (int y = 0; y < S; y++)
            for (int x = 0; x < S; x++)
            {
                float d = Mathf.Sqrt((x - half) * (x - half) + (y - half) * (y - half));
                bool onRing = d <= outer && d >= inner;
                pixels[y * S + x] = new Color(1f, 1f, 1f, onRing ? 1f : 0f);
            }
        reticleTex.SetPixels(pixels);
        reticleTex.Apply();
        var ringSprite = Sprite.Create(reticleTex, new Rect(0, 0, S, S), new Vector2(0.5f, 0.5f), S);

        reticleCanvasGO = new GameObject("LockReticleWorld");
        var worldCanvas = reticleCanvasGO.AddComponent<Canvas>();
        worldCanvas.renderMode  = RenderMode.WorldSpace;
        worldCanvas.worldCamera = cam;
        // World-space canvas units are pixels; scale down so 90px reads ~1.3 units.
        reticleCanvasGO.transform.localScale = Vector3.one * 0.014f;

        reticleGO = new GameObject("LockReticle");
        reticleGO.transform.SetParent(reticleCanvasGO.transform, false);
        var img   = reticleGO.AddComponent<Image>();
        img.sprite = ringSprite;
        img.color  = new Color(1f, 0.25f, 0.28f, 0.95f); // red
        var rect  = reticleGO.GetComponent<RectTransform>();
        rect.anchorMin        = new Vector2(0.5f, 0.5f);
        rect.anchorMax        = new Vector2(0.5f, 0.5f);
        rect.pivot            = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta        = new Vector2(90f, 90f);

        reticleGO.SetActive(false);
    }

    // Called by PlayerController: show the ring over `target`, or hide it (null).
    void UpdateLockReticle(Transform target)
    {
        lockTarget = target;
        if (reticleGO != null) reticleGO.SetActive(target != null);
    }

    // ── Threat halo (world-space orange ring over the player when targeted) ───

    void CreateThreatHalo()
    {
        const int S = 128;
        var tex = new Texture2D(S, S, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        var pixels = new Color[S * S];
        float half  = S * 0.5f;
        float outer = half - 0.5f;
        float inner = half * 0.72f; // thinner ring reads as a halo
        for (int y = 0; y < S; y++)
            for (int x = 0; x < S; x++)
            {
                float d = Mathf.Sqrt((x - half) * (x - half) + (y - half) * (y - half));
                bool onRing = d <= outer && d >= inner;
                pixels[y * S + x] = new Color(1f, 1f, 1f, onRing ? 1f : 0f);
            }
        tex.SetPixels(pixels);
        tex.Apply();
        var ringSprite = Sprite.Create(tex, new Rect(0, 0, S, S), new Vector2(0.5f, 0.5f), S);

        haloCanvasGO = new GameObject("ThreatHaloWorld");
        var wc = haloCanvasGO.AddComponent<Canvas>();
        wc.renderMode  = RenderMode.WorldSpace;
        wc.worldCamera = cam;
        haloCanvasGO.transform.localScale = Vector3.one * 0.02f;

        haloGO = new GameObject("ThreatHalo");
        haloGO.transform.SetParent(haloCanvasGO.transform, false);
        var img = haloGO.AddComponent<Image>();
        img.sprite = ringSprite;
        img.color  = new Color(1f, 0.55f, 0.1f, 0.9f); // warning orange
        var rect = haloGO.GetComponent<RectTransform>();
        rect.anchorMin        = new Vector2(0.5f, 0.5f);
        rect.anchorMax        = new Vector2(0.5f, 0.5f);
        rect.pivot            = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = Vector2.zero;
        rect.sizeDelta        = new Vector2(120f, 120f);

        haloGO.SetActive(false);
    }

    // ── HUD bars (Canvas horizontal fill, top-right) ──────────────────────────

    static Sprite _hudBarSprite;

    static Sprite GetHudBarSprite()
    {
        if (_hudBarSprite != null) return _hudBarSprite;
        // Filled-type Images require a real sprite — without one Unity silently
        // ignores fillAmount and just renders the full rect.
        var tex = Texture2D.whiteTexture;
        _hudBarSprite = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f));
        return _hudBarSprite;
    }

    void CreateHudBars(GameObject parent)
    {
        hudBarsGO = new GameObject("HudBars", typeof(RectTransform));
        hudBarsGO.transform.SetParent(parent.transform, false);
        var containerRect = hudBarsGO.GetComponent<RectTransform>();
        containerRect.anchorMin = Vector2.zero;
        containerRect.anchorMax = Vector2.one;
        containerRect.offsetMin = Vector2.zero;
        containerRect.offsetMax = Vector2.zero;

        // One meter only: Health (§2.3). Progress is your form, and your form is
        // on your body — the limbs and the slot that pulses (§2.4a).
        healthFillImage = CreateStatBar(hudBarsGO, "HealthBar", "HEALTH", 100f, new Color(1f, 0.278f, 0.341f, 1f));

        // Form readout — top-left corner
        formText = CreateUIText(hudBarsGO.transform, "FormLabel", "", 30, FontStyle.Bold,
                                new Color(1f, 1f, 1f, 0.85f), Vector2.zero, new Vector2(560f, 44f));
        var ftRect = formText.GetComponent<RectTransform>();
        ftRect.anchorMin        = new Vector2(0f, 1f);
        ftRect.anchorMax        = new Vector2(0f, 1f);
        ftRect.pivot            = new Vector2(0f, 1f);
        ftRect.anchoredPosition = new Vector2(30f, -30f);
        formText.alignment          = TextAnchor.MiddleLeft;
        // Don't wrap: the label sits top-left with empty space to its right, and a
        // long line (a long authored form name) would otherwise wrap and get
        // clipped, making the form appear to vanish.
        formText.horizontalOverflow = HorizontalWrapMode.Overflow;
        formText.verticalOverflow   = VerticalWrapMode.Overflow;

        // Center-screen notification (mutation / boss / biome messages)
        notifLabel = CreateUIText(hudBarsGO.transform, "Notification", "", 44, FontStyle.Bold,
                                  AccentGreen, new Vector2(0f, 200f), new Vector2(1200f, 90f));
        var nc = notifLabel.color; nc.a = 0f; notifLabel.color = nc;

        hudBarsGO.SetActive(false);
    }

    // Bars are anchored to the top-right corner of the screen, stacked downward.
    Image CreateStatBar(GameObject parent, string name, string label, float yOffset, Color fillColor)
    {
        const float barW = 520f;
        const float barH = 40f;
        const float rightMargin = 60f;
        const float labelH = 40f;

        var labelGO = new GameObject(name + "_Label", typeof(RectTransform));
        labelGO.transform.SetParent(parent.transform, false);
        var labelText = labelGO.AddComponent<Text>();
        labelText.text      = label;
        labelText.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        labelText.fontSize  = 32;
        labelText.fontStyle = FontStyle.Bold;
        labelText.alignment = TextAnchor.MiddleRight;
        labelText.color     = new Color(1f, 1f, 1f, 0.85f);
        var labelRect = labelGO.GetComponent<RectTransform>();
        labelRect.anchorMin        = new Vector2(1f, 1f);
        labelRect.anchorMax        = new Vector2(1f, 1f);
        labelRect.pivot            = new Vector2(1f, 1f);
        labelRect.anchoredPosition = new Vector2(-rightMargin, -(yOffset - labelH - 4f));
        labelRect.sizeDelta        = new Vector2(barW, labelH);

        var bg = new GameObject(name + "_BG", typeof(RectTransform));
        bg.transform.SetParent(parent.transform, false);
        var bgImg  = bg.AddComponent<Image>();
        bgImg.color = new Color(0.15f, 0.15f, 0.15f, 0.85f);
        var bgRect = bg.GetComponent<RectTransform>();
        bgRect.anchorMin        = new Vector2(1f, 1f);
        bgRect.anchorMax        = new Vector2(1f, 1f);
        bgRect.pivot            = new Vector2(1f, 1f);
        bgRect.anchoredPosition = new Vector2(-rightMargin, -yOffset);
        bgRect.sizeDelta        = new Vector2(barW, barH);

        var fillGO  = new GameObject(name + "_Fill", typeof(RectTransform));
        fillGO.transform.SetParent(bg.transform, false);
        var fillImg          = fillGO.AddComponent<Image>();
        fillImg.sprite       = GetHudBarSprite();
        fillImg.color        = fillColor;
        fillImg.type         = Image.Type.Filled;
        fillImg.fillMethod   = Image.FillMethod.Horizontal;
        fillImg.fillOrigin   = (int)Image.OriginHorizontal.Left;
        fillImg.fillAmount   = 1f;
        var fillRect         = fillGO.GetComponent<RectTransform>();
        fillRect.anchorMin   = Vector2.zero;
        fillRect.anchorMax   = Vector2.one;
        fillRect.offsetMin   = Vector2.zero;
        fillRect.offsetMax   = Vector2.zero;

        return fillImg;
    }

    // ── Menu / death screens (Canvas) ─────────────────────────────────────────

    static readonly Color AccentGreen = new Color(0.18f, 0.84f, 0.45f);

    void CreateMenuPanels(GameObject parent)
    {
        // Main menu — visible at launch
        menuPanelGO = CreateOverlayPanel(parent, "MenuPanel");
        CreateUIText(menuPanelGO.transform, "Title", "CUBIC EVOLUTION", 84, FontStyle.Bold,
                     AccentGreen, new Vector2(0f, 170f), new Vector2(1400f, 110f));
        CreateUIText(menuPanelGO.transform, "Tagline", "Evolve. Adapt. Dominate.", 30, FontStyle.Normal,
                     new Color(0.8f, 0.8f, 0.8f), new Vector2(0f, 90f), new Vector2(800f, 50f));
        CreateUIButton(menuPanelGO.transform, "StartButton", "INITIALIZE",
                       new Vector2(0f, -40f), new Vector2(340f, 84f), OnStartClicked);

        // Death screen — hidden until the player dies
        deathPanelGO = CreateOverlayPanel(parent, "DeathPanel");
        CreateUIText(deathPanelGO.transform, "Title", "EXTINCT", 84, FontStyle.Bold,
                     new Color(1f, 0.28f, 0.34f), new Vector2(0f, 150f), new Vector2(800f, 110f));
        deathScoreText = CreateUIText(deathPanelGO.transform, "Score", "", 30, FontStyle.Normal,
                                      new Color(0.8f, 0.8f, 0.8f), new Vector2(0f, 40f), new Vector2(800f, 90f));
        CreateUIButton(deathPanelGO.transform, "RestartButton", "NEW EVOLUTION",
                       new Vector2(0f, -90f), new Vector2(380f, 84f),
                       () => SceneManager.LoadScene(SceneManager.GetActiveScene().name));
        deathPanelGO.SetActive(false);
    }

    GameObject CreateOverlayPanel(GameObject parent, string name)
    {
        var panel = new GameObject(name, typeof(RectTransform));
        panel.transform.SetParent(parent.transform, false);
        var img   = panel.AddComponent<Image>();
        img.color = new Color(0.02f, 0.02f, 0.02f, 0.95f);
        var rect = panel.GetComponent<RectTransform>();
        rect.anchorMin = Vector2.zero;
        rect.anchorMax = Vector2.one;
        rect.offsetMin = Vector2.zero;
        rect.offsetMax = Vector2.zero;
        return panel;
    }

    Text CreateUIText(Transform parent, string name, string content, int fontSize, FontStyle style,
                      Color color, Vector2 anchoredPos, Vector2 size)
    {
        var go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        var text = go.AddComponent<Text>();
        text.text      = content;
        text.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        text.fontSize  = fontSize;
        text.fontStyle = style;
        text.alignment = TextAnchor.MiddleCenter;
        text.color     = color;
        var rect = go.GetComponent<RectTransform>();
        rect.anchoredPosition = anchoredPos; // anchors default to center
        rect.sizeDelta        = size;
        return text;
    }

    void CreateUIButton(Transform parent, string name, string label,
                        Vector2 anchoredPos, Vector2 size, UnityEngine.Events.UnityAction onClick)
    {
        var go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        var img   = go.AddComponent<Image>();
        img.sprite = GetHudBarSprite();
        img.color  = new Color(0.10f, 0.28f, 0.17f, 1f);
        var rect = go.GetComponent<RectTransform>();
        rect.anchoredPosition = anchoredPos;
        rect.sizeDelta        = size;

        var btn = go.AddComponent<Button>();
        btn.targetGraphic = img;
        var colors = btn.colors;
        colors.normalColor      = new Color(0.85f, 0.85f, 0.85f, 1f);
        colors.highlightedColor = Color.white; // hover brightens
        colors.pressedColor     = new Color(0.6f, 0.6f, 0.6f, 1f);
        btn.colors = colors;
        btn.onClick.AddListener(onClick);

        CreateUIText(go.transform, "Label", label, 32, FontStyle.Bold, Color.white, Vector2.zero, size);
    }
}
