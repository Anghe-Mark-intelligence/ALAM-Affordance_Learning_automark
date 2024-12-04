#include <stdio.h>

typedef enum {
    GRIPPER = 1,
    SUCTION_CUP,
    WELDER,
    PAINT_BRUSH,
    DRILL,
    SCREWDRIVER,
    HAMMER,
    VACUUM,
    LIGHT,
    CAMERA,
    LASER,
    CUTTER
} EndEffectorType;

typedef struct {
    int id;  // unique identifier for the end effector
    EndEffectorType type; // type of end effector
} MarkControl;

void initMarkControl(MarkControl* control, int id, EndEffectorType type) {
    control->id = id;
    control->type = type;
}

void activateEndEffector(MarkControl* control) {
    printf("Activating End Effector ID %d of type %d\n", control->id, control->type);
    // Add specific activation code based on the type
    switch (control->type) {
        case GRIPPER:
            printf("Gripper activated\n");
            break;
        case SUCTION_CUP:
            printf("Suction cup activated\n");
            break;
        case WELDER:
            printf("Welder activated\n");
            break;
        case PAINT_BRUSH:
            printf("Paint brush activated\n");
            break;
        case DRILL:
            printf("Drill activated\n");
            break;
        case SCREWDRIVER:
            printf("Screwdriver activated\n");
            break;
        case HAMMER:
            printf("Hammer activated\n");
            break;
        case VACUUM:
            printf("Vacuum activated\n");
            break;
        case LIGHT:
            printf("Light activated\n");
            break;
        case CAMERA:
            printf("Camera activated\n");
            break;
        case LASER:
            printf("Laser activated\n");
            break;
        case CUTTER:
            printf("Cutter activated\n");
            break;
        default:
            printf("Unknown end effector type\n");
            break;
    }
}

void deactivateEndEffector(MarkControl* control) {
    printf("Deactivating End Effector ID %d\n", control->id);
    // Add specific deactivation code based on the type
}

int main() {
    MarkControl control1;
    initMarkControl(&control1, 1, GRIPPER);
    activateEndEffector(&control1);

    MarkControl control2;
    initMarkControl(&control2, 2, PAINT_BRUSH);
    activateEndEffector(&control2);

    return 0;
}
