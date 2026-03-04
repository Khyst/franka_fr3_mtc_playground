import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch import LaunchContext, LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, ExecuteProcess, RegisterEventHandler, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def get_fr3_robot_description(description_pkg_name):
    
    description_pkg_path = get_package_share_directory(description_pkg_name)
    
    franka_xacro_file = os.path.join(description_pkg_path, 'robots', 'fr3', 'fr3.urdf.xacro')
    
    robot_description_config = xacro.process_file(
        franka_xacro_file,
        mappings={
            'robot_type': 'fr3',
            'hand': 'true',
            'ros2_control': 'true',
            'gazebo': 'true',
            'ee_id': 'franka_hand'
        }
    )
    
    return {'robot_description': robot_description_config.toxml()}

def generate_launch_description():
    
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_fr3_bringup = get_package_share_directory('franka_fr3_bringup')
    pkg_fr3_description = get_package_share_directory('franka_fr3_description')
    pkg_fr3_gazebo = get_package_share_directory('franka_fr3_gazebo')

    # 1. Robot State Publisher 실행 (fr3.urdf.xacro에 정의된 gripper 포함 로봇 암에 대한 robot_description 발행)
    robot_description = get_fr3_robot_description('franka_fr3_description')
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            robot_description,
            {'use_sim_time': True}
        ]
    )

    # 2. Gazebo Ignition 시뮬레이터 실행 (fr3_gazebo 패키지에 정의된 panda_world.sdf 로드)
    world_sdf = os.path.join(pkg_fr3_gazebo, 'worlds', 'panda_world.sdf')
    gazebo_empty_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': world_sdf + ' -r', }.items(),
    )

    # 3. Robot Spawn (robot_description을 통해 정의된 로봇 모델을 Gazebo에 스폰)
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description', 
            '-name', 'panda', 
            '-x', '0.2', '-y', '0', '-z', '1.025', 
            '-allow_renaming', 'true'
        ],
        output='screen',
    )

    # 4. ROS-Gazebo Bridge 실행 (fr3_gazebo 패키지에 정의된 ros_gz_bridge_config.yaml을 통해 필요한 토픽 브릿지 설정, ROS<->GZ)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(
                get_package_share_directory('franka_fr3_bringup'), 'config', 'ros_gz_bridge_config.yaml'
            ),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )
    
    # 5. Joint State Broadcaster 실행 (spawn 완료 후 joint_state_broadcaster 컨트롤러 로드)
    load_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn,
            on_exit=[
                ExecuteProcess(
                    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                        'joint_state_broadcaster'],
                    output='screen'
                )
            ],
        )
    )

    # 6. Arm Controller 실행 (JointTrajectoryController - position interface for Gazebo)
    load_fr3_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[
                ExecuteProcess(
                    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                        'fr3_arm_controller'],
                    output='screen'
                )
            ],
        )
    )

    # 7. Hand Controller 실행 (GripperActionController - position interface for Gazebo)
    load_fr3_hand_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_fr3_arm_controller,
            on_exit=[
                ExecuteProcess(
                    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
                        'fr3_hand_controller'],
                    output='screen'
                )
            ],
        )
    )

    return LaunchDescription([
        gazebo_empty_world,
        robot_state_publisher,
        spawn,
        bridge,
        load_joint_state_broadcaster, # spawn 완료 후 joint_state_broadcaster 로드
        load_fr3_arm_controller, # joint_state_broadcaster 완료 후 arm controller 로드
        load_fr3_hand_controller, # arm controller 완료 후 hand controller 로드
    ])