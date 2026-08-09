import launch
import launch_ros.actions
from launch.actions import ExecuteProcess


def generate_launch_description():


    launch_description = launch.LaunchDescription()

    launch_description.add_action(
            launch_ros.actions.Node(
            package='can_interface_pkg',
            executable='can_subscriber_node',
            name='can_subscriber_node')
        )
    
    launch_description.add_action(
            ExecuteProcess(
                cmd=["sudo", "/sbin/ip", "link", "set", "can0", "up", "type", "can", "bitrate", "1000000",],
            )
        )
    return launch_description