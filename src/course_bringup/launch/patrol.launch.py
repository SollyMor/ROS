"""Bring up turtlesim, namespaced patrol, pose relay/subscriber, optional bag."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Namespace for patrol and sensor topics',
        ),
        DeclareLaunchArgument(
            'record',
            default_value='false',
            description='If true, record /<namespace>/sensor_pose as MCAP',
        ),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='evidence/pr05/bag',
            description='Output directory for ros2 bag record',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='best_effort',
            description='pose_subscriber reliability: reliable or best_effort',
        ),
        LogInfo(msg=['course_bringup: namespace=', namespace,
                     ' record=', record,
                     ' subscriber_reliability=', subscriber_reliability]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        Node(
            package='patrol',
            executable='patrol',
            name='patrol',
            namespace=namespace,
            remappings=[('cmd_vel', '/turtle1/cmd_vel')],
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_relay',
            name='pose_relay',
            namespace=namespace,
            output='screen',
        ),
        Node(
            package='patrol',
            executable='pose_subscriber',
            name='pose_subscriber',
            namespace=namespace,
            parameters=[{'reliability': subscriber_reliability}],
            output='screen',
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record', '-s', 'mcap',
                '-o', bag_dir,
                '--topics', ['/', namespace, '/sensor_pose'],
            ],
            output='screen',
            condition=IfCondition(record),
        ),
    ])
