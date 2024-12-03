from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def get_path(package, dir, file):
    return os.path.join(
        get_package_share_directory(package),
        dir,
        file
    )

def launch(package, file, launch_folder="launch", arguments={}):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            get_path(package, launch_folder, file)
        ),
        launch_arguments=arguments.items()
    )

def generate_launch_description():
    imu_config = get_path("autonomy", "config", "imu.yml")
    robot_localization_config = get_path("autonomy", "config", "robot_localization.yml")

    return LaunchDescription(
        [
            # STATIC TRANSFORMS
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='static_transform_publisher_world_map',
                output='screen',
                arguments=[
                    '0', '0', '0',  # Translation: x = 0.035, y = 0.04, z = 0 (meters)
                    '0', '0', '0', '1', # Rotation: 0
                    'world',
                    'map'
                ],
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='static_transform_publisher_map_odom',
                output='screen',
                arguments=[
                    '0', '0', '0',  # Translation: x = 0.035, y = 0.04, z = 0 (meters)
                    '0', '0', '0', '1', # Rotation: 0
                    'map',
                    'odom'
                ],
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='static_transform_publisher_odom_base_link',
                output='screen',
                arguments=[
                    '0', '0', '0',  # Translation: x = 0.035, y = 0.04, z = 0 (meters)
                    '0', '0', '0', '1', # Rotation: 0
                    'odom',
                    'base_link'
                ],
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='static_transform_publisher_base_link_lidar',
                output='screen',
                arguments=[
                    '-0.035', '-0.04', '0',  # Translation: x = 0.035, y = 0.04, z = 0 (meters)
                    '0', '0', '1', '0', # Rotation: M_PI
                    'base_link',
                    'laser'
                ],
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                name='static_transform_publisher_base_link_imu',
                output='screen',
                arguments=[
                    '-0.18', '0.0', '0',  # Translation: x = -0.18, y = 0.07, z = 0 (meters)
                    '0', '0', '0', '1', # Rotation: 0
                    'base_link',
                    'imu'
                ],
            ),
            # Run joystick reader
            Node(
                package="joy",
                executable="joy_node",
                name="joy_node", #ros2 uses events, so don't try and direct this to /dev
            ),
            # IMU
            Node(
                package='witmotion_ros',
                executable='witmotion_ros_node',
                parameters=[
                    imu_config
                ]
            ),
            # Robot Localization
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node",
                parameters=[
                    robot_localization_config
                ]
            ),
            # SLAM TOOLBOX
            Node(
                package="slam_toolbox",
                executable="sync_slam_toolbox_node",
                name="sync_slam_toolbox_node",
                parameters=[
                    {
                        "odom_frame": "odom",
                        "base_frame": "meow_link",
                        "map_frame": "map",
                        "scan_topic": "/scan",
                        "scan_queue_size": 10,
                        "map_update_interval": 0.05,
                        # "position_covariance_scale": 1.0,
                        # "yaw_covariance_scale": 1.0,
                        "resolution": .13,
                        "min_laser_range": .15,
                        "max_laser_range": 12.0,
                        "use_scan_matching": True,
                        "do_loop_closing": True,
                        "use_scan_barycenter": True,
                        "minimum_travel_distance": .05,
                        "minimum_travel_heading": .05,
                        "correlation_search_space_dimension": .2,
                        "loop_search_space_dimension": 3.0,
                        "angle_variance_penalty": 0.0
                    }
                ]
            ),

            ## LAUNCH FILES

            # Teleop
            launch("teleop", "launch.py"),
            # Autobrake
            launch("controls", "autobrake_launch.py"),
            # Serial Communicator
            launch("serial_com", "launch.py"),
            # RPLidar
            launch("sllidar_ros2", "sllidar_a1_launch.py", arguments={"serial_port": "/dev/ttyUSB1"}),
            # Encoder Odometry (Ackermann)
            launch("encoder_odometry", "launch.py"),
        ]
    )
