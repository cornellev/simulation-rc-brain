import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def get_path(package, dir, file):
    return os.path.join(get_package_share_directory(package), dir, file)


def launch(package, file, launch_folder="launch", arguments={}):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(get_path(package, launch_folder, file)),
        launch_arguments=arguments.items(),
    )


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory("vision"), "config", "occupancy.yaml"
    )

    return LaunchDescription(
        [
            Node(
                package="vision",
                executable="occupancy_transformer",
                name="occupancy_transformer",
                parameters=[config, {"use_sim_time": True}],
            ),
        ]
    )
