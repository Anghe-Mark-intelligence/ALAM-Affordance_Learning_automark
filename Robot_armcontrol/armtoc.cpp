//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main/Robot_armcontrol
#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <Eigen/Dense> // For matrix calculations

using namespace cv;
using namespace std;

// 6 DOF Robot Arm Transformation Matrix (for simplicity, using a mock 6-DOF arm)
struct RobotArm {
    // Define the 6-DOF robot transformation matrix here
    Eigen::Matrix4d getEndEffectorPose() {
        Eigen::Matrix4d pose = Eigen::Matrix4d::Identity();
        // Modify this function to return the actual pose based on robot's joint positions
        return pose;
    }
};

// Tsai-Lenz Hand-Eye Calibration Algorithm (simplified)
Eigen::Matrix4d handEyeCalibration(const vector<Eigen::Matrix4d>& robotPoses, const vector<Eigen::Matrix4d>& cameraPoses) {
    // Implement the Tsai-Lenz algorithm for hand-eye calibration
    // This function should return the transformation matrix that relates camera to robot
    Eigen::Matrix4d transformation = Eigen::Matrix4d::Identity();
    
    // A mock implementation for the example:
    // Normally, this should be based on the optimization algorithm of Tsai-Lenz
    
    return transformation;
}

// Function to detect chessboard and extract corners
bool detectChessboard(const Mat& image, vector<Point2f>& corners) {
    Size boardSize(9, 6);  // Chessboard size: 9x6 squares
    bool found = findChessboardCorners(image, boardSize, corners,
                                       CALIB_CB_ADAPTIVE_THRESH | CALIB_CB_FAST_CHECK | CALIB_CB_NORMALIZE_IMAGE);

    if (found) {
        // Refine corner positions for better accuracy
        cornerSubPix(image, corners, Size(11, 11), Size(-1, -1), TermCriteria(TermCriteria::EPS | TermCriteria::MAX_ITER, 30, 0.1));
    }
    
    return found;
}

void visualizeCameraFeed(Mat& frame, const vector<Point2f>& corners) {
    // Draw the chessboard corners on the camera feed
    drawChessboardCorners(frame, Size(9, 6), corners, true);
    imshow("Camera Feed", frame);
    waitKey(1); // Refresh the window
}

int main() {
    // Initialize the robot arm (Mock 6-DOF arm)
    RobotArm robot;

    // Initialize the camera
    VideoCapture cap(0); // Open the default camera
    if (!cap.isOpened()) {
        cerr << "Error opening video stream" << endl;
        return -1;
    }

    vector<Eigen::Matrix4d> robotPoses;
    vector<Eigen::Matrix4d> cameraPoses;
    vector<Point2f> corners;

    while (true) {
        Mat frame;
        cap >> frame; // Capture a frame from the camera
        if (frame.empty()) break;

        // Detect chessboard corners
        if (detectChessboard(frame, corners)) {
            visualizeCameraFeed(frame, corners);

            // Get robot pose (from robot arm)
            Eigen::Matrix4d robotPose = robot.getEndEffectorPose();

            // Simulate a camera pose (based on some assumed data; replace this with actual pose calculation)
            Eigen::Matrix4d cameraPose = Eigen::Matrix4d::Identity();
            // Here, we assume that camera pose changes based on chessboard detection (replace with actual camera pose computation)

            // Store the poses for hand-eye calibration
            robotPoses.push_back(robotPose);
            cameraPoses.push_back(cameraPose);

            // Once enough data is gathered, compute the hand-eye calibration
            if (robotPoses.size() >= 5) {  // We need at least 5 poses for a good result
                Eigen::Matrix4d transformation = handEyeCalibration(robotPoses, cameraPoses);
                cout << "Transformation Matrix (Camera to Robot End Effector): \n" << transformation << endl;
                break;  // Exit after calibration
            }
        }

        // Press 'q' to exit
        if (waitKey(1) == 'q') break;
    }

    cap.release();
    destroyAllWindows();

    return 0;
}
