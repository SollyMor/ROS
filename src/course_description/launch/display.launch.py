"""Publish the Ackermann URDF and optionally open it in RViz."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Start robot_state_publisher and, when rviz is true, RViz."""
    share = get_package_share_directory('course_description')
    xacro_path = os.path.join(share, 'urdf', 'vehicle.urdf.xacro')
    rviz_config = os.path.join(share, 'rviz', 'vehicle.rviz')
    robot_description = ParameterValue(
        Command(['xacro ', xacro_path]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Open RViz with Fixed Frame base_link',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])
