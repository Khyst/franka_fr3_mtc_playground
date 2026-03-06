# Project Name (e.g., franka_arm_playground)

A brief description of what this project does and who it's for.

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

List the software and dependencies required to use this project.
- ROS 2 Humble
- MoveIt 2
- Gazebo Ignition
- etc.

## Installation

Provide step-by-step instructions on how to build and install the project.

```bash
# Clone the repository
git clone https://github.com/username/project.git

# Navigate to the workspace
cd project_ws

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build the workspace
colcon build --symlink-install
```

## Usage

Provide instructions and examples on how to use the project.

```bash
# Source the workspace
source install/setup.bash

# Run the simulation bringup
ros2 launch franka_fr3_bringup fr3_gazebo_bringup.launch.py

# Run MoveIt
ros2 launch franka_fr3_moveit_config fr3_move_group.launch.py

# Run the MoveIt Task Constructor Demo
ros2 launch learn_mtc learn_mtc_run.launch.py
```

## Package Architecture

Briefly explain the structure of the packages within the workspace.
- `franka_fr3_description`: URDF and SRDF files for the FR3 robot.
- `franka_fr3_bringup`: Launch files for Gazebo simulation and ROS-Ignition bridge.
- `franka_fr3_moveit_config`: MoveIt 2 configuration files.
- `learn_mtc`: C++ node for running Pick and Place using MoveIt Task Constructor.

## License

This project is licensed under the [License Name] License - see the LICENSE file for details.