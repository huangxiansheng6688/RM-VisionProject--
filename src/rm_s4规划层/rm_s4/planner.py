import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Bool
import math
import json
import time

class Planner(Node):
    def __init__(self):
        super().__init__('planner')
        self.sub_kf = self.create_subscription(Point, '/s3_armor_kf', self.kf_callback, 10)
        self.pub_fire = self.create_publisher(Bool, '/is_fire', 10)
        self.pub_gimbal = self.create_publisher(Point, '/gimbal_cmd', 10)

        self.bullet_speed = 25.0 
        self.gravity = 9.8
        
        self.start_time = time.time()
        self.frame_count = 0
        self.get_logger().info("S4 规划器已启动 (计算弹道与开火判断)")

    def kf_callback(self, msg):
        self.frame_count += 1
        x, y, z = msg.x, msg.y, msg.z
        
        # 计算水平距离 (假设 Z 是正前方)
        distance = math.sqrt(x**2 + z**2)
        if distance < 0.1: return

        # 1. 重力补偿 (小角度近似公式)
        pitch_comp = (self.gravity * distance) / (2 * self.bullet_speed**2)
        
        # 2. 计算云台目标角度
        yaw_target = math.atan2(x, z)
        pitch_target = pitch_comp 
        
        cmd = Point()
        cmd.x = float(yaw_target)
        cmd.y = float(pitch_target)
        self.pub_gimbal.publish(cmd)

        # 3. 开火判断
        fire_msg = Bool()
        if 1.0 < distance < 5.0: # 假设在 1-5 米内开火
            fire_msg.data = True
        else:
            fire_msg.data = False
        self.pub_fire.publish(fire_msg)
        
        self.get_logger().info(f"规划: 距离={distance:.2f}m, 俯仰补偿={math.degrees(pitch_target):.2f}°, 开火={fire_msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = Planner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # 按 Ctrl+C 时自动生成 JSON
        duration = time.time() - node.start_time
        fps = node.frame_count / duration if duration > 0 else 0
        result = {"fps": round(fps, 2), "frames": node.frame_count, "status": "success"}
        with open('result.json', 'w') as f:
            json.dump(result, f, indent=4)
        node.get_logger().info("已生成 result.json！")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
