//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main/AIAM
#include <gtk/gtk.h>
#include <opencv2/opencv.hpp>
#include <stdio.h>

// Define the MarkControl class and end effector types
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
    int id;  
    EndEffectorType type;
} MarkControl;

void initMarkControl(MarkControl* control, int id, EndEffectorType type) {
    control->id = id;
    control->type = type;
}

void activateEndEffector(MarkControl* control) {
    printf("Activating End Effector ID %d of type %d\n", control->id, control->type);
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

// OpenCV serial port setup and camera handling
cv::VideoCapture cap(1);  // Open camera on serial port 1 (assuming camera ID 1)

void on_draw(GtkWidget *widget, cairo_t *cr, gpointer user_data) {
    if (cap.isOpened()) {
        cv::Mat frame;
        cap >> frame;  // Capture a frame

        if (!frame.empty()) {
            // Convert to a format supported by GTK
            cv::Mat rgb_frame;
            cv::cvtColor(frame, rgb_frame, cv::COLOR_BGR2RGB);
            GdkPixbuf *pixbuf = gdk_pixbuf_new_from_data((guchar*)rgb_frame.data,
                                                        GDK_COLORSPACE_RGB, FALSE, 8,
                                                        rgb_frame.cols, rgb_frame.rows,
                                                        rgb_frame.step, NULL, NULL);

            // Draw the image
            gdk_cairo_set_source_pixbuf(cr, pixbuf, 0, 0);
            cairo_paint(cr);
            g_object_unref(pixbuf);
        }
    }
}

static void on_end_effector_changed(GtkComboBox *widget, gpointer user_data) {
    MarkControl *control = (MarkControl*)user_data;
    control->type = (EndEffectorType)gtk_combo_box_get_active(widget) + 1;
    activateEndEffector(control);  // Activate the selected end effector
}

int main(int argc, char *argv[]) {
    gtk_init(&argc, &argv);

    // Create GTK window
    GtkWidget *window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Robotic Arm Control");
    gtk_window_set_default_size(GTK_WINDOW(window), 800, 600);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    // Create drawing area for video display
    GtkWidget *drawing_area = gtk_drawing_area_new();
    gtk_container_add(GTK_CONTAINER(window), drawing_area);
    g_signal_connect(drawing_area, "draw", G_CALLBACK(on_draw), NULL);

    // Create a drop-down menu for selecting the end effector
    GtkWidget *combo_box = gtk_combo_box_text_new();
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Gripper");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Suction Cup");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Welder");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Paint Brush");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Drill");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Screwdriver");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Hammer");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Vacuum");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Light");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Camera");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Laser");
    gtk_combo_box_text_append_text(GTK_COMBO_BOX_TEXT(combo_box), "Cutter");
    gtk_container_add(GTK_CONTAINER(window), combo_box);
    g_signal_connect(combo_box, "changed", G_CALLBACK(on_end_effector_changed), NULL);

    // Initialize MarkControl with a default "Gripper"
    MarkControl control;
    initMarkControl(&control, 1, GRIPPER);  // Default to "Gripper"

    // Show the window
    gtk_widget_show_all(window);

    // Start the GTK main loop
    gtk_main();

    // Release OpenCV resources
    cap.release();

    return 0;
}
