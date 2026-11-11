```markdown
# rm_s0：环境与数据 (数据流与测试床构建)

## 1. 方案选型与理由
由于本地虚拟机环境（无独立显卡、算力受限）无法流畅运行官方提供的 Daedalus (ROS2Gazebo) 物理仿真引擎，本方案采取了**“真实图像流驱动 + 离线数据回放”**的替代策略：
- 编写 `image_publisher` 节点，通过 OpenCV 读取本地测试图像（520.png），以 30Hz 频率发布标准的 `sensor_msgs/Image`。
- 编写 `robot_controller` 节点，以 10Hz 频率发布底盘/云台的模拟控制指令 `geometry_msgs/Twist`。
- 通过上述节点，构建了一个完全符合 ROS2 通信规范的“虚拟测试环境”，后续的 S1-S4 算法均可基于此数据流进行闭环测试，且时间戳严格同步，保证了实验的可复现性。

## 2. 节点说明
1. **`image_publisher`**：
   - 功能：读取本地图片，转换为 ROS2 Image 消息并发布。
   - 发布话题：`/image_raw` (sensor_msgs/Image)
   - 参数：图像发布频率设为 30Hz，`frame_id` 设为 `camera_link`。
2. **`robot_controller`**：
   - 功能：模拟云台扫视与底盘移动指令，用于后续动态场景的联合调试。
   - 发布话题：`/cmd_vel` (geometry_msgs/Twist)

## 3. 编译与运行方法
```bash
# 编译
colcon build --packages-select rm_s0

# 激活环境
source install/setup.bash

# 一键启动
ros2 launch rm_s0 s0_bringup.launch.py
```

4. 已知失效场景与原因分析

· 图像渲染延迟：在使用 RViz2 查看 /image_raw 话题时，虚拟机环境可能出现 No Image 或渲染延迟。经排查，这是由于虚拟机 OpenGL 硬件加速缺失导致的显示端问题，底层 ROS2 通信与图像传输实际正常。
· 图片路径读取失败：若 520.png 未放置在 setup.py 同级目录，cv2.imread 会返回 None 导致节点崩溃。已通过在 setup.py 的 data_files 中正确配置资源安装路径解决。

5. 验收达成情况

☑ 能够持续发布图像话题 /image_raw。
☑ 能够发布控制指令 /cmd_vel。
☑ 成功替代仿真环境，为 S1-S4 提供数据输入源。

# rm_s0：环境与数据

## 1. 方案选型

无 Daedalus 仿真环境，采用 `image_publisher` 模拟真实相机（30Hz），`robot_controller` 模拟云台控制。使用 `ros2 bag` 录制数据包，保证测试可复现。

## 2. 思考题解答

- **Q：为什么图像里没有畸变？如果换成真实相机，你的链路要改哪几步？**
  - **答**：仿真图像通常无畸变。换真实相机需在 S0 中调用真实 SDK 获取图像，并在 S2 中加入 `cv2.undistort` 去畸变，同时替换相机内参。
- **Q：录 bag 时，图像和 TF 的时间戳是同一时刻吗？**
  - **答**：通常不同步。如果不一致，对于运动目标会造成严重的坐标错位误差。本方案严格使用统一时钟发布时间戳。
