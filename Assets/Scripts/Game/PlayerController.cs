using UnityEngine;
using UnityEngine.InputSystem;
using Morphivore.Content;

public class PlayerController : Creature
{
    public bool  gameStarted = false;
    public float moveSpeed;
    public float biteDamage;
    public int   totalKills  = 0;
    public int   score       = 0;

    // ── Form (§2.4a, §2.4b) ───────────────────────────────────────────────────
    // One colour slot per limb. What the slots hold resolves to exactly one of
    // the 150 forms, and that form is where every live stat comes from — there
    // is no hidden levelling underneath it.
    readonly ColourBuffer buffer = new ColourBuffer();

    public string FormName { get; private set; } = GameConfig.BlankFormName;

    float reach;      // lock + strike range, straight off the form
    float dashGear;   // form dash / form speed: the family's dash trade, scaled

    float biteCooldown  = 0f;
    float dashCooldown  = 0f;
    bool  isDashing     = false;
    float dashTimer     = 0f;
    bool  isLunging     = false;   // mid-pounce

    // Lock-on (Cubivore-style "target then launch"). Hold lock to acquire the
    // nearest enemy roughly in front; pounce launches at the locked target.
    bool     isLocking    = false;
    EnemyAI  lockedTarget = null;
    const float LockConeDot = 0.2f; // ~78° half-cone around facing to be lockable

    // Tells the HUD which transform to draw the lock-on reticle over (null = hide).
    public System.Action<Transform> OnLockTargetChanged;

    // Threat: refreshed by any enemy currently locked onto us; drives the "you
    // are targeted" halo so the player can react to an incoming pounce.
    float threatTimer = 0f;
    public bool IsThreatened => threatTimer > 0f;
    public void FlagThreat() { threatTimer = 0.25f; }

    int companionCount = 0;

    // Events consumed by GameManager
    public System.Action<string>               OnNotification;
    public System.Action<GameConfig.BiomeData> OnBiomeRequest;
    // Fires on eating coloured prey: the form the meal resolved to, and the
    // family of the meat. The ecosystem listens for it to advance the Alpha's
    // gates and to decide which champion answers.
    public System.Action<string, string>       OnAtePrey;
    // Fires on eating an Alpha: its emblem (null if the content has none) and its
    // name. An emblem whose `opens_biome` is empty was taken from the last Alpha
    // in the world — that one ends the run in victory rather than opening a door.
    public System.Action<EmblemDef, string>    OnAlphaEaten;

    // Body collider used for solid collision resolution (radius scales with rank).
    SphereCollider bodyCollider;

    protected override void Awake()
    {
        base.Awake();

        // Solid body: a collider on the root (BuildVisuals only clears child
        // colliders) plus a kinematic rigidbody so moving it stays cheap. We
        // still move via transform and depenetrate manually (ResolveCollisions).
        bodyCollider = gameObject.AddComponent<SphereCollider>();
        bodyCollider.radius = 0.5f;
        var rb = gameObject.AddComponent<Rigidbody>();
        rb.isKinematic = true;
        rb.useGravity  = false;

        // The hatchling is the blank: a white cube with one bare limb, multiplier
        // 1.0 on every axis. Its first meal is its first identity.
        buffer.Resize(rank);
        ApplyForm();
        BuildVisuals();
    }

    // ── Form resolution and stats ─────────────────────────────────────────────

    // Resolve the buffer, look the form up in forms.json and take its stat line.
    // Deterministic (not incremental), so a meal can never double-apply.
    void ApplyForm()
    {
        FormKey key = buffer.Resolve();
        family    = key.family;
        intensity = key.intensity;

        var def = ContentDatabase.Form(family, intensity, rank);
        GameConfig.StatLine s;

        if (def?.stats != null)
        {
            // The authored line: the same composition, hand-tuned per form.
            s = new GameConfig.StatLine
            {
                health = def.stats.health, damage = def.stats.damage,
                speed  = def.stats.speed,  reach  = def.stats.reach,
                dash   = def.stats.dash
            };
            FormName = def.name;
        }
        else
        {
            // No forms.json: compose the limb baseline × family × intensity here.
            s = GameConfig.StatsFor(family, intensity, rank);
            FormName = GameConfig.FormNameFor(family, intensity);
        }

        // Mutating re-cuts the bar and preserves the wound, not the number: you
        // keep the same fraction, so it never heals and never costs a point (§2.3).
        float wound = maxHealth > 0f ? Mathf.Clamp01(health / maxHealth) : 1f;
        maxHealth   = s.health;
        health      = maxHealth * wound;

        moveSpeed  = s.speed;
        biteDamage = s.damage;
        reach      = s.reach;
        dashGear   = s.speed > 0f ? s.dash / s.speed : 1f;
    }

    /// <summary>Add a limb (§2.5). The buffer grows with the body, keeping the
    /// colours already held in the limbs they occupy, so the new slot comes up
    /// white and the next meal fills it rather than evicting anything. This is
    /// what finally exercises FIFO eviction and the dilution rule — at rank 1 the
    /// buffer holds one colour and every meal simply replaces it.</summary>
    public void Grow()
    {
        if (rank >= GameConfig.Ranks.Length) return;

        rank++;
        buffer.Resize(rank);
        ApplyForm();
        BuildVisuals();
    }

    // Any change to the buffer redraws the body (limb colours are buffer state)
    // and re-stats; a change of *form* is the mutation, and it fires instantly.
    void OnBufferChanged()
    {
        string wasFamily    = family;
        int    wasIntensity = intensity;

        ApplyForm();
        BuildVisuals();

        if (family != wasFamily || intensity != wasIntensity)
            OnNotification?.Invoke($"MUTATED — {FormName.ToUpper()}!");
    }

    // A limb shows what it is holding: its family's colour, saturated by its
    // tier — Pale meat reads washed out, Rage meat reads full (§2.4b).
    protected override Color LimbColor(int index)
    {
        if (index >= buffer.Count) return GameConfig.Colors.White;
        ColourUnit unit = buffer[index];
        if (unit.IsWhite) return GameConfig.Colors.White;
        return Color.Lerp(GameConfig.Colors.White,
                          GameConfig.Colors.ForFamily(unit.family),
                          GameConfig.Intensities[unit.intensity].pct);
    }

    // The next slot to be overwritten always pulses on the body, so a colour is
    // never lost unknowingly (§2.4a). Scale and glow, never opacity (§4.9a).
    void PulseNextSlot()
    {
        int next = buffer.NextSlot;
        if (next < 0 || next >= limbs.Length || limbs[next] == null) return;

        float pulse = 0.5f + 0.5f * Mathf.Sin(Time.time * 6f);
        limbs[next].transform.localScale = Vector3.one * (0.3f + 0.09f * pulse);

        var mat = limbs[next].GetComponent<Renderer>().material;
        mat.EnableKeyword("_EMISSION");
        mat.SetColor("_EmissionColor", LimbColor(next) * (0.25f + 0.55f * pulse));
    }

    // Q / B: the oldest colour goes out, that limb turns white, and the unit is
    // left behind you on the ground.
    void Poop()
    {
        if (!buffer.Poop(out ColourUnit dropped)) return;
        LeaveDropping(dropped);
        OnBufferChanged();
    }

    void LeaveDropping(ColourUnit unit)
    {
        var drop = GameObject.CreatePrimitive(PrimitiveType.Cube);
        drop.name = "Dropping";
        Destroy(drop.GetComponent<Collider>());
        drop.transform.localScale = Vector3.one * 0.35f;

        Vector3 behind = transform.position - transform.forward * (transform.localScale.z * 0.8f);
        behind.y = Morphivore.World.BiomeTerrain.HeightAt(behind.x, behind.z) + 0.18f;
        drop.transform.position = behind;
        drop.transform.rotation = Quaternion.Euler(Random.Range(0f, 360f), Random.Range(0f, 360f), 0f);

        drop.GetComponent<Renderer>().material.color =
            GameConfig.Colors.ForFamily(unit.family) * 0.7f;
    }

    protected override void Update()
    {
        base.Update();
        if (!gameStarted || isDead) return;

        // Cooldowns
        if (biteCooldown  > 0f) biteCooldown  -= Time.deltaTime;
        if (dashCooldown  > 0f) dashCooldown  -= Time.deltaTime;
        if (isDashing)
        {
            dashTimer -= Time.deltaTime;
            if (dashTimer <= 0f) isDashing = false;
        }

        if (threatTimer > 0f) threatTimer -= Time.deltaTime;

        // Regen
        if (health < maxHealth) health += GameConfig.RegenRate * Time.deltaTime;

        PulseNextSlot();

        // Movement — keyboard + gamepad left stick
        var kb = Keyboard.current;
        Vector3 move = Vector3.zero;

        if (kb != null)
        {
            if (kb.wKey.isPressed || kb.upArrowKey.isPressed)    move += Vector3.forward;
            if (kb.sKey.isPressed || kb.downArrowKey.isPressed)  move += Vector3.back;
            if (kb.aKey.isPressed || kb.leftArrowKey.isPressed)  move += Vector3.left;
            if (kb.dKey.isPressed || kb.rightArrowKey.isPressed) move += Vector3.right;
        }

        bool gpLock   = false;
        bool gpPounce = false;
        bool gpDash   = false;
        bool gpPoop   = false;

        foreach (var gp in Gamepad.all)
        {
            Vector2 ls = gp.leftStick.ReadValue();
            if (ls.magnitude > 0.15f) move += new Vector3(ls.x, 0f, ls.y);

            if (gp.dpad.up.isPressed)    move += Vector3.forward;
            if (gp.dpad.down.isPressed)  move += Vector3.back;
            if (gp.dpad.left.isPressed)  move += Vector3.left;
            if (gp.dpad.right.isPressed) move += Vector3.right;

            if (gp.leftShoulder.isPressed)           gpLock   = true; // hold LB = hard-lock
            if (gp.buttonSouth.wasPressedThisFrame)  gpPounce = true; // A       = pounce
            if (gp.rightTrigger.wasPressedThisFrame) gpDash   = true; // RT      = dash
            if (gp.buttonEast.wasPressedThisFrame)   gpPoop   = true; // B       = poop
        }

        // Mouse buttons for combat: LMB pounce, hold RMB hard-lock, Space dash.
        var mouse = Mouse.current;
        bool hardLockHeld  = gpLock   || (mouse != null && mouse.rightButton.isPressed);
        bool pouncePressed = gpPounce || (mouse != null && mouse.leftButton.wasPressedThisFrame);
        bool dashPressed   = gpDash   || (kb != null && kb.spaceKey.wasPressedThisFrame);
        bool poopPressed   = gpPoop   || (kb != null && kb.qKey.wasPressedThisFrame);

        // Move — facing follows the movement direction.
        if (move != Vector3.zero && !isLunging)
        {
            move = move.normalized;
            float speed = moveSpeed * (isDashing ? 3f : 1f);
            transform.position += move * speed * Time.deltaTime;

            float ang = Mathf.Atan2(move.x, move.z) * Mathf.Rad2Deg;
            transform.rotation = Quaternion.Euler(0f, Mathf.LerpAngle(transform.eulerAngles.y, ang, 0.25f), 0f);
        }

        // Hard-lock: acquire/keep a target within the facing cone.
        UpdateLock(hardLockHeld);

        if (dashPressed)   Dash();
        if (pouncePressed) Pounce();
        if (poopPressed)   Poop();

        // Solid bodies: push out of any enemies/obstacles we overlap.
        ResolveCollisions();

        // Clamp to world
        float limit = Morphivore.World.BiomeTerrain.Radius;
        Vector3 pos = transform.position;
        pos.x = Mathf.Clamp(pos.x, -limit, limit);
        pos.z = Mathf.Clamp(pos.z, -limit, limit);
        pos.y = StickY(pos);
        transform.position = pos;
    }

    void Dash()
    {
        if (dashCooldown > 0f || isDead) return;
        isDashing    = true;
        // A Leaper's dash runs longer and recovers sooner; a Brawler's does neither.
        dashTimer    = 0.2f * dashGear;
        dashCooldown = 1.5f / dashGear;
    }

    // Push the player out of any overlapping enemy/obstacle so bodies feel solid.
    // We move by transform (not physics), so we depenetrate manually each frame.
    void ResolveCollisions()
    {
        // Skip mid-pounce so lunges drive into enemies instead of bouncing off.
        if (bodyCollider == null || isLunging) return;

        float myRadius    = bodyCollider.radius * transform.lossyScale.x;
        float queryRadius = myRadius + 4f; // margin to catch large neighbours

        foreach (var other in Physics.OverlapSphere(transform.position, queryRadius))
        {
            if (other == bodyCollider) continue;
            bool solid = other.GetComponentInParent<EnemyAI>() != null
                      || other.GetComponentInParent<Obstacle>() != null;
            if (!solid) continue;

            if (Physics.ComputePenetration(
                    bodyCollider, transform.position, transform.rotation,
                    other, other.transform.position, other.transform.rotation,
                    out Vector3 dir, out float dist))
            {
                Vector3 push = dir * dist;
                push.y = 0f; // horizontal only — keep the ground/height logic intact
                transform.position += push;
            }
        }
    }

    // ── Lock-on ───────────────────────────────────────────────────────────────

    // How far this beast can lock onto and strike an enemy: the form's Reach,
    // plus its own body so a big animal doesn't have to overlap what it grabs.
    // Reach is a family trade — a Sniper locks from outside a Brawler's world.
    float ReachRange() => reach + transform.localScale.x * 0.5f;

    void UpdateLock(bool lockHeld)
    {
        EnemyAI before = lockedTarget;

        if (lockHeld && !isDead)
        {
            isLocking = true;

            // Drop the lock if the target died or drifted out of reach (with a
            // little hysteresis so it doesn't flicker at the edge).
            if (lockedTarget != null)
            {
                float keep = ReachRange() * 1.15f;
                if (lockedTarget.isDead ||
                    Vector3.Distance(transform.position, lockedTarget.transform.position) > keep)
                    lockedTarget = null;
            }

            if (lockedTarget == null) lockedTarget = AcquireTarget();
        }
        else if (isLocking)
        {
            isLocking    = false;
            lockedTarget = null;
        }

        // On any target change, update the enemies' "I'm targeted" flags and the
        // HUD reticle (the reticle then follows the target each frame).
        if (before != lockedTarget)
        {
            if (before != null)       before.isLockedByPlayer = false;
            if (lockedTarget != null) lockedTarget.isLockedByPlayer = true;
            OnLockTargetChanged?.Invoke(lockedTarget != null ? lockedTarget.transform : null);
        }
    }

    // Nearest enemy within ReachRange that sits roughly within the facing cone.
    // Sticky once locked (see UpdateLock) until it dies, drifts out of reach, or
    // the lock is released.
    EnemyAI AcquireTarget()
    {
        Vector3 fwd  = transform.forward;
        EnemyAI best = null;
        float   bestScore = float.NegativeInfinity;

        foreach (var col in Physics.OverlapSphere(transform.position, ReachRange()))
        {
            var enemy = col.GetComponentInParent<EnemyAI>();
            if (enemy == null || enemy.isDead) continue;

            Vector3 to = enemy.transform.position - transform.position; to.y = 0f;
            float dist = to.magnitude;
            if (dist < 0.01f) continue;

            float dot = Vector3.Dot(fwd, to / dist);
            if (dot < LockConeDot) continue; // must be within the facing cone

            // Prefer targets more in-line with facing and closer.
            float score = dot - dist * 0.03f;
            if (score > bestScore) { bestScore = score; best = enemy; }
        }
        return best;
    }

    // ── Pounce (targeted tackle) ──────────────────────────────────────────────

    void Pounce()
    {
        if (isLunging || biteCooldown > 0f || isDead) return;
        biteCooldown = 0.4f;

        // Prefer the hard-locked target; otherwise soft-lock the enemy nearest
        // in the facing cone; otherwise just pounce straight ahead.
        EnemyAI target = (lockedTarget != null && !lockedTarget.isDead) ? lockedTarget : AcquireTarget();

        Vector3 dir = transform.forward;
        if (target != null)
        {
            Vector3 to = target.transform.position - transform.position; to.y = 0f;
            if (to.sqrMagnitude > 0.001f) dir = to.normalized;
        }
        StartCoroutine(PounceAnim(dir));
    }

    System.Collections.IEnumerator PounceAnim(Vector3 dir)
    {
        isLunging = true;
        Vector3 lungeDir = dir.normalized;
        // Snap facing to the pounce direction.
        transform.rotation = Quaternion.Euler(0f, Mathf.Atan2(lungeDir.x, lungeDir.z) * Mathf.Rad2Deg, 0f);

        // Fixed-power pounce (no charge): it carries exactly one Reach, so what
        // you can lock is what you can hit.
        float duration   = 0.3f;
        float lungeSpeed = ReachRange() / duration;
        float damageMult = 3f;
        float elapsed    = 0f;

        if (body) body.transform.localScale = new Vector3(1f, 1f, 1.5f);

        var hitEnemies = new System.Collections.Generic.HashSet<EnemyAI>();
        bool impact = false; // hit something solid → stop and bounce back

        while (elapsed < duration && !impact)
        {
            transform.position += lungeDir * lungeSpeed * Time.deltaTime;

            // The island's own edge, the same bound walking uses. This read
            // GameConfig.WorldSize, which is the world's *width* (100 units
            // across, mesh spanning ±50) — used here as a half-extent it let a
            // pounce carry the player to ±100, well past the mesh, where
            // SampleHeight has nothing to sample and the ground goes flat and
            // wrongly coloured. Radius is the one source of truth for the edge.
            float limit = Morphivore.World.BiomeTerrain.Radius;
            Vector3 pos = transform.position;
            pos.x = Mathf.Clamp(pos.x, -limit, limit);
            pos.z = Mathf.Clamp(pos.z, -limit, limit);
            pos.y = StickY(pos);
            transform.position = pos;

            Vector3 hitCenter   = transform.position + transform.forward * transform.localScale.x;
            Vector3 halfExtents = transform.localScale * 0.5f;
            var hits = Physics.OverlapBox(hitCenter, halfExtents, transform.rotation);

            foreach (var col in hits)
            {
                var enemy = col.GetComponentInParent<EnemyAI>();
                if (enemy == null || enemy.isDead || hitEnemies.Contains(enemy)) continue;
                hitEnemies.Add(enemy);

                if (enemy.isDowned)
                {
                    // Eat the downed enemy: absorb its meat (colour) now, and play
                    // the grab-and-absorb animation as it's pulled into us.
                    OnKill(enemy);
                    enemy.GetEaten(transform);
                }
                else if (rank >= enemy.rank)
                {
                    // Damage (may knock it down) + shove it, and bounce ourselves back.
                    enemy.TakeDamage(biteDamage * damageMult);
                    enemy.transform.position += lungeDir * 0.6f * transform.localScale.x;
                    impact = true;
                }
                else
                {
                    // Bigger animal than us: it hurts us and we bounce off.
                    //
                    // This used to compare *intensity*, and that was a rule the GDD
                    // never had. Meat tier is what you are made of, not what you can
                    // bite: Clash never wanders (§2.4), and the Alpha is "always at
                    // Clash intensity" at your own rank (§2.5) — so a Prairies player,
                    // capped at Dusk by the only meat that spawns there, could not
                    // scratch the Alpha the game had just sent to hunt them. It is
                    // also why PocketLeakChance is pinned at 0: Clash elites were
                    // unkillable escorts for the same reason.
                    //
                    // Rank is the GDD's size axis (§2.5), and §3.3 pins ambient rank
                    // at prey = player-1, elites = player, Alphas = player. So this
                    // guard is the one the design actually asks for — and until
                    // breeding moves rank off 1, it never fires.
                    TakeDamage(10f);
                    impact = true;
                }
            }

            elapsed += Time.deltaTime;
            yield return null;
        }

        // Bounce back off a solid hit.
        if (impact)
        {
            float rt = 0f, recoilDur = 0.12f;
            float recoilSpeed = lungeSpeed * 0.7f;
            while (rt < recoilDur)
            {
                transform.position -= lungeDir * recoilSpeed * Time.deltaTime;

                float limit = Morphivore.World.BiomeTerrain.Radius;
                Vector3 p = transform.position;
                p.x = Mathf.Clamp(p.x, -limit, limit);
                p.z = Mathf.Clamp(p.z, -limit, limit);
                p.y = StickY(p);
                transform.position = p;

                rt += Time.deltaTime;
                yield return null;
            }
        }

        // Reset body stretch
        if (body) body.transform.localScale = Vector3.one;
        isLunging = false;
    }

    public void RegisterKill(EnemyAI enemy) => OnKill(enemy);

    void OnKill(EnemyAI enemy)
    {
        // Mating: killing a pink mate spawns a companion
        if (enemy is MateEnemy)
        {
            SpawnCompanion();
            OnNotification?.Invoke("OFFSPRING SPAWNED!");
            score += 500;
            return;
        }

        totalKills++;
        score += (enemy.intensity + 1) * 100;

        // Eating the biome's champion is the only thing that grows a body (§2.5).
        // The GDD spends that through a litter — beat the Alpha, take its emblem,
        // continue as one offspring a limb larger. The litter screen is B2 and is
        // not built, so the limb is granted directly: the same rank movement, minus
        // the choice. Everything downstream is already wired for it — biomes.json
        // gates each biome on player_rank 1..5, and EcosystemManager advances on
        // its own once rank reaches the next one.
        if (enemy.isBoss)
        {
            score += 2500;
            var emblem = ContentDatabase.EmblemFor(enemy.contentId);
            Grow();
            OnAlphaEaten?.Invoke(emblem, enemy.displayName);
        }

        // Grazers are food, not meat: they heal an authored share of max health
        // (heals_player_pct) and never touch the buffer, because they carry no
        // colour — there is nothing in them to take.
        float heal = enemy.healsPlayerPct > 0f ? maxHealth * enemy.healsPlayerPct : 20f;
        health = Mathf.Min(maxHealth, health + heal);

        // Coloured prey streams into a limb: the first white one, or — with every
        // limb loaded — over the colour held longest (§2.4a).
        if (enemy.carriesColour && !string.IsNullOrEmpty(enemy.family))
        {
            buffer.Eat(enemy.family, enemy.intensity);
            OnBufferChanged();

            // Both of the Alpha's gates are fed from here, and only from here:
            // it counts meat, so a grazer never moves either one. The form
            // reported is the one this meal *left* the player in, so the
            // distinct-forms gate counts what you became, not what you chewed —
            // while the family is the prey's own, which is what decides who comes
            // for you (§2.5: the champion of the colour you ate most).
            OnAtePrey?.Invoke(FormName, enemy.family);
        }
    }

    void SpawnCompanion()
    {
        var go = new GameObject("Companion");

        // Mini cube body in player's colour
        var body = GameObject.CreatePrimitive(PrimitiveType.Cube);
        Destroy(body.GetComponent<Collider>());
        body.transform.SetParent(go.transform, false);
        body.GetComponent<Renderer>().material.color = GameConfig.Colors.ForFamily(family);

        // Eyes
        for (int s = -1; s <= 1; s += 2)
        {
            var eye = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Destroy(eye.GetComponent<Collider>());
            eye.transform.SetParent(go.transform, false);
            eye.transform.localScale    = new Vector3(0.2f, 0.2f, 0.1f);
            eye.transform.localPosition = new Vector3(s * 0.25f, 0.2f, 0.5f);
            eye.GetComponent<Renderer>().material.color = Color.black;
        }

        // Scale smaller than player
        go.transform.localScale = transform.localScale * 0.5f;
        go.transform.position   = transform.position + transform.right * (companionCount + 1) * 2f;

        var comp   = go.AddComponent<Companion>();
        comp.target = transform;
        comp.index  = companionCount;
        companionCount++;
    }
}
