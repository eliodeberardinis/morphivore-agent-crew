// Hand-written loader for emblems.json, the last file in the §3.3 content
// contract. Written alongside the Assignment #6 GER pipeline that generates it.
//
// An emblem is a trophy cut off a defeated Alpha (§2.5). It does exactly two
// things — opens the way to the next biome, and enables breeding — and grants
// no power of its own; powers come from panels. There is deliberately no field
// here for an effect, a stat or a magnitude, because the type is part of how
// that rule is kept: content that tried to grant a power would have nowhere to
// put it.
using System;
using UnityEngine;

namespace Morphivore.Content
{
    [Serializable]
    public class EmblemDef
    {
        public string id;           // emblem_<biome>_<family>
        public string alpha_id;     // the Alpha it was taken from
        public string biome;        // where that Alpha lives
        public string opens_biome;  // the biome it unlocks; empty for the last
        public string name;
        public string flavor;

        /// <summary>The final biome's emblems open nothing (§4.9) — the run ends
        /// at the Ascension rather than at another door.</summary>
        public bool OpensNothing => string.IsNullOrEmpty(opens_biome);
    }

    [Serializable]
    public class EmblemTable
    {
        public string generated_by;
        public string rule_enforced;
        public int count;
        public EmblemDef[] emblems;

        public static EmblemTable Load(string json) =>
            JsonUtility.FromJson<EmblemTable>(json);
    }
}
