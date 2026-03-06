#!/bin/bash
set -e # 에러 발생 시 즉시 중단

# 매크로
add_to_bashrc() {
    local line="$1"
    if ! grep -qF "$line" ~/.bashrc; then
        echo "$line" >> ~/.bashrc
    fi
}

# 1. 시스템 업데이트 (컨테이너 내부이므로 sudo 제외)
apt update && apt upgrade -y

# 2. 필수 도구 설치
apt install -y \
    git gedit nano vim curl wget build-essential \
    python3-colcon-common-extensions \
    python3-rosdep

# 3. Git 소유권 예외 등록 (중요: dubious ownership 에러 방지)
git config --global --add safe.directory /root/ws_moveit

# 4. rosdep 초기화 (실패해도 중단되지 않도록 || true 처리)
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    rosdep init || true
fi
rosdep update

# 5. Bashrc 설정 추가
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

echo "Setup complete! Please restart your terminal or run 'sb'."