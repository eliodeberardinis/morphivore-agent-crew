using UnityEngine;

// Marker for solid, static world obstacles the player collides with (e.g. the
// scattered crystals). No behaviour — PlayerController's collision resolution
// depenetrates against any collider that has this in its parent hierarchy.
public class Obstacle : MonoBehaviour { }
