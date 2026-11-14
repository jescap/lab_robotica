# This script is used for generating the statistics that will be used in
# the evaluation of the robotics challenge

import math
import time
import yaml

import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions

import tf2_ros
import tf2_geometry_msgs  # noqa: F401  (registers PoseStamped transform support on Buffer)

from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker, MarkerArray


class Metrics:
    def __init__(self, logger, output_file):
        self.logger = logger
        self.goal_reached = False
        self.distance_traveled = 0.0
        self.elapsed_time = 0.0
        self.min_dist_to_obs = 100.0
        self.avg_dist_to_obs = 0.0
        self.collision_penalty = 0
        self.lin_vel_penalty = 0
        self.ang_vel_penalty = 0
        self.out_file = output_file

    def store_metrics(self):
        self.logger.info('Stopped Evaluation node. Generating metrics result file')
        try:
            with open(self.out_file, 'w') as f:
                f.write('Goals reached: %s\n' % (self.goal_reached))
                f.write('Elapsed time: %f\n' % (float(self.elapsed_time)))
                f.write('Traveled distance: %f\n' % (self.distance_traveled))
                f.write('Min distance to obstacles: %f\n' % (self.min_dist_to_obs))
                f.write('Avg distance to obstacles: %f\n' % (self.avg_dist_to_obs))
                f.write('Collision penalties: %d\n' % (self.collision_penalty))

            self.logger.info(f'File exported successfully. Filename: {self.out_file}')
        except OSError as e:
            self.logger.error(f'Could not save output file. Error: {e}')


class Evaluation(Node):
    def __init__(self):
        super().__init__('evaluation')

        self.get_logger().info('Starting Evaluation node...')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('global_frame', 'map')
        self.declare_parameter('output_file', 'metrics.txt')
        self.declare_parameter('max_lin_vel', 0.25)
        self.declare_parameter('max_ang_vel', 1.2)
        self.declare_parameter('goal_tolerance', 0.15)
        self.declare_parameter('min_collision_dist', 0.1)
        self.declare_parameter('path_following', False)
        self.declare_parameter('goals_file', '')
        self.declare_parameter('path_file', '')

        self.base_frame = self.get_parameter('base_frame').get_parameter_value().string_value
        self.global_frame = self.get_parameter('global_frame').get_parameter_value().string_value
        self.output_file = self.get_parameter('output_file').get_parameter_value().string_value
        self.max_lin_vel = self.get_parameter('max_lin_vel').get_parameter_value().double_value
        self.max_ang_vel = self.get_parameter('max_ang_vel').get_parameter_value().double_value
        self.goal_gap = self.get_parameter('goal_tolerance').get_parameter_value().double_value
        self.min_collision = self.get_parameter('min_collision_dist').get_parameter_value().double_value
        self.path_following = self.get_parameter('path_following').get_parameter_value().bool_value

        # Get the robot pose in global frame
        self.has_transform = False
        while not self.has_transform:
            self.init_x, self.init_y = self.get_transform()
            self.px = self.init_x
            self.py = self.init_y
            if not self.has_transform:
                # Process incoming TF messages while we wait (nothing does this
                # automatically until rclpy.spin() is called from main)
                rclpy.spin_once(self, timeout_sec=0.1)
        self.get_logger().info(
            f'Evaluation: got robot position! init_x = {self.init_x} init_y={self.init_y}')

        self.metrics = Metrics(self.get_logger(), self.output_file)
        self.hist_dist_to_obs = []

        if self.path_following:
            path_file = self.get_parameter('path_file').get_parameter_value().string_value
            with open(path_file, 'r') as f:
                goals = sorted(yaml.safe_load(f)['path'].items())

            self.goals_queue = []
            self.path = Path()
            self.path.header.frame_id = self.global_frame
            for point in goals:
                self.get_logger().info(
                    f"Reading path waypoint x: {point[1]['x']:.2f}, y: {point[1]['y']:.2f}")
                pose = PoseStamped()
                pose.header.frame_id = self.path.header.frame_id
                pose.pose.position.x = point[1]['x']
                pose.pose.position.y = point[1]['y']
                pose.pose.position.z = 0.0
                pose.pose.orientation.w = 1.0
                self.path.poses.append(pose)

            # Take the last goal
            self.current_goal = self.path.poses[-1]
            self.goals_queue.append(self.current_goal)
            self.time_limit = 90.0  # seconds

            markers = self.generate_visualization_goals()

        else:
            goals_file = self.get_parameter('goals_file').get_parameter_value().string_value
            with open(goals_file, 'r') as f:
                goals = sorted(yaml.safe_load(f)['goals'].items())

            self.goals_queue = []
            for point in goals:
                self.get_logger().info(
                    f"Reading goal x: {point[1]['x']:.2f}, y: {point[1]['y']:.2f}")
                pose = PoseStamped()
                pose.header.frame_id = self.global_frame
                pose.pose.position.x = float(point[1]['x'])
                pose.pose.position.y = float(point[1]['y'])
                pose.pose.position.z = 0.0
                pose.pose.orientation.w = 1.0
                self.goals_queue.append(pose)

            markers = self.generate_visualization_goals()

            # Take the first goal
            self.current_goal = self.goals_queue.pop(0)
            self.time_limit = 200.0  # seconds

        self.flag_markers = MarkerArray()
        self.goal_sent = False
        self.count = 0

        self.get_logger().info('Before publishers and subscribers....')
        self.goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 10)
        self.path_pub = self.create_publisher(Path, 'path', 10)
        self.marker_pub = self.create_publisher(MarkerArray, 'goal_markers', 10)
        self.flag_pub = self.create_publisher(MarkerArray, 'flag_markers', 10)
        self.create_subscription(LaserScan, 'scan', self.scan_callback, 1)
        self.create_subscription(TwistStamped, 'cmd_vel', self.cmd_vel_callback, 1)

        # Wait for RViz2 to be subscribed to the markers before publishing
        while self.marker_pub.get_subscription_count() < 1:
            self.get_logger().info('Waiting for subscribers...')
            time.sleep(0.5)
        self.get_logger().info('Publishing markers')
        self.marker_pub.publish(markers)
        self.init_time = self.get_clock().now()

        # Timer to run the evaluation loop
        self.timer = self.create_timer(0.1, self.update)

    def scan_callback(self, data):
        m = min(data.ranges)
        self.hist_dist_to_obs.append(m)
        if m < self.metrics.min_dist_to_obs:
            self.metrics.min_dist_to_obs = m
        if m <= self.min_collision:
            self.get_logger().warn('Collision penalty!!!')
            self.metrics.collision_penalty += 1

    def cmd_vel_callback(self, data):
        if abs(data.twist.linear.x) > self.max_lin_vel:
            self.metrics.lin_vel_penalty += 1
        if abs(data.twist.angular.z) > self.max_ang_vel:
            self.metrics.ang_vel_penalty += 1

    def get_transform(self):
        try:
            t = self.tf_buffer.lookup_transform(self.global_frame, self.base_frame, rclpy.time.Time())
            self.has_transform = True
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                tf2_ros.ExtrapolationException):
            return (0.0, 0.0)

        return (t.transform.translation.x, t.transform.translation.y)

    def generate_visualization_goals(self):
        ma = MarkerArray()
        t = self.get_clock().now().to_msg()
        for i, p in enumerate(self.goals_queue):
            m = Marker()
            m.header.frame_id = p.header.frame_id
            m.header.stamp = t
            m.ns = 'goals'
            m.id = i
            m.type = Marker.CYLINDER
            m.action = Marker.ADD
            m.pose.position.x = p.pose.position.x
            m.pose.position.y = p.pose.position.y
            m.pose.position.z = 0.01
            m.pose.orientation.w = 1.0
            m.scale.x = 0.16
            m.scale.y = 0.16
            m.scale.z = 0.01
            m.color.a = 1.0
            m.color.r = 0.0
            m.color.g = 1.0
            m.color.b = 0.0
            ma.markers.append(m)
        return ma

    def publish_flag(self, goal):
        t = self.get_clock().now().to_msg()
        m = Marker()
        i = len(self.flag_markers.markers)
        for f in self.flag_markers.markers:
            f.header.stamp = t

        m.header.frame_id = goal.header.frame_id
        m.header.stamp = t
        m.ns = 'goal_flags'
        m.id = i
        m.type = Marker.CYLINDER
        m.action = Marker.ADD
        m.pose.position.x = goal.pose.position.x
        m.pose.position.y = goal.pose.position.y
        m.pose.position.z = 0.02
        m.pose.orientation.w = 1.0
        m.scale.x = 0.16
        m.scale.y = 0.16
        m.scale.z = 0.01
        m.color.a = 1.0
        m.color.r = 0.0
        m.color.g = 0.0
        m.color.b = 1.0
        self.flag_markers.markers.append(m)
        self.get_logger().info('Publishing goal reached flag!')
        self.flag_pub.publish(self.flag_markers)

    def update(self):
        self.count += 1
        gx = self.current_goal.pose.position.x
        gy = self.current_goal.pose.position.y

        # If no goal has been sent, send it!
        if not self.goal_sent:
            if self.path_following and self.path_pub.get_subscription_count() > 0:
                self.path_pub.publish(self.path)
                self.get_logger().info(
                    f'\n\t\tNAVIGATION PATH TO GOAL x:{gx:.2f}, y:{gy:.2f} SENT!\n')
                self.goal_sent = True
            elif not self.path_following and self.goal_pub.get_subscription_count() > 0:
                self.goal_pub.publish(self.current_goal)
                self.get_logger().info(
                    f'\n\t\tNAVIGATION GOAL x:{gx:.2f}, y:{gy:.2f} SENT!\n')
                self.goal_sent = True

        # Get the current robot position in the map
        cx, cy = self.get_transform()

        # Check the distance to the current goal
        dist_goal = math.sqrt((cx - gx) ** 2 + (cy - gy) ** 2)

        # Compute the distance that the robot has moved
        self.metrics.distance_traveled += math.sqrt((cx - self.px) ** 2 + (cy - self.py) ** 2)
        self.px = cx
        self.py = cy

        # Check that we do not exceed a time deadline
        ts = (self.get_clock().now() - self.init_time).nanoseconds * 1e-9

        if self.count > 10:
            self.get_logger().info(
                f'Metrics update: Traveled distance {self.metrics.distance_traveled} '
                f'Time: {ts:.2f} Dist to goal: {dist_goal}')
            self.count = 0

        if ts >= self.time_limit:
            self.get_logger().info(
                f'TIME ELAPSED EXCEEDED THE TIME LIMIT OF {self.time_limit:.1f} SECONDS!!!')
            self.metrics.elapsed_time = ts
            self.metrics.avg_dist_to_obs = round(
                (sum(self.hist_dist_to_obs) / len(self.hist_dist_to_obs)), 2)
            raise SystemExit

        # Has the goal been reached?
        if dist_goal <= self.goal_gap:
            self.get_logger().info(
                f'Goal x: {gx:.2f}, y: {gy:.2f} reached!!! Elapsed time: {ts:.2f}\n')
            self.publish_flag(self.current_goal)
            # Update goal if possible. In path following mode there is only one final goal
            if not self.path_following and len(self.goals_queue) > 0:
                self.current_goal = self.goals_queue.pop(0)
                self.goal_sent = False
            else:
                # All goals have been reached, finish the program
                ts = (self.get_clock().now() - self.init_time).nanoseconds * 1e-9
                self.metrics.elapsed_time = ts
                self.metrics.goal_reached = True
                self.metrics.avg_dist_to_obs = round(
                    (sum(self.hist_dist_to_obs) / len(self.hist_dist_to_obs)), 2)
                self.get_logger().info('ALL THE GOALS REACHED!!! Storing metrics...')
                raise SystemExit


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)

    node = Evaluation()
    node.get_logger().info('To stop the Evaluation node press CTRL + C')

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass

    node.metrics.store_metrics()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
