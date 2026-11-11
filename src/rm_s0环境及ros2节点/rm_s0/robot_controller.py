import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.time_counter = 0.0
        self.get_logger().info("S0: [底盘/云台控制节点] 已启动，正在发送 /cmd_vel...")

    def timer_callback(self):
        msg = Twist()
        msg.angular.z = math.sin(self.time_counter) * 0.5 
        msg.linear.x = 0.2
        self.pub_vel.publish(msg)
        self.time_counter += 0.1

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
