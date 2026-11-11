from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='rm_s0', executable='image_publisher', name='image_publisher', output='screen'),
        Node(package='rm_s0', executable='robot_controller', name='robot_controller', output='screen')
    ])
