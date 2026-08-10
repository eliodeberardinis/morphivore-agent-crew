using System.Collections;
using UnityEngine;

public class Creature : MonoBehaviour
{
    // ── Identity (§2.4) ───────────────────────────────────────────────────────
    // A creature is one of five families at an intensity, on a body of `rank`
    // limbs (1–6). No family = white, the empty state: a newborn, a grazer, a
    // bare limb. Rank is morphology and intensity is meat — they are orthogonal,
    // so a 2-limb Rage beast and a 5-limb Pale one are both legal animals.
    public string family    = null;
    public int    intensity = GameConfig.Pale;
    public int    rank      = 1;
    public bool   isBoss    = false;

    // Set from creatures.json when the creature comes from the content tables:
    // the authored name, and the authored base_hex, which overrides the palette
    // colour the family alone would pick. The family is still what the player
    // inherits by eating this creature.
    public string displayName     = null;
    public bool   hasBodyColor    = false;
    public bool   hasContentStats = false;
    public Color  bodyColor;

    public Color BodyColor => hasBodyColor ? bodyColor : GameConfig.Colors.ForFamily(family);

    // ── Standing on the ground ────────────────────────────────────────────────
    // The world used to be a plane at y=0, so every body simply pinned itself to
    // half its own height. It is terrain now, so the same idea reads the ground
    // underneath instead. Before the mesh exists BiomeTerrain returns 0, which is
    // exactly the old flat-plane answer — so nothing breaks while it generates.

    protected const float GroundFollow = 18f; // how fast a body settles onto a slope

    /// <summary>Y this body should stand at, over the ground beneath `at`.</summary>
    protected float GroundY(Vector3 at) =>
        Morphivore.World.BiomeTerrain.HeightAt(at.x, at.z) + transform.localScale.y * 0.5f;

    /// <summary>Eased toward the ground, so walking a slope doesn't snap.</summary>
    protected float StickY(Vector3 pos) =>
        Mathf.Lerp(pos.y, GroundY(pos), Mathf.Clamp01(GroundFollow * Time.deltaTime));

    public float maxHealth  = 100f;
    public float health;
    public bool  isDead     = false;
    public bool  isDowned   = false; // "dizzy" / vulnerable knockdown state (enemies)

    protected float damageCooldownTimer = 0f;

    protected GameObject body;
    protected GameObject[] limbs = new GameObject[0];

    protected virtual void Awake()
    {
        // Visuals are built by the spawner after setting family/intensity/rank.
        // Only init health here.
        if (isBoss) maxHealth *= GameConfig.Boss.HealthMultiplier;
        health = maxHealth;
    }

    // Call this after setting family, intensity, rank, isBoss (and after
    // ApplyContent, if this creature came from the content tables — authored
    // health wins over the prototype boss multiplier).
    public void Init()
    {
        if (isBoss && !hasContentStats)
        {
            maxHealth = 100f * GameConfig.Boss.HealthMultiplier;
            health    = maxHealth;
        }
        BuildVisuals();
    }

    public void BuildVisuals()
    {
        // Destroy old children except this component's GO root
        foreach (Transform child in transform)
            Destroy(child.gameObject);

        limbs = new GameObject[0];

        var rankData = GameConfig.RankFor(rank);
        Color col = BodyColor;

        // Body cube
        body = GameObject.CreatePrimitive(PrimitiveType.Cube);
        body.transform.SetParent(transform, false);
        SetColor(body, col, isBoss);
        Destroy(body.GetComponent<Collider>());

        // Eyes
        CreateEye(new Vector3(-0.25f, 0.2f, 0.5f));
        CreateEye(new Vector3( 0.25f, 0.2f, 0.5f));

        // One limb per rank — and, on the player, one colour slot per limb.
        int limbCount = Mathf.Clamp(rank, 0, GameConfig.Ranks.Length);
        limbs = new GameObject[limbCount];
        for (int i = 0; i < limbCount; i++)
        {
            float angle  = (float)i / limbCount * Mathf.PI * 2f;
            float radius = 0.6f;
            var limb = CreateLimb(LimbColor(i));
            limb.transform.SetParent(transform, false);
            limb.transform.localPosition = new Vector3(Mathf.Cos(angle) * radius, -0.3f, Mathf.Sin(angle) * radius);
            limbs[i] = limb;
        }

        // Scale
        float finalScale = rankData.scale;
        if (isBoss) finalScale *= GameConfig.Boss.ScaleMultiplier;
        transform.localScale = Vector3.one * finalScale;
        // Re-seat on the ground: the body just changed size, and a rebuild fires
        // on every mutation and every recovery from a knockdown.
        transform.position   = new Vector3(transform.position.x,
                                           GroundY(transform.position),
                                           transform.position.z);
    }

    /// <summary>Colour of limb `index`. Wildlife wears one colour all over; the
    /// player overrides this to show what each limb is holding (§2.4a).</summary>
    protected virtual Color LimbColor(int index) => BodyColor;

    void CreateEye(Vector3 localPos)
    {
        var eye = GameObject.CreatePrimitive(PrimitiveType.Cube);
        eye.transform.SetParent(transform, false);
        eye.transform.localPosition = localPos;
        eye.transform.localScale    = new Vector3(0.2f, 0.2f, 0.1f);
        eye.GetComponent<Renderer>().material.color = Color.black;
        Destroy(eye.GetComponent<Collider>());
    }

    GameObject CreateLimb(Color col)
    {
        // Sphere for the agile families, cube for the heavy ones (Unity has no
        // tetrahedron/octahedron primitive). Shape reads the body's family, not
        // the slot's — the silhouette is what you are, not what you ate last.
        PrimitiveType pType = (family == "Red" || family == "Blue" || family == "Purple")
            ? PrimitiveType.Sphere
            : PrimitiveType.Cube;
        var limb = GameObject.CreatePrimitive(pType);
        limb.transform.localScale = Vector3.one * 0.3f;
        SetColor(limb, col, false);
        Destroy(limb.GetComponent<Collider>());
        return limb;
    }

    void SetColor(GameObject go, Color col, bool emissive)
    {
        var mat = go.GetComponent<Renderer>().material;
        mat.color = col;
        if (emissive)
        {
            mat.EnableKeyword("_EMISSION");
            mat.SetColor("_EmissionColor", col * 0.5f);
        }
    }

    protected virtual void Update()
    {
        if (isDead) return;

        float t = Time.time * 5f;
        if (body) body.transform.localPosition = new Vector3(0f, Mathf.Sin(t) * 0.05f, 0f);
        for (int i = 0; i < limbs.Length; i++)
            if (limbs[i]) limbs[i].transform.localPosition = new Vector3(
                limbs[i].transform.localPosition.x,
                -0.3f + Mathf.Sin(t + i) * 0.1f,
                limbs[i].transform.localPosition.z);

        if (damageCooldownTimer > 0f)
        {
            damageCooldownTimer -= Time.deltaTime;
            if (body)
            {
                float flash = Mathf.Sin(Time.time * 30f) > 0 ? 1f : 0f;
                var mat = body.GetComponent<Renderer>().material;
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", Color.white * flash * 0.5f);
            }
        }
        else if (body && !isBoss)
        {
            var mat = body.GetComponent<Renderer>().material;
            mat.SetColor("_EmissionColor", Color.black);
        }
    }

    public virtual void TakeDamage(float amount)
    {
        if (damageCooldownTimer > 0f || isDead) return;
        health -= amount;
        damageCooldownTimer = GameConfig.DamageCooldown;
        if (health <= 0f) Die();
    }

    protected virtual void Die()
    {
        isDead = true;
        transform.localScale = new Vector3(transform.localScale.x, 0.1f, transform.localScale.z);
        transform.position   = new Vector3(transform.position.x, 0.05f, transform.position.z);
        StartCoroutine(RemoveAfterDelay(2f));
    }

    IEnumerator RemoveAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);
        Destroy(gameObject);
    }
}
