#!/bin/bash
#set -e # 에러 발생 시 즉시 중단

# 매크로
add_to_bashrc() {
    local line="$1"
    if ! grep -qF "$line" ~/.bashrc; then
        echo "$line" >> ~/.bashrc
    fi
}

cd /root/ws_moveit

# 시스템 업데이트 (컨테이너 내부이므로 sudo 제외)
apt update && apt upgrade -y

# 필수 도구 설치
apt install -y \
    git gedit nano vim curl wget build-essential \
    python3-colcon-common-extensions \
    python3-rosdep

# Git 소유권 예외 등록 (중요: dubious ownership 에러 방지)
git config --global --add safe.directory /root/ws_moveit

# Gazebo Ignition이 설치 (ROS2 humble 기준 Gazebo Ignition)
sudo apt-get install -y ros-humble-ros-gz

# Franka Arm 관련 의존성 설치
sudo apt install -y ros-humble-libfranka ros-humble-franka-msgs

# 파일이 없을 때만 init을 실행하거나, 이미 있어도 에러를 무시하고 넘어감
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    rosdep init
else
    echo "rosdep is already initialized, skipping 'rosdep init'..."
fi

rosdep update
rosdep install --from-paths src --ignore-src -y
# ------------------------------

# 빌드하기
colcon build --symlink-install

# Bashrc 설정 추가
add_to_bashrc "source /opt/ros/humble/setup.bash"

# 빌드 결과물이 있을 때만 source 하도록 설정 (에러 방지)
add_to_bashrc "[ -f /root/ws_moveit/install/setup.bash ] && source /root/ws_moveit/install/setup.bash"

# 통신 및 Alias 설정
add_to_bashrc "export ROS_DOMAIN_ID=42"
add_to_bashrc "export ROS_LOCALHOST_ONLY=0"
add_to_bashrc "alias sb='source ~/.bashrc'"
add_to_bashrc "alias rosdep_install='rosdep install --from-paths src --ignore-src -y'"
add_to_bashrc "alias cb='colcon build --symlink-install'"
add_to_bashrc "alias cbp='colcon build --symlink-install --packages-select'"

add_to_bashrc "alias fr_world='ros2 launch franka_fr3_bringup fr3_gazebo_bringup.launch.py'"
add_to_bashrc "alias fr_moveit='ros2 launch franka_fr3_moveit_config fr3_move_group.launch.py'"
add_to_bashrc "alias f1='ros2 launch learn_mtc learn_mtc_run_cup_without_reset_world.launch.py'"
add_to_bashrc "alias f2='ros2 launch learn_mtc learn_mtc_run_figure_without_reset_world.launch.py'"
add_to_bashrc "alias reset='python3 /root/ws_moveit/src/learn_mtc/scripts/reset_gz_world.py'"

echo "Setup complete! Please restart your terminal or run 'source ~/.bashrc' to apply the changes."