//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main
#include <iostream>
#include <vector>
#include <string>

class RobotArm {
private:
    bool manualMode;
    bool onlineMode;
    bool offlineMode;
    bool recording;
    bool replaying;
    std::vector<std::string> trajectory;

public:
    RobotArm()
        : manualMode(false), onlineMode(false), offlineMode(true), recording(false), replaying(false) {}

    // Switch to manual mode
    void manual_mode() {
        manualMode = true;
        onlineMode = false;
        offlineMode = false;
        std::cout << "Switched to Manual Mode.\n";
    }

    // Switch to online mode
    void online_mode() {
        manualMode = false;
        onlineMode = true;
        offlineMode = false;
        std::cout << "Switched to Online Mode.\n";
    }

    // Switch to offline mode
    void offline_mode() {
        manualMode = false;
        onlineMode = false;
        offlineMode = true;
        std::cout << "Switched to Offline Mode.\n";
    }

    // Start recording trajectory
    void record_start() {
        if (recording) {
            std::cout << "Already recording. Stop recording before starting again.\n";
            return;
        }
        recording = true;
        trajectory.clear();
        std::cout << "Recording started. Add points to the trajectory.\n";
    }

    // Stop recording trajectory
    void record_stop() {
        if (!recording) {
            std::cout << "Not recording. Start recording before stopping.\n";
            return;
        }
        recording = false;
        std::cout << "Recording stopped.\n";
    }

    // Start replaying recorded trajectory
    void replay_start() {
        if (trajectory.empty()) {
            std::cout << "No trajectory recorded to replay.\n";
            return;
        }
        replaying = true;
        std::cout << "Replaying recorded trajectory...\n";
        for (const auto& point : trajectory) {
            std::cout << "Moving to: " << point << "\n";
        }
        replaying = false;
        std::cout << "Replay finished.\n";
    }

    // Function to simulate adding points to the trajectory while recording
    void add_trajectory_point(const std::string& point) {
        if (recording) {
            trajectory.push_back(point);
            std::cout << "Added point to trajectory: " << point << "\n";
        } else {
            std::cout << "Not recording. Start recording before adding points.\n";
        }
    }
};

int main() {
    RobotArm arm;

    arm.manual_mode();       // Switch to manual mode
    arm.record_start();      // Start recording trajectory
    arm.add_trajectory_point("Point 1");
    arm.add_trajectory_point("Point 2");
    arm.record_stop();       // Stop recording trajectory

    arm.online_mode();      // Switch to online mode
    arm.replay_start();     // Start replaying recorded trajectory

    arm.offline_mode();     // Switch to offline mode

    return 0;
}
