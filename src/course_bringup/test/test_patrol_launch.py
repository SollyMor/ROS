# Copyright 2026 course
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Launch test: namespaced patrol comes up and every process exits cleanly."""

import os
import unittest

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
import launch
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import launch_testing
import launch_testing.actions
from launch_testing_ros import WaitForTopics
import pytest
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


@pytest.mark.launch_test
def generate_test_description():
    """Start patrol.launch.py with recording disabled."""
    launch_file = os.path.join(
        get_package_share_directory('course_bringup'),
        'launch',
        'patrol.launch.py',
    )
    return launch.LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file),
            launch_arguments={
                'namespace': 'robot_a',
                'record': 'false',
                'subscriber_reliability': 'best_effort',
            }.items(),
        ),
        launch_testing.actions.ReadyToTest(),
    ])


class TestPatrolBringup(unittest.TestCase):
    """Live checks while the launch processes are running."""

    def test_sensor_and_command_topics(self):
        """best_effort sensor_pose and remapped cmd_vel both deliver."""
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        topics = [
            ('/robot_a/sensor_pose', Pose),
            ('/turtle1/cmd_vel', Twist),
        ]
        with WaitForTopics(topics, timeout=20.0, qos_profile=qos) as waiter:
            assert waiter.topics_received() == {
                '/robot_a/sensor_pose',
                '/turtle1/cmd_vel',
            }
            assert waiter.topics_not_received() == set()

    def test_subscriber_uses_best_effort(self, proc_output):
        """Launch argument subscriber_reliability reaches the node."""
        proc_output.assertWaitFor(
            'subscribing to sensor_pose with best_effort',
            timeout=20,
        )


@launch_testing.post_shutdown_test()
class TestPatrolShutdown(unittest.TestCase):
    """After the test, every launched process must exit with code 0."""

    def test_exit_codes(self, proc_info):
        """SIGINT from launch is handled; no process is left to be killed."""
        launch_testing.asserts.assertExitCodes(proc_info)
