#https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark
import logging
import math
import time

import gym
import numpy as np


log = logging.getLogger(__name__)  # Set up logging

# Constants for gripper operations
WAIT_AFTER_GRIPPER_CLOSE = 1  # Time to wait after closing gripper
WAIT_FOR_WIDTH_MEASUREMENT = 1  # Time to wait for gripper width measurement
MOVE_UP_AFTER_GRASP = 0.03  # Move up after grasping the object
GRIPPER_SUCCESS_THRESHOLD = 0.01  # Success threshold for gripper width
GRIPPER_WIDTH_FAIL = 0.075  # Threshold for gripper failure
MAX_FAIL_COUNT = 5  # Maximum failure count before resetting the task

class MARKEnvE(gym.Wrapper):
    def __init__(
        self,
        env,
        d_pos,
        d_rot,
        gripper_success_threshold,
        reward_fail,
        reward_success,
        termination_radius,
        offset,
        *args,
        **kwargs,
    ):
        super().__init__(env)  # Initialize the gym wrapper
        self.d_pos = d_pos  # Scaling factor for position changes
        self.d_rot = d_rot  # Scaling factor for rotation changes
        self.gripper_success_threshold = gripper_success_threshold  # Threshold for successful gripper action
        self.reward_fail = reward_fail  # Reward for failure
        self.reward_success = reward_success  # Reward for success
        self.termination_radius = termination_radius  # Distance threshold for termination
        self.target_pos = None  # Target position for the task
        self.offset = offset["pickup"]  # Offset for task (pickup)
        self.task = "pickup"  # Default task is pickup
        self.start_orn = np.array([math.pi, 0, 0])  # Default orientation (rotation)
        if "box_pos" in kwargs:  # If box position is given in kwargs
            self.box_pos = kwargs["box_pos"]  # Get box position
            self.box_3D_end_points = get_3D_end_points(*self.box_pos, *kwargs["box_dims"])  # Get 3D box end points
        self.fail_count = 0  # Count consecutive failures
        self.task_history = []  # Record of task history for learning

    @property
    def task(self):  # Getter for task property
        return self._task

    @task.setter
    def task(self, value):  # Setter for task property
        self._task = value

    def get_target_orn(self, task):  # Get target orientation for the task
        return self.start_orn  # Return default orientation

    def reset(self, target_pos=None, target_orn=None):  # Reset the environment
        self.env.robot.open_gripper()  # Open the gripper at the start
        if target_pos is not None and target_orn is not None:  # If target position and orientation are provided
            self.target_pos = target_pos  # Set the target position
            move_to = target_pos + self.offset[self.task]  # Apply the offset for the current task
        else:
            move_to = target_pos  # Only move to the target position if no orientation is given
        return self.transform_obs(self.env.reset(move_to, target_orn))  # Reset the environment and transform the observation

    def check_success(self):  # Check if the gripper successfully grasped the object
        time.sleep(WAIT_AFTER_GRIPPER_CLOSE)  # Wait for the gripper to close
        pos, orn = self.env.robot.get_tcp_pos_orn()  # Get the robot's TCP position and orientation
        pos[2] += MOVE_UP_AFTER_GRASP  # Move the object up slightly after grasping
        self.env.robot.move_async_cart_pos_abs_lin(pos, orn)  # Move the robot asynchronously
        time.sleep(WAIT_FOR_WIDTH_MEASUREMENT)  # Wait for the gripper width measurement
        gripper_width = self.env.robot.get_state()["gripper_opening_width"]  # Get the gripper width
        if gripper_width > GRIPPER_WIDTH_FAIL:  # If the gripper width is too large, the action failed
            log.error("Gripper action seems to have no effect.")  # Log an error
            raise Exception  # Raise an exception indicating failure
        return gripper_width > self.gripper_success_threshold  # Return success if gripper width is within the threshold

    def move_to_box(self):  # Move the robot to the box position
        box_pos = self.box_pos  # Get the box position
        pos, orn = self.env.robot.get_tcp_pos_orn()  # Get the current TCP position and orientation
        pos[2] = box_pos[-1] + MOVE_UP_AFTER_GRASP * 2  # Set the Z position above the box
        self.env.robot.move_cart_pos_abs_ptp(pos, orn)  # Move the robot to the position above the box
        time.sleep(WAIT_FOR_WIDTH_MEASUREMENT)  # Wait for the gripper width measurement
        self.env.robot.move_cart_pos_abs_ptp(box_pos, orn)  # Move the robot to the box position
        self.env.robot.open_gripper(blocking=True)  # Open the gripper to place the object

    def put_back_object(self):  # Put the object back
        pos, orn = self.env.robot.get_tcp_pos_orn()  # Get the current TCP position and orientation
        pos[2] -= MOVE_UP_AFTER_GRASP * 0.8  # Lower the robot slightly
        self.env.robot.move_async_cart_pos_abs_lin(pos, orn)  # Move the robot asynchronously
        self.env.robot.open_gripper(blocking=True)  # Open the gripper to release the object

    def check_termination(self, current_pos):  # Check if the task is complete
        return np.linalg.norm(self.target_pos - current_pos) > self.termination_radius  # Check if the target is within the termination radius

    def step(self, action, move_to_box=False):  # Perform a step in the environment
        assert len(action) == 5  # Ensure the action has the correct length

        rel_target_pos = np.array(action[:3]) * self.d_pos  # Calculate relative position change
        rel_target_orn = np.array([0, 0, action[3]]) * self.d_rot  # Calculate relative orientation change
        gripper_action = action[-1]  # Gripper action

        curr_pos = self.env.robot.get_tcp_pos_orn()[0]  # Get current TCP position
        depth_thresh = curr_pos[-1] <= self.env.workspace_limits[0][-1] + 0.01  # Check if depth is within limits
        if depth_thresh:  # If the depth is below threshold
            print("depth threshold reached")
            gripper_action = -1  # Set gripper action to -1 for depth threshold condition

        action = {"motion": (rel_target_pos, rel_target_orn, gripper_action), "ref": "rel"}  # Create action dictionary

        obs, reward, done, info = self.env.step(action)  # Execute the action and get the observation

        info["success"] = False  # Initialize success flag as False

        if gripper_action == -1:  # If gripper action is -1, it indicates a failed grasp
            done = True  # End the episode
            if self.check_success():  # Check if the grasp was successful
                reward = self.reward_success  # Assign success reward
                info["success"] = True  # Set success flag
                if move_to_box:  # If moving to box is requested
                    self.move_to_box()  # Move the object to the box
                else:
                    self.put_back_object()  # Otherwise, put the object back
            else:
                reward = self.reward_fail  # Assign failure reward
                info["failure_case"] = "failed_grasp"  # Log failure case
                self.fail_count += 1  # Increment failure count
        else:  # If the gripper action is not -1, check if the task is completed
            done = self.check_termination(obs["robot_state"]["tcp_pos"])  # Check if the task is terminated
            if done:  # If terminated, assign failure reward
                reward = self.reward_fail
                info["failure_case"] = "outside_radius"
                self.fail_count += 1  # Increment failure count

        # If failure count exceeds max allowed, reset task
        if self.fail_count > MAX_FAIL_COUNT:
            self.reset()  # Reset the environment
            reward = self.reward_fail  # Assign failure reward
            info["failure_case"] = "max_fail_count_reached"
            self.fail_count = 0  # Reset failure count

        return self.transform_obs(obs), reward, done, info  # Return the updated observation, reward, done flag, and info

    def transform_obs(self, obs):  # Transform observation
        return obs  # Return transformed observation
