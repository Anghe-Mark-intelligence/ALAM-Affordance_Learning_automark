#https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark
import logging
import gym
import numpy as np
import random
import threading
import time
from robot_io.utils.utils import pos_orn_to_matrix

# Configure logging format
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

log = logging.getLogger(__name__)

# State evaluation module
class StateEvaluator:
    def __init__(self):
        self.success_threshold = 0.9  # Set success threshold

    def evaluate_state(self, robot_obs):
        tcp_pos = robot_obs["tcp_pos"]
        gripper_width = robot_obs["gripper_opening_width"]
        # Evaluate if the robot's state is normal
        if gripper_width < 0.01:
            log.warning("Gripper is almost completely closed, may cause failure!")
        if np.linalg.norm(tcp_pos) > 2.0:
            log.warning("TCP position exceeds safe range!")

# Task management module
class TaskManager:
    def __init__(self):
        self.tasks = {"drawer": {"pos": np.array([0, 0, 0]), "orn": np.array([0, 0, 0])}}

    def set_task(self, task_name, target_pos, target_orn):
        if task_name not in self.tasks:
            self.tasks[task_name] = {"pos": target_pos, "orn": target_orn}
        else:
            self.tasks[task_name]["pos"] = target_pos
            self.tasks[task_name]["orn"] = target_orn

    def get_task(self, task_name):
        return self.tasks.get(task_name, None)

# MARKEnvE class
class MARKEnvE(gym.Wrapper):
    def __init__(
        self,
        env,
        d_pos,
        d_rot,
        gripper_success_width,
        gripper_success_displacement,
        reward_fail,
        reward_success,
        termination_radius,
        offset,
        *args,
        **kwargs,
    ):
        super().__init__(env)
        self.d_pos = d_pos
        self.d_rot = d_rot
        self.gripper_success_width = gripper_success_width
        self.reward_fail = reward_fail
        self.reward_success = reward_success
        self.termination_radius = termination_radius
        self.offset = np.array([*offset, 1])
        self.gripper_success_displacement = np.array([*gripper_success_displacement, 1])
        self._task = "drawer"
        self._target_orn = np.array([-2.26, 0.05, -0.12])

        # To track success of episode
        self._target_pos = None
        self.init_task_pos = None
        self.gripper_success_displacement = gripper_success_displacement

        self.task_manager = TaskManager()  # Initialize the task manager
        self.state_evaluator = StateEvaluator()  # Initialize the state evaluator
        self.max_retries = 5  # Maximum retry attempts

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, value):
        self._task = value

    @property
    def target_orn(self):
        return self._target_orn

    @property
    def target_pos(self):
        return self._target_pos

    @target_pos.setter
    def target_pos(self, value):
        self._target_pos = value

    def reset(self, target_pos=None, target_orn=None):
        self.env.robot.open_gripper()
        if target_pos is not None and target_orn is not None:
            self.target_pos = target_pos
            self.init_task_pos = target_pos
            tcp_mat = pos_orn_to_matrix(target_pos, target_orn)
            # Offset in gripper frame
            offset_global_frame = tcp_mat @ self.offset
            move_to = offset_global_frame[:3]
        else:
            move_to = target_pos
        return self.transform_obs(self.env.reset(move_to, target_orn))

    def check_success(self, robot_obs):
        gripper_width = robot_obs["gripper_opening_width"]
        holding_obj = gripper_width > self.gripper_success_width

        tcp_pos = robot_obs["tcp_pos"]
        tcp_orn = robot_obs["tcp_orn"]
        T_world_tcp = pos_orn_to_matrix(tcp_pos, tcp_orn)

        # Initial position in end effector frame coords
        _initial_pos = np.array([*self.init_task_pos, 1])
        rel_disp_from_aff = -np.linalg.inv(T_world_tcp) @ _initial_pos
        moved_thresh_dist = rel_disp_from_aff[-1] >= self.gripper_success_displacement[-1]

        return holding_obj and moved_thresh_dist

    def check_termination(self, current_pos):
        return np.linalg.norm(self.target_pos - current_pos) > self.termination_radius

    def step(self, action, move_to_box=False):
        assert len(action) == 4

        rel_target_pos = np.array(action[:3]) * self.d_pos
        rel_target_orn = np.array([0, 0, 0])
        gripper_action = action[-1]

        action = {"motion": (rel_target_pos, rel_target_orn, gripper_action), "ref": "rel"}

        obs, reward, done, info = self.env.step(action)
        info["success"] = False
        done = self.check_termination(obs["robot_state"]["tcp_pos"])
        if done:
            reward = self.reward_fail
            info["failure_case"] = "outside_radius"
            print("outside_radius")

        if self.check_success(obs["robot_state"]):
            reward = self.reward_success
            info["success"] = True
            done = True
            print("success")
        obs = self.transform_obs(obs)
        
        # State evaluation
        self.state_evaluator.evaluate_state(obs["robot_state"])

        return obs, reward, done, info

    def get_obs(self):
        return self.transform_obs(self.env._get_obs())

    @staticmethod
    def transform_obs(obs):
        robot_obs = obs["robot_state"]
        obs["robot_obs"] = np.concatenate([robot_obs["tcp_pos"], [robot_obs["gripper_opening_width"]]])
        del obs["robot_state"]
        return obs

    def retry_action(self, action):
        retries = 0
        while retries < self.max_retries:
            obs, reward, done, info = self.step(action)
            if done:  # Exit if successful
                return obs, reward, done, info
            retries += 1
            log.warning(f"Retry attempt {retries}...")
        return obs, reward, done, info  # Return failure after max retries

    def dynamic_task(self):
        # Simulate dynamic task change: randomly generate target position and orientation
        new_target_pos = np.array([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0.5])
        new_target_orn = np.array([random.uniform(-np.pi, np.pi), 0, 0])
        self.task_manager.set_task("dynamic_task", new_target_pos, new_target_orn)

    def set_new_task(self, task_name, target_pos, target_orn):
        self.task_manager.set_task(task_name, target_pos, target_orn)
