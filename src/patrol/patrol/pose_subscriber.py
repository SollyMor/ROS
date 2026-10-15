"""Subscribe to relative sensor_pose with configurable reliability."""

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    """Log sensor_pose messages using the requested reliability profile."""

    def __init__(self) -> None:
        super().__init__('pose_subscriber')
        self.declare_parameter('reliability', 'best_effort')
        reliability_name = str(self.get_parameter('reliability').value).lower()
        if reliability_name == 'reliable':
            reliability = ReliabilityPolicy.RELIABLE
        elif reliability_name == 'best_effort':
            reliability = ReliabilityPolicy.BEST_EFFORT
        else:
            raise ValueError(
                f'unsupported reliability={reliability_name!r}; '
                "use 'reliable' or 'best_effort'"
            )

        qos = QoSProfile(
            reliability=reliability,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._count = 0
        self._sub = self.create_subscription(
            Pose,
            'sensor_pose',
            self._on_pose,
            qos,
        )
        self.get_logger().info(f'subscribing to sensor_pose with {reliability_name}')

    def _on_pose(self, msg: Pose) -> None:
        self._count += 1
        if self._count == 1 or self._count % 50 == 0:
            self.get_logger().info(
                f'received pose #{self._count}: x={msg.x:.3f} y={msg.y:.3f}'
            )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PoseSubscriber()
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
