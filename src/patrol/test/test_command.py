"""Unit tests for twist_from_pose."""

from patrol.command import ANGULAR_Z, LINEAR_X, twist_from_pose
from turtlesim.msg import Pose


def test_twist_without_pose_is_zero():
    cmd = twist_from_pose(None)
    assert cmd.linear.x == 0.0
    assert cmd.linear.y == 0.0
    assert cmd.linear.z == 0.0
    assert cmd.angular.x == 0.0
    assert cmd.angular.y == 0.0
    assert cmd.angular.z == 0.0


def test_twist_with_pose_uses_patrol_speeds():
    pose = Pose()
    pose.x = 5.5
    pose.y = 5.5
    pose.theta = 0.0
    cmd = twist_from_pose(pose)
    assert cmd.linear.x == LINEAR_X
    assert cmd.angular.z == ANGULAR_Z
    assert cmd.linear.y == 0.0
    assert cmd.angular.x == 0.0
