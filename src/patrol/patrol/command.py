"""Pure helpers for patrol velocity selection."""

from geometry_msgs.msg import Twist

LINEAR_X = 0.5
ANGULAR_Z = 0.3
LINEAR_X_LIMIT = (0.0, 0.5)
ANGULAR_Z_LIMIT = (-1.0, 1.0)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def twist_from_pose(pose) -> Twist:
    """
    Build a Twist from the last pose.

    Before the first pose arrives (``pose is None``) return a zero command.
    After that publish the fixed patrol speeds, clamped to safe limits.
    """
    cmd = Twist()
    if pose is None:
        return cmd

    cmd.linear.x = _clamp(LINEAR_X, *LINEAR_X_LIMIT)
    cmd.angular.z = _clamp(ANGULAR_Z, *ANGULAR_Z_LIMIT)
    return cmd
