using UnityEngine;
using Morphivore.Content;

public class EnemyAI : Creature
{
    enum State  { Wander, Chase, Flee }
    enum Attack { None, Windup, Pounce }

    // ── Content-driven identity & stats (creatures.json) ──────────────────────
    // Everything here has a prototype default, so an enemy spawned without
    // content still behaves exactly as it did before.
    public string contentId;
    public string role            = "prey";
    public bool   carriesColour   = true;   // grazers carry no colour to give
    public float  healsPlayerPct  = 0f;     // >0: eating heals this share of max HP

    float contactDamage = 8f;
    float lockRange     = -1f;   // <0 → derive from body size, as before
    float pounceSpeed   = -1f;   // <0 → derive from moveSpeed, as before
    bool  alwaysFlees;           // grazers: never fight, whatever the gap
    bool  alwaysHunts;           // elites, minibosses, alphas, the apex

    // The content's `dash` is a speed on the same scale as `speed`; a pounce is a
    // committed lunge, so it travels at a multiple of it.
    const float PounceLungeFactor = 4f;

    /// <summary>Stamp this enemy with one creature from the content tables, for a
    /// specific biome. Call before Init() so the visuals build from it.</summary>
    public void ApplyContent(CreatureDef def, SpawnDef spawn)
    {
        contentId       = def.id;
        role            = def.role;
        displayName     = def.name;
        carriesColour   = def.carries_colour;
        healsPlayerPct  = def.heals_player_pct;

        // Family is the colour its meat carries; the content's tier is that
        // meat's intensity, and its limb count is the body plan (§2.4b). Grazers
        // author neither — they come out white and limbless, which is what they are.
        family    = def.family;
        intensity = ContentDatabase.IntensityIndex(def.tier);
        rank      = Mathf.Clamp(def.limbs > 0 ? def.limbs : def.rank, 0, GameConfig.Ranks.Length);

        bodyColor    = ContentDatabase.HexToColor(def.base_hex, GameConfig.Colors.ForFamily(family));
        hasBodyColor = true;

        alwaysFlees = role == "grazer";
        isGrazer    = role == "grazer";   // built smaller, and wears the heart
        alwaysHunts = role == "elite" || role == "trait_miniboss"
                   || role == "alpha" || role == "apex";

        // Authored numbers land here once, scaled by GameConfig.Ecology, so every
        // consumer below reads a playable value and the JSON stays untouched.
        // Health is deliberately not scaled: a creature that takes a couple of
        // pounces to knock down is the point, and it's not what kills the player.
        var st = spawn.stats;
        if (st != null)
        {
            if (st.health > 0f)
            {
                // The Alpha is the fight the biome is built around; its authored
                // health is on the same scale as the prey it rules over.
                maxHealth = isBoss
                    ? st.health * GameConfig.Boss.ContentHealthMultiplier
                    : st.health;
                health = maxHealth;
            }

            // "You cannot outrun it" (§2.5) is authored data, not a feeling: every
            // Alpha carries can_be_outrun = false, and its speed is already the
            // GDD's formula — the fastest player form at that rank plus 5%
            // (rank 1: 12 baseline x 1.3 Red x 1.05 = 16.38, exactly the file).
            // Passing that through SpeedScale flattened it to 9.83 against a
            // player who moves 11.1-13.8, so the one creature that must catch you
            // was the one thing you could stroll away from. Take it raw.
            //
            // Note the role test. `can_be_outrun` is absent from every prey record
            // and JsonUtility cannot tell absent from false, so reading the flag
            // alone would hand the whole biome unscaled speed. Only the roles that
            // actually author it are allowed to claim it.
            bool pinnedSpeed = !def.can_be_outrun && (role == "alpha" || role == "apex");
            if (st.speed  > 0f) moveSpeed   = pinnedSpeed
                                            ? st.speed
                                            : st.speed * GameConfig.Ecology.SpeedScale;
            if (st.reach  > 0f) lockRange   = st.reach  * GameConfig.Ecology.ReachScale;
            if (st.dash   > 0f) pounceSpeed = st.dash   * GameConfig.Ecology.SpeedScale * PounceLungeFactor;
            contactDamage = st.damage * GameConfig.Ecology.ContactDamageScale;
        }
        // Grazers carry no combat stats — they get a flee speed instead.
        if (spawn.flee_speed > 0f) moveSpeed = spawn.flee_speed * GameConfig.Ecology.SpeedScale;

        hasContentStats = true;
    }

    State state = State.Wander;
    Vector3 targetDir;
    float moveSpeed;
    float changeDirTimer = 0f;

    Transform        playerTransform;
    PlayerController playerCtrl;

    // Knockdown ("dizzy") state — enemies don't die from stomach loss, they get
    // knocked down and become vulnerable, and are only removed when eaten.
    float   downedTimer = 0f;
    const float DownedDuration = 5f;
    Vector3 preDownedScale;

    // Reactions
    float staggerTimer = 0f;                 // brief reel after being hit
    public bool isLockedByPlayer = false;    // set by PlayerController while it locks us
    float   fleePhase;                       // per-enemy zig-zag offset

    // Temperament — rolled per creature so a biome doesn't react as one animal.
    float sightScale   = 1f;   // this creature's share of the sight radius
    bool  standsGround;        // content prey: territorial minority that fights back

    // Attacking the player — mirrors the player's lock → pounce. Weaker meat
    // (<= the player's intensity) must stand still to wind up; stronger meat can
    // keep closing while locked.
    Attack  attackPhase    = Attack.None;
    float   attackCooldown = 0f;
    float   windupTimer    = 0f;
    float   pounceTimer    = 0f;
    Vector3 pounceDir      = Vector3.zero;
    const float WindupTime = 0.6f;
    const float PounceTime = 0.3f;

    Collider myCol;

    // Floating health bar — shown only when the enemy is damaged. Kept as a
    // separate object (not a child) so Creature.BuildVisuals, which clears all
    // children, doesn't destroy it.
    GameObject healthBarGO;
    Transform  healthFillTf;
    Renderer   healthFillRend;
    Camera     barCam;

    protected override void Awake()
    {
        base.Awake();
        moveSpeed = Random.Range(2f, 5f);
        if (isBoss) moveSpeed *= 0.7f;
        targetDir = new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)).normalized;
        fleePhase = Random.Range(0f, 6.28f);

        sightScale   = Random.Range(1f - GameConfig.Ecology.SightJitter,
                                    1f + GameConfig.Ecology.SightJitter);
        standsGround = Random.value < GameConfig.Ecology.TerritorialPreyShare;
    }

    // ── Aggro budget ──────────────────────────────────────────────────────────
    // A content biome holds 18-34 creatures, and unbounded, every one that ever
    // noticed the player joined the same chase and never fell off. Only a few may
    // hunt at once. Counting per frame rather than handing out held slots means
    // nothing has to be released when a creature is eaten, downed or unloaded.
    static int hunters = 0, hunterFrame = -1;

    static void BeginHunterFrame()
    {
        if (hunterFrame == Time.frameCount) return;
        hunterFrame = Time.frameCount;
        hunters     = 0;
    }

    static void CountHunter() { BeginHunterFrame(); hunters++; }

    static bool ClaimHunterSlot()
    {
        BeginHunterFrame();
        if (hunters >= GameConfig.Ecology.MaxHunters) return false;
        hunters++;
        return true;
    }

    /// <summary>Content prey only: bolt unless this one is territorial or carries
    /// stronger meat than the player — and then only if the budget has room. A
    /// creature already mid-attack is always let through so a committed pounce
    /// resolves.</summary>
    bool WantsToHunt(int playerIntensity)
    {
        if (attackPhase != Attack.None) { CountHunter(); return true; }
        if (!standsGround && intensity <= playerIntensity) return false;
        return ClaimHunterSlot();
    }

    // Damage is ignored while dead or already downed; otherwise it staggers us
    // and interrupts any attack in progress.
    public override void TakeDamage(float amount)
    {
        if (isDead || isDowned) return;
        base.TakeDamage(amount); // gates on cooldown, subtracts health, calls Die() at 0
        if (!isDowned)
        {
            staggerTimer   = 0.35f;
            attackPhase    = Attack.None;                     // getting hit cancels our attack
            attackCooldown = Mathf.Max(attackCooldown, 0.5f);
            SetBodyPose(Vector3.one);                         // and drops the gather/stretch
        }
    }

    // Reaching zero stomach knocks the enemy down instead of removing it.
    protected override void Die()
    {
        EnterDowned();
    }

    void EnterDowned()
    {
        isDowned    = true;
        attackPhase = Attack.None;
        downedTimer = DownedDuration;
        SetBodyPose(Vector3.one);   // the squash below is the pose now

        // Squash flat + dim so it clearly reads as "dizzy / vulnerable".
        preDownedScale = transform.localScale;
        transform.localScale = new Vector3(preDownedScale.x * 1.25f,
                                           preDownedScale.y * 0.4f,
                                           preDownedScale.z * 1.25f);
        if (body) body.GetComponent<Renderer>().material.color = BodyColor * 0.5f;
    }

    void Recover()
    {
        isDowned = false;
        transform.localScale = preDownedScale;
        health = maxHealth * 0.5f;
        BuildVisuals(); // restores color + scale cleanly
    }

    // Called by the player when pouncing a downed enemy to eat it. Plays a
    // grab-and-absorb animation: the enemy is pulled into the eater while
    // shrinking and spinning, then removed.
    public void GetEaten(Transform eater)
    {
        if (isDead) return;
        isDead   = true;   // stops AI (Creature.Update early-outs) and re-hits
        isDowned = false;

        if (myCol == null) myCol = GetComponent<Collider>();
        if (myCol != null) myCol.enabled = false; // don't collide while being absorbed

        // Update() early-outs once dead, so the followers cannot hide themselves.
        if (grazerMarkGO != null) grazerMarkGO.SetActive(false);
        if (healthBarGO  != null) healthBarGO.SetActive(false);

        StopAllCoroutines(); // cancel any in-flight bite
        StartCoroutine(EatSequence(eater));
    }

    System.Collections.IEnumerator EatSequence(Transform eater)
    {
        float dur = 0.35f, t = 0f;
        Vector3 startScale = transform.localScale;

        while (t < dur)
        {
            if (eater != null)
            {
                Vector3 mouth = eater.position
                              + eater.forward * (eater.localScale.x * 0.4f)
                              + Vector3.up   * (eater.localScale.y * 0.25f);
                transform.position = Vector3.Lerp(transform.position, mouth, 14f * Time.deltaTime);
            }
            transform.localScale = Vector3.Lerp(startScale, Vector3.one * 0.01f, t / dur);
            transform.Rotate(0f, 900f * Time.deltaTime, 0f);

            t += Time.deltaTime;
            yield return null;
        }
        Destroy(gameObject);
    }

    protected override void Update()
    {
        UpdateHealthBar();
        UpdateGrazerMark();

        if (isDowned) { UpdateDowned(); return; }

        base.Update();
        if (isDead) return;

        // Lazy-find player so spawn order doesn't matter
        if (playerCtrl == null)
        {
            var go = GameObject.FindWithTag("Player");
            if (go == null) return;
            playerTransform = go.transform;
            playerCtrl      = go.GetComponent<PlayerController>();
        }
        if (playerCtrl.isDead) return;

        float dt              = Time.deltaTime;
        float distToPlayer    = Vector3.Distance(transform.position, playerTransform.position);
        int   playerIntensity = playerCtrl.intensity;
        Vector3 toPlayer      = playerTransform.position - transform.position; toPlayer.y = 0f;
        Vector3 toPlayerDir   = toPlayer.sqrMagnitude > 0.001f ? toPlayer.normalized : transform.forward;

        if (attackCooldown > 0f) attackCooldown -= dt;

        // Bigger / darker-meated creatures notice you from farther. Perception is
        // not reach: the authored reach is how far a creature can pounce, and
        // borrowing it as a sight radius had a Pale prey spotting the player from
        // 18.7 units — a third of the map's width, so the biome aggroed as one.
        // Content creatures see about as far as the prototype's did, jittered per
        // creature, with the (already scaled) reach only as a floor so nothing
        // stands inside its own pounce range doing nothing.
        float awareness = hasContentStats
            ? Mathf.Max((GameConfig.Ecology.SightRadius + intensity * 2f + transform.localScale.x) * sightScale,
                        lockRange)
            : 10f + intensity * 2f + transform.localScale.x;

        if (staggerTimer > 0f)
        {
            staggerTimer -= dt; // reel in place after a hit
            FaceDir(toPlayerDir);
        }
        else
        {
            if (distToPlayer < awareness)
            {
                // Role and temperament decide the reaction, not the meat gap alone.
                // Ordinary content prey bolt — the Prairies' Pale prey are authored
                // to sprint for open ground when locked, not to brawl. Predators
                // still count against the budget without being blocked by it, so
                // prey yield the field to whatever is hunting.
                if      (alwaysFlees)      state = State.Flee;
                else if (alwaysHunts)    { CountHunter(); state = State.Chase; }
                else if (hasContentStats) state = WantsToHunt(playerIntensity) ? State.Chase : State.Flee;
                else                      state = (intensity < playerIntensity) ? State.Flee : State.Chase;
            }
            else
                state = State.Wander;

            if (state == State.Chase)
            {
                // Same/stronger meat: hunt and pounce the player like they pounce us.
                UpdateAttack(dt, distToPlayer, toPlayerDir);
            }
            else
            {
                // Breaking off the chase abandons a half-finished attack, so a
                // stale Windup can't buy a hunt slot later (WantsToHunt lets a
                // committed attacker through) when the player wanders back.
                if (hasContentStats) attackPhase = Attack.None;

                float spd = moveSpeed;
                if (state == State.Flee)
                {
                    // Zig-zag panic away from the player.
                    Vector3 away = -toPlayerDir;
                    Vector3 perp = Vector3.Cross(Vector3.up, away);
                    float   wob  = Mathf.Sin(Time.time * 8f + fleePhase) * 0.6f;
                    targetDir = (away + perp * wob).normalized;
                    // The prototype's panic boost was tuned against random wander
                    // speeds. A content creature's authored speed already IS its
                    // flat-out sprint, and prey have to stay runnable-down or the
                    // player can never finish a hunt, so no boost on that path.
                    if (!hasContentStats)
                    {
                        if (isLockedByPlayer)                     spd *= 1.6f;
                        else if (distToPlayer < awareness * 0.5f) spd *= 1.3f;
                    }
                }
                else // Wander
                {
                    // Authored speed is a sprint, not a patrol pace — wandering at
                    // it made the whole biome look like it was already charging.
                    if (hasContentStats) spd *= GameConfig.Ecology.WanderPace;

                    changeDirTimer -= dt;
                    if (changeDirTimer <= 0f)
                    {
                        targetDir      = new Vector3(Random.Range(-1f, 1f), 0f, Random.Range(-1f, 1f)).normalized;
                        changeDirTimer = Random.Range(2f, 5f);
                    }
                }
                transform.position += targetDir * spd * dt;
                FaceDir(targetDir);
            }
        }

        // Solid: don't overlap other enemies / obstacles.
        ResolveEnemyCollisions();

        // Boundary
        float limit = Morphivore.World.BiomeTerrain.Radius;
        Vector3 pos = transform.position;
        if (Mathf.Abs(pos.x) > limit) targetDir.x *= -1f;
        if (Mathf.Abs(pos.z) > limit) targetDir.z *= -1f;
        pos.x = Mathf.Clamp(pos.x, -limit, limit);
        pos.z = Mathf.Clamp(pos.z, -limit, limit);
        pos.y = GroundY(pos);
        transform.position = pos;
    }

    // Lock → windup → pounce cycle against the player.
    void UpdateAttack(float dt, float dist, Vector3 toPlayerDir)
    {
        bool  canMoveWhileLocked = intensity > playerCtrl.intensity; // stronger meat moves while locked
        float startRange = lockRange > 0f ? lockRange : 3.5f + transform.localScale.x;
        float delock     = startRange + 7f;
        float lunge      = pounceSpeed > 0f ? pounceSpeed : moveSpeed * 4.5f;

        switch (attackPhase)
        {
            case Attack.None:
                // Close in; when in range and off cooldown, begin the wind-up.
                transform.position += toPlayerDir * ClosingSpeed * dt;
                FaceDir(toPlayerDir);
                if (dist < startRange && attackCooldown <= 0f)
                {
                    attackPhase = Attack.Windup;
                    windupTimer = WindupTime;
                    SetBodyPose(WindupPose);        // crouch: the tell (§2.2)
                }
                break;

            case Attack.Windup:
                playerCtrl.FlagThreat();          // player sees the "targeted" halo
                FaceDir(toPlayerDir);
                if (canMoveWhileLocked)
                    transform.position += toPlayerDir * ClosingSpeed * 0.6f * dt; // big keeps closing
                // small enemies stand still to wind up

                windupTimer -= dt;
                if (dist > delock)                 EndAttack(0.4f);   // player ran → de-lock
                else if (windupTimer <= 0f)
                {
                    pounceDir   = toPlayerDir;      // commit — moving now dodges it
                    attackPhase = Attack.Pounce;
                    SetBodyPose(LungePose);         // the same stretch the player wears
                    // A pounce should carry roughly as far as the creature can
                    // lock, so a long-reach Sniper actually crosses its own range.
                    pounceTimer = lockRange > 0f
                        ? Mathf.Clamp(startRange / lunge, PounceTime, 0.6f)
                        : PounceTime;
                }
                break;

            case Attack.Pounce:
                playerCtrl.FlagThreat();
                transform.position += pounceDir * lunge * dt;
                FaceDir(pounceDir);
                pounceTimer -= dt;

                float contact = (transform.localScale.x + playerCtrl.transform.localScale.x) * 0.5f + 0.4f;
                if (dist < contact)
                {
                    HitPlayer();
                    // Land it like the player lands one: shove the target off the
                    // impact and recoil off it. A hit used to be a silent
                    // subtraction from the health bar, indistinguishable from
                    // walking into something.
                    playerCtrl.transform.position += pounceDir * 0.6f * transform.localScale.x;
                    StartCoroutine(Recoil(-pounceDir, 0.12f, lunge * 0.5f));
                    EndAttack(1.6f);
                }
                else if (pounceTimer <= 0f)
                {
                    // Whiffed. Hold the overshoot a beat so a dodge visibly leaves
                    // it committed and open — otherwise ducking a pounce looks
                    // exactly like nothing happening, and there is no reason to.
                    StartCoroutine(WhiffRecovery());
                    EndAttack(1.2f);
                }
                break;
        }
    }

    // ── The body during an attack ─────────────────────────────────────────────
    // A creature's whole read is its cube, so the attack has to be visible in the
    // cube: gather, then throw. Without these the symmetric attack existed only in
    // the state machine — the player saw a creature slide into them and lose HP.

    static readonly Vector3 WindupPose = new Vector3(1.15f, 0.80f, 0.90f); // gather
    static readonly Vector3 LungePose  = new Vector3(1.00f, 1.00f, 1.50f); // throw
    const float WhiffHold = 0.18f;

    /// <summary>Closing speed. SpeedScale governs the ambient world; a creature
    /// actually committing to a hunt needs to arrive.</summary>
    float ClosingSpeed => hasContentStats
        ? moveSpeed * GameConfig.Ecology.ChasePace
        : moveSpeed;

    void SetBodyPose(Vector3 pose)
    {
        // BuildVisuals() destroys and rebuilds children, so `body` can be a stale
        // reference across a mutation; never assume it survived.
        if (body != null) body.transform.localScale = pose;
    }

    System.Collections.IEnumerator Recoil(Vector3 dir, float duration, float speed)
    {
        float t = 0f;
        while (t < duration && !isDead && !isDowned)
        {
            transform.position += dir * speed * Time.deltaTime;
            t += Time.deltaTime;
            yield return null;
        }
        SetBodyPose(Vector3.one);
    }

    System.Collections.IEnumerator WhiffRecovery()
    {
        yield return new WaitForSeconds(WhiffHold);
        SetBodyPose(Vector3.one);
    }

    void EndAttack(float cooldown)
    {
        attackPhase    = Attack.None;
        attackCooldown = cooldown;
        // Only reset here if no coroutine is going to do it — a landed or whiffed
        // pounce clears its own pose on a delay so the impact reads.
        if (!isDead && !isDowned && attackCooldown < 1.2f) SetBodyPose(Vector3.one);
    }

    void HitPlayer()
    {
        // Content creatures carry their own authored damage (an alpha is already
        // scaled as a boss); the prototype path keeps the flat value + multiplier.
        float dmg = hasContentStats
            ? contactDamage
            : (isBoss ? 8f * GameConfig.Boss.DamageMultiplier : 8f);
        playerCtrl.TakeDamage(dmg);
    }

    void FaceDir(Vector3 dir)
    {
        if (dir == Vector3.zero) return;
        float targetRot = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
        transform.rotation = Quaternion.Euler(0f, Mathf.LerpAngle(transform.eulerAngles.y, targetRot, 0.15f), 0f);
    }

    // ── Floating health bar ───────────────────────────────────────────────────

    const float BarWidth = 1.4f;

    void UpdateHealthBar()
    {
        // Only show it once the enemy has been hit (and isn't down/dead) — except
        // for the Alpha, whose bar is up from the moment it arrives. It is the one
        // fight long enough for "am I even hurting this thing?" to be a real
        // question, and an undamaged Alpha with no bar reads as invulnerable.
        bool show = !isDead && !isDowned && (isBoss || health < maxHealth - 0.01f);

        if (!show)
        {
            if (healthBarGO != null && healthBarGO.activeSelf) healthBarGO.SetActive(false);
            return;
        }

        if (healthBarGO == null) CreateHealthBar();
        if (barCam == null) barCam = Camera.main;
        healthBarGO.SetActive(true);

        // Hover above the enemy, billboarded to the camera.
        float top = transform.localScale.y * 0.5f + 1.0f;
        healthBarGO.transform.position = transform.position + Vector3.up * top;
        if (barCam != null) healthBarGO.transform.rotation = barCam.transform.rotation;

        // Fill grows from the left; colour lerps red→green with health.
        float ratio = Mathf.Clamp01(health / maxHealth);
        healthFillTf.localScale    = new Vector3(BarWidth * ratio, 0.18f, 0.06f);
        healthFillTf.localPosition = new Vector3(-BarWidth * (1f - ratio) * 0.5f, 0f, -0.02f);
        if (healthFillRend != null)
            healthFillRend.material.color =
                Color.Lerp(new Color(1f, 0.25f, 0.2f), new Color(0.3f, 0.9f, 0.35f), ratio);
    }

    void CreateHealthBar()
    {
        healthBarGO = new GameObject("EnemyHealthBar");

        var bg = GameObject.CreatePrimitive(PrimitiveType.Cube);
        bg.name = "BG";
        Destroy(bg.GetComponent<Collider>());
        bg.transform.SetParent(healthBarGO.transform, false);
        bg.transform.localScale    = new Vector3(BarWidth, 0.18f, 0.05f);
        bg.GetComponent<Renderer>().material.color = new Color(0.08f, 0.08f, 0.08f, 1f);

        var fill = GameObject.CreatePrimitive(PrimitiveType.Cube);
        fill.name = "Fill";
        Destroy(fill.GetComponent<Collider>());
        fill.transform.SetParent(healthBarGO.transform, false);
        fill.transform.localScale    = new Vector3(BarWidth, 0.18f, 0.06f);
        fill.transform.localPosition = new Vector3(0f, 0f, -0.02f);
        healthFillTf   = fill.transform;
        healthFillRend = fill.GetComponent<Renderer>();
        healthFillRend.material.color = new Color(0.3f, 0.9f, 0.35f);
    }

    // ── Grazer mark ───────────────────────────────────────────────────────────
    // A heart floating over the one creature that heals you. Size alone says
    // "different"; the heart says *how*. Built from cubes like everything else in
    // the world — two lobes and a rotated square — rather than a sprite, so it
    // belongs to the same object language as the creatures and needs no texture.
    //
    // It is a separate object, not a child: BuildVisuals() destroys all children
    // on every rebuild, so anything following a creature has to live outside it.

    GameObject grazerMarkGO;

    void UpdateGrazerMark()
    {
        if (!isGrazer) return;

        // Gone once eaten; still shown while downed, because a downed grazer is
        // exactly the one you want to walk back to.
        if (isDead)
        {
            if (grazerMarkGO != null) grazerMarkGO.SetActive(false);
            return;
        }

        if (grazerMarkGO == null) CreateGrazerMark();
        if (barCam == null) barCam = Camera.main;
        grazerMarkGO.SetActive(true);

        // Hover above, billboarded, with a slow beat so the eye catches it across
        // a field of wandering meat.
        float top   = transform.localScale.y * 0.5f + 1.1f;
        float beat  = 1f + Mathf.Sin(Time.time * 3f) * 0.12f;
        grazerMarkGO.transform.position   = transform.position + Vector3.up * top;
        grazerMarkGO.transform.localScale = Vector3.one * beat;
        if (barCam != null) grazerMarkGO.transform.rotation = barCam.transform.rotation;
    }

    void CreateGrazerMark()
    {
        grazerMarkGO = new GameObject("GrazerHeart");

        var heart = new Color(1f, 0.30f, 0.42f);

        // Two lobes on top...
        for (int i = 0; i < 2; i++)
            AddHeartPiece(new Vector3(i == 0 ? -0.16f : 0.16f, 0.16f, 0f),
                          Quaternion.identity, new Vector3(0.32f, 0.32f, 0.08f), heart);

        // ...over a square stood on its corner, which reads as the point.
        AddHeartPiece(Vector3.zero, Quaternion.Euler(0f, 0f, 45f),
                      new Vector3(0.34f, 0.34f, 0.08f), heart);
    }

    void AddHeartPiece(Vector3 pos, Quaternion rot, Vector3 scale, Color color)
    {
        var piece = GameObject.CreatePrimitive(PrimitiveType.Cube);
        Destroy(piece.GetComponent<Collider>());
        piece.transform.SetParent(grazerMarkGO.transform, false);
        piece.transform.localPosition = pos;
        piece.transform.localRotation = rot;
        piece.transform.localScale    = scale;

        var mat = piece.GetComponent<Renderer>().material;
        mat.color = color;
        // Unlit-bright so it stays legible against dark ground and in fog.
        mat.EnableKeyword("_EMISSION");
        mat.SetColor("_EmissionColor", color * 0.9f);
    }

    void OnDestroy()
    {
        if (healthBarGO  != null) Destroy(healthBarGO);
        if (grazerMarkGO != null) Destroy(grazerMarkGO);
    }

    void UpdateDowned()
    {
        downedTimer -= Time.deltaTime;
        transform.rotation = Quaternion.Euler(0f, transform.eulerAngles.y + 120f * Time.deltaTime, 0f);
        Vector3 p = transform.position;
        p.y = GroundY(p);
        transform.position = p;
        if (downedTimer <= 0f) Recover();
    }

    // Push out of overlapping enemies (shared half each) and obstacles (full).
    void ResolveEnemyCollisions()
    {
        if (myCol == null) myCol = GetComponent<Collider>();
        if (myCol == null) return;

        float q = myCol.bounds.extents.magnitude + 2f;
        foreach (var other in Physics.OverlapSphere(transform.position, q))
        {
            if (other == myCol) continue;
            if (other.GetComponentInParent<PlayerController>() != null) continue; // player resolves itself

            bool isEnemy    = other.GetComponentInParent<EnemyAI>()  != null;
            bool isObstacle = other.GetComponentInParent<Obstacle>() != null;
            if (!isEnemy && !isObstacle) continue;

            if (Physics.ComputePenetration(
                    myCol, transform.position, transform.rotation,
                    other, other.transform.position, other.transform.rotation,
                    out Vector3 dir, out float dist))
            {
                Vector3 push = dir * dist; push.y = 0f;
                transform.position += isObstacle ? push : push * 0.5f;
            }
        }
    }
}
