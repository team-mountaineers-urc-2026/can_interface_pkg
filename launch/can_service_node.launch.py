import launch
import launch_ros.actions
from launch.actions import ExecuteProcess


def generate_launch_description():


    launch_description = launch.LaunchDescription()

    launch_description.add_action(
            launch_ros.actions.Node(
            package='can_interface_pkg',
            executable='can_service_node',
            name='can_service_node')
        )
    
    return launch_description