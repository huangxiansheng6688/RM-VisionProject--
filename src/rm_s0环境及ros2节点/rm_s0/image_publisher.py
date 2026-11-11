import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
from ament_index_python.packages import get_package_share_directory

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        pkg_dir = get_package_share_directory('rm_s0')
        self.image_path = os.path.join(pkg_dir, '520.png')
        
        if not os.path.exists(self.image_path):
            self.get_logger().error(f"找不到图：{self.image_path}")
            exit(1)

        self.cv_image = cv2.imread(self.image_path)
        self.bridge = CvBridge()
        self.publisher_ = self.create_publisher(Image, '/image_raw', 10)
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        self.get_logger().info("S0: [图像发布节点] 已启动，正在发布 /image_raw...")

    def timer_callback(self):
        msg = self.bridge.cv2_to_imgmsg(self.cv_image, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_link"
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
