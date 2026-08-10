using UnityEngine;

/// <summary>One colour unit — a family at an intensity — sitting in a limb.
/// A white (empty) slot carries no family.</summary>
public struct ColourUnit
{
    public string family;
    public int    intensity;
    public int    eaten;      // insertion order; the buffer is strictly FIFO

    public bool IsWhite => string.IsNullOrEmpty(family);
}

/// <summary>The form a buffer state names: a family at an intensity, or the
/// blank when every limb is white.</summary>
public struct FormKey
{
    public string family;
    public int    intensity;

    public bool IsBlank => string.IsNullOrEmpty(family);
}

// ── The colour buffer (§2.4a) ────────────────────────────────────────────────
// One slot per limb, filled by eating and emptied by pooping, on rules the
// player can execute in their head: white limb first, else the oldest colour
// goes. Nothing here is hidden — the forcing comes from what the world serves.
public class ColourBuffer
{
    ColourUnit[] slots = new ColourUnit[0];
    int eatCount = 0;

    public int Count => slots.Length;
    public ColourUnit this[int i] => slots[i];

    /// <summary>One slot per limb. Rank only ever grows (breeding, §2.5), so the
    /// colours already held keep the limbs they are in.</summary>
    public void Resize(int limbs)
    {
        if (limbs == slots.Length) return;
        var resized = new ColourUnit[Mathf.Max(0, limbs)];
        for (int i = 0; i < Mathf.Min(resized.Length, slots.Length); i++) resized[i] = slots[i];
        slots = resized;
    }

    /// <summary>The slot the next meal lands in: the first white limb, or — with
    /// every limb coloured — the oldest colour, which the meal evicts. This is
    /// the slot that pulses on the body, so a colour is never lost unknowingly.</summary>
    public int NextSlot
    {
        get
        {
            for (int i = 0; i < slots.Length; i++)
                if (slots[i].IsWhite) return i;
            return Oldest();
        }
    }

    public void Eat(string family, int intensity)
    {
        int slot = NextSlot;
        if (slot < 0) return;   // no limbs at all: nothing can be held
        slots[slot] = new ColourUnit { family = family, intensity = intensity, eaten = ++eatCount };
    }

    /// <summary>Q / B: the oldest colour goes out and its limb turns white.
    /// False when there is nothing coloured to lose.</summary>
    public bool Poop(out ColourUnit dropped)
    {
        dropped = default;
        int slot = Oldest();
        if (slot < 0) return false;
        dropped     = slots[slot];
        slots[slot] = default;
        return true;
    }

    int Oldest()
    {
        int oldest = -1;
        for (int i = 0; i < slots.Length; i++)
        {
            if (slots[i].IsWhite) continue;
            if (oldest < 0 || slots[i].eaten < slots[oldest].eaten) oldest = i;
        }
        return oldest;
    }

    // ── Resolution (§2.4b) ───────────────────────────────────────────────────

    /// <summary>Every buffer state resolves to exactly one form — no recipes, no
    /// invalid states.</summary>
    public FormKey Resolve()
    {
        // Family = the colour holding the most limbs. Ties break toward the most
        // recently eaten and then, for a litter born with its limbs loaded in one
        // go, toward the fixed precedence Yellow → Red → Blue → Purple → Grey,
        // which is the order GameConfig.Families is written in.
        string family    = null;
        int    bestCount = 0;
        int    bestEaten = -1;

        foreach (var f in GameConfig.Families)
        {
            int count = 0, newest = -1;
            for (int i = 0; i < slots.Length; i++)
            {
                if (slots[i].family != f.name) continue;
                count++;
                if (slots[i].eaten > newest) newest = slots[i].eaten;
            }

            if (count == 0) continue;
            if (count > bestCount || (count == bestCount && newest > bestEaten))
            {
                family    = f.name;
                bestCount = count;
                bestEaten = newest;
            }
        }

        if (family == null) return new FormKey();   // all limbs white: the blank

        // Intensity = the lowest tier among the family's own units ("your weakest
        // meat sets your intensity"), stepped down one rung for every limb not
        // carrying the family, floored at Pale.
        int rung = int.MaxValue;
        for (int i = 0; i < slots.Length; i++)
            if (slots[i].family == family)
                rung = Mathf.Min(rung, GameConfig.LadderRung(slots[i].intensity));

        rung = Mathf.Max(0, rung - (slots.Length - bestCount));

        // Clash shares the top rung with Rage rather than sitting above it, and
        // any Clash unit wins that tie; dilute either and it slides off to Deep.
        int intensity = GameConfig.WildLadder[rung];
        if (intensity == GameConfig.Rage && HoldsClash(family)) intensity = GameConfig.Clash;

        return new FormKey { family = family, intensity = intensity };
    }

    bool HoldsClash(string family)
    {
        for (int i = 0; i < slots.Length; i++)
            if (slots[i].family == family && slots[i].intensity == GameConfig.Clash) return true;
        return false;
    }
}
