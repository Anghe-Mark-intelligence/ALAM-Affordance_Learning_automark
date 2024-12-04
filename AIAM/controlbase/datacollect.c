#include <stdio.h>
#include <stdlib.h>
#include <opencv2/opencv.hpp>
#include <string.h>
#include <time.h>

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
}

// Function to capture and save camera video
void captureCameraVideo(cv::VideoCapture *cap, const char* filename) {
    cv::Mat frame;
    cv::VideoWriter writer(filename, cv::VideoWriter::fourcc('M', 'J', 'P', 'G'), 30, cv::Size(640, 480));

    if (!cap->isOpened()) {
        printf("Error: Could not open camera.\n");
        return;
    }

    printf("Recording video from camera...\n");
    while (true) {
        *cap >> frame;
        if (frame.empty()) break;

        writer.write(frame);  // Write the frame to video file
        cv::imshow("Camera Feed", frame);

        if (cv::waitKey(30) >= 0) break; // Exit on key press
    }
    writer.release();
    cv::destroyAllWindows();
    printf("Video saved to %s\n", filename);
}

// Function to collect data (real or simulated)
void collectData(const char* mode) {
    FILE *file;
    time_t t;
    time(&t);

    // Open appropriate file based on mode
    if (strcmp(mode, "real") == 0) {
        file = fopen("real_date.txt", "a");
    } else if (strcmp(mode, "sim") == 0) {
        file = fopen("sim_date.txt", "a");
    } else {
        printf("Invalid mode selected.\n");
        return;
    }

    if (file == NULL) {
        printf("Error opening file.\n");
        return;
    }

    // Collect data: You can simulate trajectory data here
    fprintf(file, "Timestamp: %s\n", ctime(&t));
    fprintf(file, "End Effector ID: %d, Type: %d\n", 1, GRIPPER);
    fprintf(file, "Trajectory: (0, 0, 0) -> (10, 10, 10)\n\n");

    fclose(file);
    printf("Data collected successfully.\n");
}

// Menu for user to choose between real and simulated data collection
void showMenu() {
    int choice;
    printf("Select data collection mode:\n");
    printf("1. Real Data\n");
    printf("2. Simulated Data\n");
    printf("0. Exit\n");
    printf("Enter your choice: ");
    scanf("%d", &choice);

    if (choice == 1) {
        collectData("real");
    } else if (choice == 2) {
        collectData("sim");
    } else if (choice == 0) {
        printf("Exiting program...\n");
        return;
    } else {
        printf("Invalid choice. Please try again.\n");
    }
}

int main() {
    // Initialize OpenCV camera
    cv::VideoCapture cap(1); // Open camera at COM1 (Device ID = 1)
    
    // Capture video
    captureCameraVideo(&cap, "captured_video.avi");

    // Show the menu for collecting data
    while (1) {
        showMenu();
    }

    return 0;
}
