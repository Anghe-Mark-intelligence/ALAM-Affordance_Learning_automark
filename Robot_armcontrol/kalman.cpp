//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main/Robot_armcontrol
#include <iostream>
#include <Eigen/Dense>

using namespace std;
using namespace Eigen;

class KalmanFilter {
public:
    KalmanFilter() {
        // Initializing matrices (for a simple 2D state: position and velocity)
        A = Matrix2d::Identity();   // State transition matrix
        A(0, 1) = 1;  // Assuming velocity influences position

        H = MatrixXd(1, 2);   // Measurement matrix (1 measurement, 2 state variables)
        H << 1, 0;  // We measure the position

        Q = Matrix2d::Identity() * 0.01;  // Process noise covariance (tuning required)
        R = MatrixXd(1, 1);  // Measurement noise covariance
        R << 1;  // Assume a fixed measurement noise value

        P = Matrix2d::Identity() * 1000;  // Initial covariance (large initial uncertainty)

        x = Vector2d(0, 0);  // Initial state (position = 0, velocity = 0)
    }

    // Prediction step of the Kalman Filter
    void predict(Vector2d u) {
        // Predict state
        x = A * x + B * u;
        P = A * P * A.transpose() + Q;
    }

    // Update step of the Kalman Filter
    void update(double z) {
        // Compute Kalman Gain
        MatrixXd K = P * H.transpose() * (H * P * H.transpose() + R).inverse();

        // Update estimate with new measurement
        x = x + K * (z - H * x);

        // Update covariance estimate
        P = (Matrix2d::Identity() - K * H) * P;
    }

    // Get the current estimated state
    Vector2d getState() {
        return x;
    }

    // Set the measurement noise covariance (tuning parameter)
    void setMeasurementNoise(double noise) {
        R(0, 0) = noise;
    }

private:
    Matrix2d A;   // State transition matrix
    MatrixXd H;   // Measurement matrix
    Matrix2d Q;   // Process noise covariance
    MatrixXd R;   // Measurement noise covariance
    Matrix2d P;   // Estimate covariance
    Vector2d x;   // Current state estimate (position, velocity)
    Matrix2d B;   // Control matrix (optional)
};

int main() {
    // Create an instance of the Kalman filter
    KalmanFilter kf;

    // Simulate some noisy sensor data for position
    double real_position = 10.0;  // Real position of the robot (for example)
    double noise_level = 1.0;     // Simulated measurement noise
    double noisy_position = real_position + ((rand() % 100) / 100.0) * noise_level;

    // Print initial state estimate
    cout << "Initial state estimate (position, velocity): " << kf.getState().transpose() << endl;

    // Simulate robot's motion and process measurements
    for (int i = 0; i < 100; ++i) {
        // Predict the next state based on the current control input (no control here)
        kf.predict(Vector2d(0, 0));  // No control input for this example

        // Simulate noisy measurement
        noisy_position = real_position + ((rand() % 100) / 100.0) * noise_level;

        // Update Kalman filter with noisy measurement
        kf.update(noisy_position);

        // Output the estimated state (position and velocity)
        cout << "Estimated state (position, velocity) at step " << i << ": " << kf.getState().transpose() << endl;
    }

    return 0;
}
