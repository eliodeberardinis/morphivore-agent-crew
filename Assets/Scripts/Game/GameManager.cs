using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using Morphivore.Content;

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
    Text       objectiveText;   // what the Alpha is waiting for
    Image      alarmFlash;      // full-screen red pulse when the Alpha wakes

    // ── Menu / death screens (Canvas) ─────────────────────────────────────────
    GameObject menuPanelGO;
    GameObject deathPanelGO;
    Text       deathScoreText;
    GameObject victoryPanelGO;
    Text       victoryScoreText;

    // ── Notification (Canvas, fades out) ──────────────────────────────────────
    float _notifTimer = 0f;
    float _notifLife  = 2f;   // how long this notification was given
    float _alarmTimer = 0f;   // red screen pulse, counts down alongside it

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

    void Start() => StartCoroutine(Boot());

    /// <summary>Boot is a coroutine because WebGL cannot read StreamingAssets
    /// synchronously — the content has to be fetched over HTTP before anything
    /// that depends on it is built. On desktop the prefetch completes in a frame
    /// or two and the order is otherwise identical.</summary>
    IEnumerator Boot()
    {
        // Fetch the generated world content up front so a missing or malformed
        // file reports itself at boot rather than on the first spawn. Failure is
        // non-fatal — the ecosystem falls back to the prototype tables.
        yield return Morphivore.Content.ContentDatabase.Prefetch();
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
        currentBiomeId   = "prairies";
        terrain = Morphivore.World.BiomeTerrain.Build(
            Morphivore.World.BiomeTerrain.SeedForBiome(runSeed, 0),
            Morphivore.World.BiomeTerrain.TerrainProfile.For("prairies", biomeVisuals.groundColor),
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
        ecosystem.OnBossSpawned  = name => ShowNotification(
            string.IsNullOrEmpty(name)
                ? "THE ALPHA HAS WOKEN"
                : $"THE ALPHA HAS WOKEN\n{name.ToUpper()}",
            5f, new Color(1f, 0.30f, 0.26f), alarm: true);
        player.OnAtePrey         = (form, family) => ecosystem.RecordColouredPrey(form, family);
        player.OnAlphaEaten      = OnAlphaEaten;
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

    // How far the camera stays clear of the ground beneath it. Enough that a
    // slope's near face never crosses the near clip plane, which is its own way of
    // punching a hole in the world.
    const float CameraGroundClearance = 3f;

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

        // What the Alpha is waiting for. Two counters, both fed by eating meat:
        // how many forms you have worn here, and how much of it you have eaten.
        // Before this line existed the Alpha's arrival was unexplained — you were
        // working toward something the game never named (§2.5).
        if (objectiveText != null && ecosystem != null)
        {
            if (ecosystem.AlphaDefeated)
            {
                objectiveText.text  = "ALPHA DOWN  —  THIS BIOME IS YOURS";
                objectiveText.color = new Color(0.18f, 0.84f, 0.45f, 0.95f);
            }
            else if (ecosystem.AlphaAwake)
            {
                objectiveText.text  = "THE ALPHA IS AWAKE  —  HUNT IT";
                objectiveText.color = new Color(1f, 0.35f, 0.30f, 0.95f);
            }
            else
            {
                objectiveText.text  = $"WAKE THE ALPHA:  FORMS {ecosystem.FormsSeen}/{ecosystem.FormGate}" +
                                      $"   ·   PREY EATEN {ecosystem.PreyEaten}/{ecosystem.PreyGate}";
                objectiveText.color = new Color(1f, 1f, 1f, 0.62f);
            }
        }

        // Fade the notification out over its remaining lifetime.
        if (notifLabel != null)
        {
            var c = notifLabel.color;
            c.a = Mathf.Clamp01(_notifTimer / Mathf.Min(_notifLife, 1f));
            notifLabel.color = c;
        }

        // The alarm: a red wash over the whole screen, pulsing, decaying out.
        if (alarmFlash != null)
        {
            if (_alarmTimer > 0f)
            {
                _alarmTimer -= Time.deltaTime;
                float decay = Mathf.Clamp01(_alarmTimer / 3f);
                float pulse = 0.5f + 0.5f * Mathf.Sin(Time.time * 12f);
                alarmFlash.enabled = true;
                alarmFlash.color   = new Color(0.85f, 0.05f, 0.08f, 0.34f * decay * pulse);
            }
            else if (alarmFlash.enabled) alarmFlash.enabled = false;
        }
    }

    // Camera follows in LateUpdate so it always runs after player movement.
    void LateUpdate()
    {
        if (cam == null || player == null) return;

        Vector3 target = player.transform.position + new Vector3(0f, 6f, -10f);
        cam.transform.position = Vector3.Lerp(cam.transform.position, target, 8f * Time.deltaTime);

        // Keep the camera above the ground it is standing over.
        //
        // The follow offset is fixed and sits 10 units behind the player on -z, so
        // any ground rising behind them puts the camera *inside* the hill. From in
        // there you are behind the terrain's front faces, and backface culling
        // draws nothing: hills read as hollow shells and the ground appears to stop
        // having a texture. It looks like missing terrain, and it isn't — it is the
        // camera looking at the world from underneath its own skin. Always on the
        // -z side, because that is the only side the camera is ever on.
        //
        // The world was flat when this follow was written; it has been an island
        // with 11 units of relief since C1b, and more of it now reaches the shore.
        Vector3 eye    = cam.transform.position;
        float   ground = Morphivore.World.BiomeTerrain.HeightAt(eye.x, eye.z);
        if (eye.y < ground + CameraGroundClearance)
        {
            eye.y = ground + CameraGroundClearance;
            cam.transform.position = eye;
        }

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
    // The live prop root, kept so a biome change can clear the last one's trees
    // rather than stacking a marsh on top of a meadow.
    GameObject propRootGO;
    string     currentBiomeId;

    void ScatterProps()
    {
        if (propRootGO != null) Destroy(propRootGO);
        propRootGO = new GameObject("Props");

        var propRoot = propRootGO.transform;
        string biomeId = string.IsNullOrEmpty(currentBiomeId) ? "prairies" : currentBiomeId;

        if (!Morphivore.World.PropScatter.Scatter(biomeId, propRoot))
            ScatterPrimitiveProps(propRoot);

        // The ground moved under everything. Creatures re-seat themselves (they
        // read GroundY every frame), but the player is placed, not walked, so a
        // new island could leave them buried in a hill or hanging over a hollow.
        ReseatPlayer();
    }

    void ReseatPlayer()
    {
        if (player == null) return;

        Vector3 p = player.transform.position;
        float limit = Morphivore.World.BiomeTerrain.Radius;
        p.x = Mathf.Clamp(p.x, -limit, limit);
        p.z = Mathf.Clamp(p.z, -limit, limit);
        p.y = Morphivore.World.BiomeTerrain.HeightAt(p.x, p.z) + 1f;
        player.transform.position = p;
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

    // ── The Alpha's payout ────────────────────────────────────────────────────

    /// <summary>Beating the biome's champion. The emblem is a trophy, not a power
    /// (§2.5) — what it does is open the way on, and the last one in the world
    /// opens nothing, because there is nowhere further to go.</summary>
    void OnAlphaEaten(EmblemDef emblem, string alphaName)
    {
        string trophy = emblem != null ? emblem.name : "the Alpha's emblem";
        bool   last   = emblem != null && string.IsNullOrEmpty(emblem.opens_biome);

        if (last)
        {
            StartCoroutine(ShowVictoryScreen());
            return;
        }

        ShowNotification($"{trophy.ToUpper()} TAKEN\nYOU GROW A LIMB — RANK {player.rank}",
                         5f, AccentGreen);
    }

    IEnumerator ShowVictoryScreen()
    {
        ShowNotification("THE LAST ALPHA FALLS", 3f, AccentGreen);
        yield return new WaitForSeconds(3f);

        if (victoryScoreText != null)
            victoryScoreText.text =
                $"Five territories. Five emblems. Six limbs.\nScore: {player.score}";
        if (hudBarsGO != null)    hudBarsGO.SetActive(false);
        if (victoryPanelGO != null) victoryPanelGO.SetActive(true);
    }

    // ── Biome ─────────────────────────────────────────────────────────────────

    void ApplyBiome(GameConfig.BiomeData biome)
    {
        if (cam) cam.backgroundColor = biome.groundColor;

        // A new territory is a new island, not the same one repainted. Entering a
        // biome used to change only the palette and the spawn table, so all five
        // read as one map in five colours — the thing the run is *about* (pushing
        // through five territories, §2.7) was the least visible part of it.
        if (terrain != null && !string.IsNullOrEmpty(biome.id) && biome.id != currentBiomeId)
        {
            currentBiomeId = biome.id;
            terrain.Regenerate(
                Morphivore.World.BiomeTerrain.SeedForBiome(runSeed, biome.index),
                Morphivore.World.BiomeTerrain.TerrainProfile.For(biome.id, biome.groundColor),
                ScatterProps);
        }
        else if (terrain != null)
        {
            terrain.SetGroundColor(biome.groundColor);
        }
        RenderSettings.fogColor = biome.fogColor;
        RenderSettings.fog      = true;

        // fogStartDistance / fogEndDistance apply to LINEAR fog only. Without
        // this line Unity stayed on its default exponential-squared fog at
        // density 0.01, quietly ignoring both numbers below: ground 100 units out
        // came through about 63% fog colour and the far corner ~86%, so relief and
        // texture dissolved into a flat wash partway across the island — the
        // "textures cut off" edge, which moved with the camera because fog is
        // measured from the camera, not the world.
        RenderSettings.fogMode = FogMode.Linear;

        // Sized for THIS world: the island is 100 units across and the camera sits
        // 10 units behind the player, so the far corner is ~140 away. Fog starting
        // at 40 fogged more of the world than it left clear. Start it past the
        // island's own width so it only softens the horizon.
        RenderSettings.fogStartDistance = 110f;
        RenderSettings.fogEndDistance   = 260f;

        ShowNotification($"ENTERING {biome.name}");
    }

    // ── Notification ──────────────────────────────────────────────────────────

    void ShowNotification(string text) => ShowNotification(text, 2f, AccentGreen);

    /// <summary>A notification that can be louder than the default: longer on
    /// screen, and in its own colour. The Alpha's arrival uses both, because a
    /// two-second green line was being missed entirely — the first the player
    /// knew of the Alpha was being hit by it.</summary>
    void ShowNotification(string text, float seconds, Color color, bool alarm = false)
    {
        _notifTimer = seconds;
        _notifLife  = Mathf.Max(0.01f, seconds);
        if (notifLabel != null)
        {
            notifLabel.text     = text;
            notifLabel.color    = color;
            notifLabel.fontSize = alarm ? 62 : 44;
        }
        if (alarm) _alarmTimer = seconds;
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

        // Objective readout — directly under the form line, same corner.
        objectiveText = CreateUIText(hudBarsGO.transform, "Objective", "", 24, FontStyle.Bold,
                                     new Color(1f, 1f, 1f, 0.62f), Vector2.zero, new Vector2(700f, 34f));
        var obRect = objectiveText.GetComponent<RectTransform>();
        obRect.anchorMin        = new Vector2(0f, 1f);
        obRect.anchorMax        = new Vector2(0f, 1f);
        obRect.pivot            = new Vector2(0f, 1f);
        obRect.anchoredPosition = new Vector2(30f, -74f);
        objectiveText.alignment          = TextAnchor.MiddleLeft;
        objectiveText.horizontalOverflow = HorizontalWrapMode.Overflow;

        // Controls, permanently on screen. The game is a browser build with no
        // manual and no tutorial: a stranger has to be able to play it inside two
        // minutes, and nothing else in the world tells them which button eats.
        var controls = CreateUIText(hudBarsGO.transform, "Controls",
            "WASD / ARROWS  move      LEFT-CLICK  pounce      HOLD RIGHT-CLICK  lock on      SPACE  dash      Q  spit out oldest colour\n" +
            "Pounce prey until it falls, then pounce again to eat it — its colour becomes yours. White grazers heal you.",
            22, FontStyle.Normal, new Color(1f, 1f, 1f, 0.55f), Vector2.zero, new Vector2(1500f, 62f));
        var cRect = controls.GetComponent<RectTransform>();
        cRect.anchorMin        = new Vector2(0f, 0f);
        cRect.anchorMax        = new Vector2(0f, 0f);
        cRect.pivot            = new Vector2(0f, 0f);
        cRect.anchoredPosition = new Vector2(30f, 24f);
        controls.alignment          = TextAnchor.LowerLeft;
        controls.horizontalOverflow = HorizontalWrapMode.Overflow;

        // Full-screen red wash for the Alpha's arrival. Behind the text, in front
        // of nothing it needs to click through, so raycasts pass straight past it.
        var flashGO = new GameObject("AlarmFlash", typeof(RectTransform));
        flashGO.transform.SetParent(hudBarsGO.transform, false);
        alarmFlash = flashGO.AddComponent<Image>();
        alarmFlash.color         = new Color(0.85f, 0.05f, 0.08f, 0f);
        alarmFlash.raycastTarget = false;
        alarmFlash.enabled       = false;
        var flRect = flashGO.GetComponent<RectTransform>();
        flRect.anchorMin = Vector2.zero;
        flRect.anchorMax = Vector2.one;
        flRect.offsetMin = Vector2.zero;
        flRect.offsetMax = Vector2.zero;

        // Center-screen notification (mutation / boss / biome messages). Created
        // last so it draws over the alarm wash rather than under it.
        notifLabel = CreateUIText(hudBarsGO.transform, "Notification", "", 44, FontStyle.Bold,
                                  AccentGreen, new Vector2(0f, 200f), new Vector2(1400f, 110f));
        var nc = notifLabel.color; nc.a = 0f; notifLabel.color = nc;
        notifLabel.horizontalOverflow = HorizontalWrapMode.Overflow;

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

        // The whole game, on the title screen. This is a browser build: whoever
        // opens the link gets no manual, and the controls are not guessable —
        // "pounce a downed creature to eat it" is a rule, not an affordance.
        CreateUIText(menuPanelGO.transform, "HowTo",
            "Eat to become. Every creature you swallow puts its colour in a limb,\n" +
            "and the colours you carry decide what you are.\n\n" +
            "WASD / ARROWS  move          LEFT-CLICK  pounce          HOLD RIGHT-CLICK  lock on\n" +
            "SPACE  dash          Q  spit out your oldest colour\n\n" +
            "Pounce prey until it falls, then pounce the fallen body to eat it.\n" +
            "White grazers carry no colour — they are food, and they heal you.\n" +
            "Eat enough of a biome, in enough different forms, and its Alpha wakes up.",
            24, FontStyle.Normal, new Color(0.72f, 0.72f, 0.72f),
            new Vector2(0f, -260f), new Vector2(1200f, 300f));

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

        // Victory — the run has an end now. Five Alphas, five emblems, six limbs.
        victoryPanelGO = CreateOverlayPanel(parent, "VictoryPanel");
        CreateUIText(victoryPanelGO.transform, "Title", "CONQUEST", 84, FontStyle.Bold,
                     AccentGreen, new Vector2(0f, 150f), new Vector2(900f, 110f));
        victoryScoreText = CreateUIText(victoryPanelGO.transform, "Score", "", 30, FontStyle.Normal,
                                        new Color(0.8f, 0.8f, 0.8f), new Vector2(0f, 40f), new Vector2(900f, 90f));
        CreateUIButton(victoryPanelGO.transform, "AgainButton", "NEW BLOODLINE",
                       new Vector2(0f, -90f), new Vector2(380f, 84f),
                       () => SceneManager.LoadScene(SceneManager.GetActiveScene().name));
        victoryPanelGO.SetActive(false);
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
