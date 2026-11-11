import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import math

class PnpSolver(Node):
    def __init__(self):
        super().__init__('pnp_solver')
        # 订阅 S1 的像素点
        self.sub_pixel = self.create_subscription(Point, '/s1_armor_pixel', self.pixel_callback, 10)
        # 发布 3D 坐标 (x, y, z) 单位：米
        self.pub_xyz = self.create_publisher(Point, '/s2_armor_xyz', 10)
        
        # 假装我们的相机内参已知（可以替换为你真实的相机内参）
        self.cx = 320.0 # 假设图像宽 640，光心在中心
        self.cy = 240.0 # 假设图像高 480，光心在中心
        self.f = 800.0  # 焦距
        self.get_logger().info("S2 PnP 解算节点已启动！")

    def pixel_callback(self, msg):
        px = msg.x
        py = msg.y
        
        # 极简等效模型（为了在无真实靶标的环境下跑通链路，假设目标Z轴距离为2米）
        # 真实比赛中这里应该调用 cv2.solvePnP 使用装甲板真实物理尺寸
        z_real = 2.0
        
        # 用相机针孔模型反推真实的 X 和 Y
        x_real = (px - self.cx) * z_real / self.f
        y_real = (py - self.cy) * z_real / self.f
        
        pt3d = Point()
        pt3d.x, pt3d.y, pt3d.z = float(x_real), float(y_real), float(z_real)
        self.pub_xyz.publish(pt3d)
        self.get_logger().info(f"解算3D坐标: X={x_real:.2f}m, Y={y_real:.2f}m, Z={z_real:.2f}m")

def main(args=None):
    rclpy.init(args=args)
    node = PnpSolver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
