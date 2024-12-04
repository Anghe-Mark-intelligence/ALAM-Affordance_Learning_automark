//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main
#include <ros/ros.h>
#include <sensor_msgs/JointState.h>
#include <sensor_msgs/Image.h>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <QtWidgets/QApplication>
#include <QtWidgets/QWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QLabel>
#include <QtCore/QTimer>

class RobotArmVisualizer : public QWidget {
    Q_OBJECT

public:
    RobotArmVisualizer(ros::NodeHandle& nh, QWidget* parent = nullptr)
        : QWidget(parent), nh_(nh) {
        // Setup GUI components
        jointStateLabel_ = new QLabel("Joint States: ", this);
        depthImageLabel_ = new QLabel("Depth Image: ", this);
        QVBoxLayout* layout = new QVBoxLayout(this);
        layout->addWidget(jointStateLabel_);
        layout->addWidget(depthImageLabel_);

        // Timer to update the UI
        updateTimer_ = new QTimer(this);
        connect(updateTimer_, &QTimer::timeout, this, &RobotArmVisualizer::updateGUI);
        updateTimer_->start(100);  // Update every 100ms

        // Initialize ROS subscribers
        jointStateSubscriber_ = nh_.subscribe("/joint_states", 10, &RobotArmVisualizer::jointStateCallback, this);
        depthImageSubscriber_ = nh_.subscribe("/camera/depth/image_raw", 10, &RobotArmVisualizer::depthImageCallback, this);
    }

private slots:
    // Callback for joint states
    void jointStateCallback(const sensor_msgs::JointState::ConstPtr& msg) {
        jointStates_ = *msg;
        updateGUI();
    }

    // Callback for depth image
    void depthImageCallback(const sensor_msgs::Image::ConstPtr& msg) {
        try {
            // Convert ROS Image message to OpenCV format
            cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::TYPE_16UC1);
            depthImage_ = cv_ptr->image;
        }
        catch (cv_bridge::Exception& e) {
            ROS_ERROR("Could not convert from '%s' to '16UC1'.", msg->encoding.c_str());
        }
    }

    // Update the GUI components with new data
    void updateGUI() {
        // Display joint states
        if (jointStates_.position.size() > 0) {
            QString jointStateText = "Joint States: ";
            for (size_t i = 0; i < jointStates_.position.size(); ++i) {
                jointStateText += QString("J%1: %2  ").arg(i+1).arg(jointStates_.position[i]);
            }
            jointStateLabel_->setText(jointStateText);
        }

        // Display depth image
        if (!depthImage_.empty()) {
            cv::Mat displayImage;
            cv::normalize(depthImage_, displayImage, 0, 255, cv::NORM_MINMAX);
            displayImage.convertTo(displayImage, CV_8UC1); // Convert to 8-bit for displaying
            QImage img(displayImage.data, displayImage.cols, displayImage.rows, displayImage.step, QImage::Format_Grayscale8);
            depthImageLabel_->setPixmap(QPixmap::fromImage(img));
        }
    }

private:
    ros::NodeHandle nh_;
    ros::Subscriber jointStateSubscriber_;
    ros::Subscriber depthImageSubscriber_;
    sensor_msgs::JointState jointStates_;
    cv::Mat depthImage_;
    QLabel* jointStateLabel_;
    QLabel* depthImageLabel_;
    QTimer* updateTimer_;
};

int main(int argc, char** argv) {
    // Initialize ROS
    ros::init(argc, argv, "robot_arm_visualizer");
    ros::NodeHandle nh;

    // Initialize Qt application
    QApplication app(argc, argv);
    RobotArmVisualizer window(nh);
    window.setWindowTitle("Robot Arm Visualizer");
    window.resize(800, 600);
    window.show();

    // Start the Qt event loop
    return app.exec();
}

#include "robot_arm_gui.moc"
