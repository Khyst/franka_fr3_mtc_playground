import os
import yaml
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def load_yaml(package_name, file_path):
    """ Utility function to load a YAML file from a given package and file path """
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    with open(absolute_file_path, 'r') as f:
        return yaml.safe_load(f)

def get_fr3_robot_description(description_pkg_name):
    """ Utility function to load and process the URDF xacro file to generate the robot_description parameter """
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

def get_fr3_robot_description_semantic(description_pkg_name):
    """ Utility function to load and process the SRDF xacro file to generate the robot_description_semantic parameter """
    description_pkg_path = get_package_share_directory(description_pkg_name)
    
    srdf_xacro_file = os.path.join(
        description_pkg_path, 'robots', 'fr3', 'fr3.srdf.xacro'
    )
    
    robot_description_semantic_config = xacro.process_file(
        srdf_xacro_file,
        mappings={'hand': 'true', 'ee_id': 'franka_hand'}
    )
    
    return {'robot_description_semantic': robot_description_semantic_config.toxml()}

def get_fr3_ompl_planning_pipeline_config(config_pkg_name, config_file_name):
    """ Utility function to load the OMPL planning pipeline configuration from a YAML file """
    ompl_planning_yaml = load_yaml(config_pkg_name, f'config/{config_file_name}')
    
    ompl_planning_pipeline_config = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': ' '.join([
                'default_planner_request_adapters/AddTimeOptimalParameterization',
                'default_planner_request_adapters/ResolveConstraintFrames',
                'default_planner_request_adapters/FixWorkspaceBounds',
                'default_planner_request_adapters/FixStartStateBounds',
                'default_planner_request_adapters/FixStartStateCollision',
                'default_planner_request_adapters/FixStartStatePathConstraints',
            ]),
            'start_state_max_bounds_error': 0.1,
        }
    }
    ompl_planning_pipeline_config['move_group'].update(ompl_planning_yaml)
    
    return ompl_planning_pipeline_config

def generate_launch_description():
    
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_fr3_bringup = get_package_share_directory('franka_fr3_bringup')
    pkg_fr3_description = get_package_share_directory('franka_fr3_description')
    pkg_fr3_gazebo = get_package_share_directory('franka_fr3_gazebo')

    # ── Robot Description (URDF) ───────────────────────────────────────
    robot_description = get_fr3_robot_description('franka_fr3_description')

    # ── Robot Description Semantic (SRDF) ────────────────────────────
    robot_description_semantic = get_fr3_robot_description_semantic('franka_fr3_description')

    # ── kinematic configuration ─────────────────────────────────────────────────
    kinematics_yaml = load_yaml('franka_fr3_moveit_config', 'config/kinematics.yaml')

    # ── OMPL Planning Pipeline Configuration ─────────────────────────────────────
    ompl_planning_pipeline_config = get_fr3_ompl_planning_pipeline_config('franka_fr3_moveit_config', 'ompl_planning.yaml')

    
    # ── MoveIt Controllers Configuration ─────────────────────────────────────────
    moveit_controllers = {
        'moveit_simple_controller_manager': load_yaml('franka_fr3_moveit_config', 'config/moveit_controllers.yaml'),
        'moveit_controller_manager':
            'moveit_simple_controller_manager/MoveItSimpleControllerManager',
    }

    # ── Trajectory Execution Configuration ───────────────────────────────────────
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    # ── Planning Scene Monitor Configuration ─────────────────────────────────────
    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
    }

    # ── move_group node ───────────────────────────────────────────────
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
            {'use_sim_time': True},
        ],
    )

    # ── RViz ─────────────────────────────────────────────────────────
    rviz_config = os.path.join(
        get_package_share_directory('franka_fr3_moveit_config'), 'rviz', 'moveit.rviz'
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config],
        parameters=[
            robot_description,
            robot_description_semantic,
            ompl_planning_pipeline_config,
            kinematics_yaml,
            {'use_sim_time': True},
        ],
    )

    return LaunchDescription([
        move_group_node,
        rviz_node,
    ])
