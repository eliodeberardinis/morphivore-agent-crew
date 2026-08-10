// Editor-only sanity check on the generated world content: does it parse, does
// every biome have something to spawn, and does the weighted roll actually
// produce the family mix the biome asks for? Run it after regenerating content,
// without entering Play mode.
//
// Tools → Morphivore → Verify World Content
using System.Collections.Generic;
using System.Text;
using Morphivore.Content;
using UnityEditor;
using UnityEngine;

public static class ContentCheck
{
    const int RollSamples = 2000;

    [MenuItem("Tools/Morphivore/Verify World Content")]
    public static void Verify()
    {
        ContentDatabase.Reset(); // always check what's on disk right now

        if (!ContentDatabase.Load())
        {
            Debug.LogError($"[ContentCheck] FAILED to load: {ContentDatabase.LoadError}");
            return;
        }

        var sb = new StringBuilder("[ContentCheck] world content\n");
        bool ok = true;

        foreach (var biome in ContentDatabase.Biomes.biomes)
        {
            var wander = ContentDatabase.Wandering(biome.id);
            var pocket = ContentDatabase.Pocket(biome.id);

            int nWander = wander?.Count ?? 0;

            sb.AppendLine($"  {biome.id} (order {biome.order}, rank {biome.player_rank}): " +
                          $"{nWander} wandering, {pocket?.Count ?? 0} pocket, " +
                          $"{biome.alpha_roster?.Length ?? 0} alphas, " +
                          $"pop {biome.standing_population}, respawn {biome.respawn_per_min}/min");

            if (nWander == 0)
            {
                sb.AppendLine("    ERROR: nothing wanders here — the ambient roll would fail.");
                ok = false;
            }

            // Roll the ambient pool and report the family mix it produces. It
            // should track palette_weights; a family weighted 0 must never show.
            var mix = new Dictionary<string, int>();
            for (int i = 0; i < RollSamples; i++)
            {
                if (!ContentDatabase.RollSpawn(biome, wander, out var e)) { ok = false; break; }
                string fam = string.IsNullOrEmpty(e.def.family) ? "(grazer)" : e.def.family;
                mix.TryGetValue(fam, out int n);
                mix[fam] = n + 1;
            }

            sb.Append("    rolled: ");
            foreach (var kv in mix) sb.Append($"{kv.Key} {kv.Value * 100f / RollSamples:0.#}%  ");
            sb.AppendLine();

            if (biome.palette_weights == null)
            {
                sb.AppendLine("    ERROR: palette_weights did not deserialise.");
                ok = false;
            }
            else
            {
                foreach (var fam in new[] { "Yellow", "Red", "Blue", "Purple", "Grey" })
                    if (biome.palette_weights.For(fam) <= 0f && mix.ContainsKey(fam))
                    {
                        sb.AppendLine($"    ERROR: {fam} is weighted 0 here but still rolled.");
                        ok = false;
                    }
            }

            // Every alpha in the roster must have a stat block for this biome.
            foreach (var id in biome.alpha_roster ?? new string[0])
            {
                var def = ContentDatabase.ById(id);
                if (def == null) { sb.AppendLine($"    ERROR: alpha '{id}' not in creatures.json"); ok = false; continue; }
                if (!HasSpawn(def, biome.id)) { sb.AppendLine($"    ERROR: alpha '{id}' has no spawn for {biome.id}"); ok = false; }
            }
        }

        sb.AppendLine(ok ? "  RESULT: OK" : "  RESULT: PROBLEMS FOUND (see above)");
        if (ok) Debug.Log(sb.ToString());
        else    Debug.LogError(sb.ToString());
    }

    static bool HasSpawn(CreatureDef def, string biomeId)
    {
        if (def.spawns == null) return false;
        foreach (var s in def.spawns) if (s != null && s.biome == biomeId) return true;
        return false;
    }
}
