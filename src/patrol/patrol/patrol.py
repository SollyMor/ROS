"""Patrol node: subscribe to pose, publish Twist on a timer."""

from geometry_msgs.msg import Twist
from patrol.command import twist_from_pose
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class Patrol(Node):
    """Store the latest turtle pose and publish a periodic velocity command."""

    def __init__(self) -> None:
        super().__init__('patrol')
        self._last_pose: Pose | None = None
        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(0.1, self._on_timer)

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(twist_from_pose(self._last_pose))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
