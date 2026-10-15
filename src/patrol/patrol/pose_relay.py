"""Relay /turtle1/pose to relative sensor_pose with best_effort QoS."""

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseRelay(Node):
    """Copy turtlesim pose onto a namespaced best_effort sensor topic."""

    def __init__(self) -> None:
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        # Absolute turtlesim topic: one global simulator for the whole graph.
        self._sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )

    def _on_pose(self, msg: Pose) -> None:
        self._pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PoseRelay()
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
