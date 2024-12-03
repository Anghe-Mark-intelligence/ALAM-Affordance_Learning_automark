#include <librealsense2/rs.hpp>
#include <opencv2/opencv.hpp>

int main() {
    // Initialize RealSense pipeline
    rs2::pipeline p;
    rs2::config cfg;
    cfg.enable_stream(RS2_STREAM_DEPTH);  // Enable depth stream
    cfg.enable_stream(RS2_STREAM_COLOR);  // Enable color stream

    p.start(cfg);

    cv::namedWindow("Original Frame", cv::WINDOW_AUTOSIZE);
    cv::namedWindow("Depth Map", cv::WINDOW_AUTOSIZE);

    while (true) {
        // Wait for the next set of frames
        rs2::frameset frames = p.wait_for_frames();

        // Get the color and depth frames
        rs2::frame color_frame = frames.get_color_frame();
        rs2::depth_frame depth_frame = frames.get_depth_frame();

        // Convert RealSense frame to OpenCV format
        int width = color_frame.as<rs2::video_frame>().get_width();
        int height = color_frame.as<rs2::video_frame>().get_height();

        // Create OpenCV matrix from RealSense color and depth frames
        cv::Mat color_mat(cv::Size(width, height), CV_8UC3, (void*)color_frame.get_data(), cv::Mat::AUTO_STEP);
        cv::Mat depth_mat(cv::Size(width, height), CV_16UC1, (void*)depth_frame.get_data(), cv::Mat::AUTO_STEP);

        // Normalize depth data for display
        cv::Mat depth_display;
        depth_mat.convertTo(depth_display, CV_8UC1, 255.0 / 10000.0);  // Adjust the depth range

        // Show the original color frame and depth frame
        cv::imshow("Original Frame", color_mat);
        cv::imshow("Depth Map", depth_display);

        // Wait for key press (exit on ESC)
        if (cv::waitKey(1) == 27) {
            break;
        }
    }

    cv::destroyAllWindows();
    return 0;
}
