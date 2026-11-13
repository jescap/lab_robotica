#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8

import yaml

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path


class PathPublisher(Node):

    def __init__(self):
        super().__init__('path_publisher')

        # The node receives the path of a YAML file with the goals.
        # It also receives the frame of the goals. 
        self.declare_parameter('path_file', '')
        self.declare_parameter('path_frame', 'odom')

        path_file = self.get_parameter('path_file').get_parameter_value().string_value

        if not path_file:
            raise RuntimeError(
                "The 'path_file' parameter is required (path to a YAML file with the path points)")

        path_frame = self.get_parameter('path_frame').get_parameter_value().string_value

        with open(path_file, 'r') as f:
            goals = sorted(yaml.safe_load(f)['path'].items())

        # Fill the path message
        self.path = Path()
        self.path.header.frame_id = path_frame
        
        for point in goals:
            pose = PoseStamped()
            pose.header.frame_id = self.path.header.frame_id
            pose.pose.position.x = point[1]['x']
            pose.pose.position.y = point[1]['y']
            pose.pose.position.z = 0.0
            self.path.poses.append(pose)
            self.get_logger().info(f"Added point {point[1]['x']:.2f}, {point[1]['y']:.2f}")

        self.path_publisher = self.create_publisher(Path, 'path', 10)

        # Send the path once a second
        self.timer = self.create_timer(1.0, self.publish_path)

    def publish_path(self):
        self.path.header.stamp = self.get_clock().now().to_msg()
        self.path_publisher.publish(self.path)


def main(args=None):
    
    rclpy.init(args=args)
    node = PathPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
