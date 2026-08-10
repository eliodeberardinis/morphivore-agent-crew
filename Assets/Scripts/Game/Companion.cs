using UnityEngine;

public class Companion : MonoBehaviour
{
    public Transform target;
    public int       index; // offset slot so multiple companions don't stack

    float followSpeed = 8f;

    void Start()
    {
        // Visual: mini version of player (built by whoever spawns us)
    }

    void Update()
    {
        if (target == null) return;

        // Orbit slightly behind and to the side of the player
        float angle  = index * 60f * Mathf.Deg2Rad;
        Vector3 offset = new Vector3(Mathf.Sin(angle) * 2f, 0f, -2f - index * 0.5f);
        Vector3 worldOffset = target.TransformDirection(offset);
        Vector3 desired = target.position + worldOffset;

        transform.position = Vector3.Lerp(transform.position, desired, followSpeed * Time.deltaTime);
        transform.rotation = Quaternion.Lerp(transform.rotation, target.rotation, followSpeed * Time.deltaTime);
    }
}
