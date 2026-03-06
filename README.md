# Franka FR3 MoveIt Task Constructor based Playground

Franka Arm을 이용한 Manipulation Task 작업을 위해 제작한 Playground 패키지

## Features

- Table 위에 Cup, Figure와 이를 집어서(Pick) 담을(Place) Bascket가 존재하는 Gazebo Ignition 기반 환경 실행
- URDF로 구성된 Franka FR3 (with Gripper)이 환경 내에서 스폰되어서 MoveIt2 기반으로 Plan & Control 기능
- MoveIt Task Constructor를 기반으로 Pick n Place와 같은 Task 수행을 위한 로직

## Prerequisites

- ROS 2 Humble
- MoveIt 2
- Gazebo Ignition
- Docker CE (Optional : DevContainer)

## Installation

```bash

# Clone the repository
git clone https://github.com/Khyst/franka_fr3_mtc_playground <my_project_ws>

# locate to the project working directory
cd my_project_ws

# Container 열기
DOCKER_IMAGE=humble-release docker compose run cpu

# rosdep을 통한 의존성 패키지 설치 (Docker 컨테이너 내에서)
rosdep init
rosdep update
rosdep install --from-paths src --ignore-src y

# 빌드하기
colcon build --symlink-install

# 빌드한 환경 최종 소싱 작업
source ~/.bashrc

```

## Usage (작성중)

```bash
# Source the workspace
source install/setup.bash

# Run the simulation bringup (Gazebo Ignition 실행)
ros2 launch franka_fr3_bringup fr3_gazebo_bringup.launch.py

# Run MoveIt (MoveIt2 실행)
ros2 launch franka_fr3_moveit_config fr3_move_group.launch.py

# Run the MoveIt Task Constructor Demo (Custom(cup and figure pick n place)으로 제작된 MTC 로직 실행)
ros2 launch learn_mtc learn_mtc_run.launch.py
```

## Trouble Shooting

- Container 내에서 실행파일을 실행했을 때 GUI(RViz)등의 화면이 나오지 않을 경우
    - 호스트 터미널에서 아래 명령어를 입력하여서 X 서버 접근 권한을 허용해보자
    ``` xhost +local:docker ```
