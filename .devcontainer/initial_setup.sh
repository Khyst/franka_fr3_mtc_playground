#!/bin/bash
set -e # 에러 발생 시 즉시 중단

# 매크로 (1)
add_to_bashrc() {
    local line="$1"
    if ! grep -qF "$line" ~/.bashrc; then
        echo "$line" >> ~/.bashrc
    fi
}

# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools for ROS2 development
sudo apt install -y \
    git \
    gedit \
    nano \
    vim \
    curl \
    wget \
    build-essential \

# 작업 공간 setup 추가
add_to_bashrc "source /opt/ros/humble/setup.bash"
add_to_bashrc "source /root/ws_moveit/install/setup.bash"

# 통신 설정 (호스트 공유를 위한 필수 설정)
add_to_bashrc "export ROS_DOMAIN_ID=42"
add_to_bashrc "export ROS_LOCALHOST_ONLY=0"
# add_to_bashrc "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" # 필요 시 RMW 강제 설정 (통신 불량 시 CycloneDDS 권장)

# Alias 설정
add_to_bashrc "alias sb='source ~/.bashrc'"
add_to_bashrc "alias rosdep_install='rosdep install --from-paths src --ignore-src -y'"
add_to_bashrc "alias cb='colcon build --symlink-install'"
add_to_bashrc "alias cbm='colcon build --symlink-install --mixin release'"
add_to_bashrc "alias cbp='colcon build --symlink-install --packages-select'"
add_to_bashrc "alias cbpm='colcon build --symlink-install --packages-select --mixin release'"

# bashrc 적용
source ~/.bashrc

echo "Setup complete!"