"""Launch test: fixed frames arrive on /tf_static and processes exit cleanly."""

import os
import unittest

from ament_index_python.packages import get_package_share_directory
import launch
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import launch_testing
import pytest
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from tf2_msgs.msg import TFMessage


@pytest.mark.launch_test
def generate_test_description():
    """Start the display launch without RViz."""
    launch_file = os.path.join(
        get_package_share_directory('course_description'),
        'launch',
        'display.launch.py',
    )
    return launch.LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file),
            launch_arguments={'rviz': 'false'}.items(),
        ),
        launch_testing.actions.ReadyToTest(),
    ])


class TestStaticFrames(unittest.TestCase):
    """robot_state_publisher is the only source of the fixed tree."""

    def test_fixed_sensors_on_tf_static(self):
        from launch_testing_ros import WaitForTopics

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        with WaitForTopics(
            [('/tf_static', TFMessage)],
            timeout=20.0,
            qos_profile=qos,
        ) as waiter:
            frames = {
                (transform.header.frame_id, transform.child_frame_id)
                for message in waiter.received_messages('/tf_static')
                for transform in message.transforms
            }
        assert ('base_link', 'lidar_link') in frames
        assert ('base_link', 'camera_link') in frames
        assert ('base_link', 'imu_link') in frames
        assert ('camera_link', 'lidar_link') not in frames


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):

    def test_exit_codes(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
