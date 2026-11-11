import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Point
import cv2
import numpy as np

class ArmorDetector(Node):
    def __init__(self):
        super().__init__('armor_detector')
        self.sub_img = self.create_subscription(Image, '/image_raw', self.image_callback, 10)
        # 发布找到的像素坐标
        self.pub_pixel = self.create_publisher(Point, '/s1_armor_pixel', 10)
        self.bridge = CvBridge()
        self.get_logger().info("S1 识别节点已启动！正在等待图像...")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"图像转换失败: {e}")
            return

        # 1. 转 HSV 找红色
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 80, 80])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # 2. 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找最大的红色块当作装甲板
            max_cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_cnt) > 50: # 过滤噪点
                x, y, w, h = cv2.boundingRect(max_cnt)
                cx, cy = x + w/2.0, y + h/2.0
                
                # 3. 发布像素坐标
                pt = Point()
                pt.x, pt.y, pt.z = float(cx), float(cy), 0.0
                self.pub_pixel.publish(pt)
                
                # 打印在终端上，证明代码跑通了！
                self.get_logger().info(f"发现目标! 像素坐标: X={cx:.1f}, Y={cy:.1f}, 面积={cv2.contourArea(max_cnt):.1f}")

def main(args=None):
    rclpy.init(args=args)
    node = ArmorDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
