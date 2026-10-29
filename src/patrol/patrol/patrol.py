"""Patrol node: subscribe to pose, publish Twist on a timer."""

from geometry_msgs.msg import Twist
from patrol.command import (
    DEFAULT_LINEAR_SPEED,
    DEFAULT_PUBLISH_HZ,
    DEFAULT_TURN_RATE,
    timer_period,
    twist_from_pose,
    validate_linear_speed,
    validate_publish_hz,
    validate_turn_rate,
)
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from turtlesim.msg import Pose


class Patrol(Node):
    """Store the latest turtle pose and publish a periodic velocity command."""

    def __init__(self) -> None:
        super().__init__('patrol')
        self._last_pose: Pose | None = None

        self.declare_parameter('linear_speed', DEFAULT_LINEAR_SPEED)
        self.declare_parameter('turn_rate', DEFAULT_TURN_RATE)
        self.declare_parameter('publish_hz', DEFAULT_PUBLISH_HZ)

        self._linear_speed = float(self.get_parameter('linear_speed').value)
        self._turn_rate = float(self.get_parameter('turn_rate').value)
        self._publish_hz = float(self.get_parameter('publish_hz').value)

        ok, reason = validate_linear_speed(self._linear_speed)
        if not ok:
            raise ValueError(reason)
        ok, reason = validate_turn_rate(self._turn_rate)
        if not ok:
            raise ValueError(reason)
        ok, reason = validate_publish_hz(self._publish_hz)
        if not ok:
            raise ValueError(reason)

        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = None
        self._recreate_timer(self._publish_hz)
        self.add_on_set_parameters_callback(self._on_set_parameters)

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(
            twist_from_pose(
                self._last_pose,
                linear_speed=self._linear_speed,
                turn_rate=self._turn_rate,
            )
        )

    def _recreate_timer(self, publish_hz: float) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self.destroy_timer(self._timer)
            self._timer = None
        self._timer = self.create_timer(timer_period(publish_hz), self._on_timer)

    def _on_set_parameters(self, params: list[Parameter]) -> SetParametersResult:
        pending_linear = self._linear_speed
        pending_turn = self._turn_rate
        pending_hz = self._publish_hz
        hz_changed = False

        for param in params:
            if param.name == 'linear_speed':
                ok, reason = validate_linear_speed(param.value)
                if not ok:
                    return SetParametersResult(successful=False, reason=reason)
                pending_linear = float(param.value)
            elif param.name == 'turn_rate':
                ok, reason = validate_turn_rate(param.value)
                if not ok:
                    return SetParametersResult(successful=False, reason=reason)
                pending_turn = float(param.value)
            elif param.name == 'publish_hz':
                ok, reason = validate_publish_hz(param.value)
                if not ok:
                    return SetParametersResult(successful=False, reason=reason)
                pending_hz = float(param.value)
                hz_changed = True

        self._linear_speed = pending_linear
        self._turn_rate = pending_turn
        if hz_changed and pending_hz != self._publish_hz:
            self._recreate_timer(pending_hz)
            self._publish_hz = pending_hz
        elif hz_changed:
            self._publish_hz = pending_hz

        return SetParametersResult(successful=True)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
