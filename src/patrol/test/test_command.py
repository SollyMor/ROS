"""Unit tests for twist_from_pose and parameter validation."""

import math

from patrol.command import (
    ANGULAR_Z,
    LINEAR_X,
    timer_period,
    twist_from_pose,
    validate_linear_speed,
    validate_publish_hz,
    validate_turn_rate,
)
import pytest
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


def test_twist_uses_custom_speeds():
    pose = Pose()
    cmd = twist_from_pose(pose, linear_speed=0.2, turn_rate=-0.4)
    assert cmd.linear.x == 0.2
    assert cmd.angular.z == -0.4


def test_validate_publish_hz_accepts_five():
    ok, reason = validate_publish_hz(5.0)
    assert ok
    assert reason == ''
    assert timer_period(5.0) == pytest.approx(0.2)


def test_validate_publish_hz_rejects_zero():
    ok, reason = validate_publish_hz(0.0)
    assert not ok
    assert 'publish_hz' in reason


def test_validate_publish_hz_rejects_negative():
    ok, reason = validate_publish_hz(-1.0)
    assert not ok
    assert 'publish_hz' in reason


def test_validate_publish_hz_rejects_nan():
    ok, reason = validate_publish_hz(float('nan'))
    assert not ok
    assert 'finite' in reason


def test_timer_period_without_check_divides_by_zero():
    with pytest.raises(ZeroDivisionError):
        timer_period(0.0)


def test_validate_linear_speed_and_turn_rate_bounds():
    assert validate_linear_speed(0.5)[0]
    assert not validate_linear_speed(1.5)[0]
    assert not validate_linear_speed(float('nan'))[0]
    assert validate_turn_rate(-0.3)[0]
    assert not validate_turn_rate(2.0)[0]
    assert not validate_turn_rate(math.inf)[0]
