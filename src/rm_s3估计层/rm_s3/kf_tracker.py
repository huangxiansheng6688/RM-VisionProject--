import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

class KfTracker(Node):
    def __init__(self):
        super().__init__('kf_tracker')
        self.sub_xyz = self.create_subscription(Point, '/s2_armor_xyz', self.xyz_callback, 10)
        self.pub_filtered = self.create_publisher(Point, '/s3_armor_kf', 10)
        
        # 极简 1D 卡尔曼参数
        self.x = 0.0 
        self.p = 1.0 
        self.q = 0.01 # 过程噪声 (越小越平滑)
        self.r = 0.1  # 测量噪声
        
        self.get_logger().info("S3 卡尔曼滤波节点已启动！")

    def xyz_callback(self, msg):
        z_measure = msg.z
        
        # 预测
        self.p = self.p + self.q
        # 更新
        k = self.p / (self.p + self.r)
        self.x = self.x + k * (z_measure - self.x)
        self.p = (1 - k) * self.p
        
        out_msg = Point()
        out_msg.x = msg.x
        out_msg.y = msg.y
        out_msg.z = self.x 
        self.pub_filtered.publish(out_msg)
        self.get_logger().info(f"滤波后坐标: X={out_msg.x:.2f}, Y={out_msg.y:.2f}, Z={self.x:.3f}")

def main(args=None):
    rclpy.init(args=args)
    node = KfTracker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
