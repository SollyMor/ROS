"""Pure helpers for patrol velocity selection and parameter checks."""

import math

from geometry_msgs.msg import Twist

DEFAULT_LINEAR_SPEED = 0.5
DEFAULT_TURN_RATE = 0.3
DEFAULT_PUBLISH_HZ = 10.0

LINEAR_SPEED_LIMIT = (0.0, 1.0)
TURN_RATE_LIMIT = (-1.0, 1.0)
PUBLISH_HZ_LIMIT = (1.0, 30.0)

# Backwards-compatible aliases used by older tests.
LINEAR_X = DEFAULT_LINEAR_SPEED
ANGULAR_Z = DEFAULT_TURN_RATE
LINEAR_X_LIMIT = LINEAR_SPEED_LIMIT
ANGULAR_Z_LIMIT = TURN_RATE_LIMIT


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def is_finite_number(value) -> bool:
    """Return True if value converts to a finite float."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def validate_linear_speed(value) -> tuple[bool, str]:
    """Validate linear_speed before applying it to active state."""
    if not is_finite_number(value):
        return False, 'linear_speed must be a finite number'
    number = float(value)
    low, high = LINEAR_SPEED_LIMIT
    if number < low or number > high:
        return False, f'linear_speed must be in [{low}, {high}] m/s'
    return True, ''


def validate_turn_rate(value) -> tuple[bool, str]:
    """Validate turn_rate before applying it to active state."""
    if not is_finite_number(value):
        return False, 'turn_rate must be a finite number'
    number = float(value)
    low, high = TURN_RATE_LIMIT
    if number < low or number > high:
        return False, f'turn_rate must be in [{low}, {high}] rad/s'
    return True, ''


def validate_publish_hz(value) -> tuple[bool, str]:
    """Validate publish_hz before recreating the timer."""
    if not is_finite_number(value):
        return False, 'publish_hz must be a finite number'
    number = float(value)
    low, high = PUBLISH_HZ_LIMIT
    if number < low or number > high:
        return False, f'publish_hz must be in [{low}, {high}] Hz'
    return True, ''


def timer_period(publish_hz: float) -> float:
    """
    Convert publish frequency to a timer period.

    Caller must validate publish_hz first; zero yields ZeroDivisionError.
    """
    return 1.0 / float(publish_hz)


def twist_from_pose(
    pose,
    linear_speed: float = DEFAULT_LINEAR_SPEED,
    turn_rate: float = DEFAULT_TURN_RATE,
) -> Twist:
    """
    Build a Twist from the last pose and configured speeds.

    Before the first pose arrives (``pose is None``) return a zero command.
    After that publish the requested speeds, clamped to safe limits.
    """
    cmd = Twist()
    if pose is None:
        return cmd

    cmd.linear.x = _clamp(float(linear_speed), *LINEAR_SPEED_LIMIT)
    cmd.angular.z = _clamp(float(turn_rate), *TURN_RATE_LIMIT)
    return cmd
