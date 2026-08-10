using UnityEngine;

public class HumanWalk : MonoBehaviour
{
    [Header("Movement")]
    public float speed = 1.5f;
    public float distance = 10f;

    [Header("Leg swing")]
    public float legSwingAngle = 35f;
    public float legFrequency = 1.8f;

    [Header("Arm swing")]
    public float armSwingAngle = 30f;

    [Header("Body bob")]
    public float bobAmount = 0.04f;

    Transform _upperLegL, _upperLegR;
    Transform _lowerLegL, _lowerLegR;
    Transform _upperArmL, _upperArmR;
    Transform _lowerArmL, _lowerArmR;
    Transform _torso;

    Vector3 _startPos;
    float _elapsed;
    bool _done;

    void Start()
    {
        _upperLegL = Find("Hips/UpperLeg_L");
        _upperLegR = Find("Hips/UpperLeg_R");
        _lowerLegL = Find("Hips/UpperLeg_L/LowerLeg_L");
        _lowerLegR = Find("Hips/UpperLeg_R/LowerLeg_R");
        _upperArmL = Find("Torso/UpperArm_L");
        _upperArmR = Find("Torso/UpperArm_R");
        _lowerArmL = Find("Torso/UpperArm_L/LowerArm_L");
        _lowerArmR = Find("Torso/UpperArm_R/LowerArm_R");
        _torso     = Find("Torso");
        _startPos  = transform.position;
    }

    Transform Find(string path) => transform.Find(path);

    void Update()
    {
        if (_done) return;

        _elapsed += Time.deltaTime;
        float walked = _elapsed * speed;

        if (walked >= distance)
        {
            walked = distance;
            _done = true;
        }

        // Move forward (Z axis)
        transform.position = _startPos + new Vector3(0, 0, walked);

        float phase = _elapsed * legFrequency * 2f * Mathf.PI;

        // Upper legs swing forward/back on X axis
        float legSwing = Mathf.Sin(phase) * legSwingAngle;
        if (_upperLegL) _upperLegL.localEulerAngles = new Vector3(legSwing, 0, 0);
        if (_upperLegR) _upperLegR.localEulerAngles = new Vector3(-legSwing, 0, 0);

        // Lower legs bend (always positive — knee only bends backward)
        float kneeL = Mathf.Max(0, -Mathf.Sin(phase)) * legSwingAngle * 0.8f;
        float kneeR = Mathf.Max(0,  Mathf.Sin(phase)) * legSwingAngle * 0.8f;
        if (_lowerLegL) _lowerLegL.localEulerAngles = new Vector3(kneeL, 0, 0);
        if (_lowerLegR) _lowerLegR.localEulerAngles = new Vector3(kneeR, 0, 0);

        // Arms swing opposite to legs
        float armSwing = Mathf.Sin(phase) * armSwingAngle;
        if (_upperArmL) _upperArmL.localEulerAngles = new Vector3(-armSwing, 0, 0);
        if (_upperArmR) _upperArmR.localEulerAngles = new Vector3(armSwing, 0, 0);

        // Slight forearm bend during swing
        if (_lowerArmL) _lowerArmL.localEulerAngles = new Vector3(Mathf.Abs(armSwing) * 0.3f, 0, 0);
        if (_lowerArmR) _lowerArmR.localEulerAngles = new Vector3(Mathf.Abs(armSwing) * 0.3f, 0, 0);

        // Body bob up/down
        if (_torso)
        {
            var p = _torso.localPosition;
            p.y = Mathf.Abs(Mathf.Sin(phase)) * bobAmount;
            _torso.localPosition = p;
        }
    }
}
