//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main/Robot_armcontrol
#include <iostream>
#include <deque>
#include <vector>

using namespace std;

class MeanFilter {
public:
    MeanFilter(int window_size) : window_size(window_size) {
        // Initialize the sliding window
        window.resize(window_size, 0.0);  // Start with all zeros
    }

    // Function to add a new measurement and compute the moving average
    double update(double new_measurement) {
        // Remove the oldest measurement if the window is full
        if (window.size() >= window_size) {
            window.pop_front();
        }

        // Add the new measurement to the window
        window.push_back(new_measurement);

        // Compute the moving average (mean) of the window
        double sum = 0.0;
        for (double val : window) {
            sum += val;
        }

        return sum / window.size();  // Return the average
    }

private:
    int window_size;       // Size of the sliding window
    deque<double> window;  // Store the measurements in a deque (efficient for pop and push operations)
};

int main() {
    // Initialize the MeanFilter with a window size of 5
    MeanFilter filter(5);

    // Simulate some noisy position data from the robotic arm
    vector<double> noisy_positions = {10.0, 10.5, 11.2, 10.7, 11.0, 11.5, 12.0, 12.2, 11.8, 12.1};

    // Process each noisy measurement through the filter
    cout << "Filtered Position Data (Moving Average):" << endl;
    for (double noisy_position : noisy_positions) {
        // Update the filter with the noisy position and get the filtered position
        double filtered_position = filter.update(noisy_position);

        // Output the noisy position and the filtered position
        cout << "Noisy: " << noisy_position << " -> Filtered: " << filtered_position << endl;
    }

    return 0;
}
