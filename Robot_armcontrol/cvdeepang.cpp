#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>

int main() {
    // Open the default camera (index 0), or change to another index for other cameras
    cv::VideoCapture cap(0);

    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera!" << std::endl;
        return -1;
    }

    // Set the width and height of the camera capture frame
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    // Create a matrix to store frames
    cv::Mat frame, grayFrame, depthMap;

    // For depth capture, we use a stereo camera or a depth camera.
    // In this case, we will use a simulated depth map for simplicity.
    while (true) {
        // Capture the frame from the camera
        cap >> frame;

        if (frame.empty()) {
            std::cerr << "Error: Captured empty frame!" << std::endl;
            break;
        }

        // Convert the frame to grayscale for depth estimation (if necessary)
        cv::cvtColor(frame, grayFrame, cv::COLOR_BGR2GRAY);

        // Simulate a simple depth map by applying a "depth-like" effect (for demonstration)
        // In real use, this is where you'd retrieve depth data from a stereo camera or depth sensor
        cv::applyColorMap(grayFrame, depthMap, cv::COLORMAP_JET);

        // Display the original frame in a window titled "Original Frame"
        cv::imshow("Original Frame", frame);

        // Display the depth map in a window titled "Depth Map"
        cv::imshow("Depth Map", depthMap);

        // Wait for a key press for 1 millisecond. If the 'Esc' key is pressed, break the loop.
        char key = cv::waitKey(1);
        if (key == 27) {  // 27 is the ASCII value for the ESC key
            break;
        }
    }

    // Release the camera and close all OpenCV windows
    cap.release();
    cv::destroyAllWindows();

    return 0;
}
