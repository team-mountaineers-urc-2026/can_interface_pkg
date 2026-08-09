import rclpy, threading 
from rclpy.node import Node
import can

from controls_msgs.msg import CanMessage

class CanSubscriberNode(Node):

    thread_lock = threading.Lock()

    def __init__(self):
        super().__init__('can_subscriber_node')

        self.declare_parameter('can_topic_name','outgoing_can_commands')
        self.declare_parameter('can_data_topic_name','recieved_can_messages')

        self.declare_parameter('can_interface','socketcan')
        self.declare_parameter('can_channel','can0')
        self.declare_parameter('is_extended_id',False)
        self.declare_parameter('can_bitrate',1000000)

        self.declare_parameter('can_timeout_seconds',0.10)
        self.declare_parameter('debugging',False)

        self.can_command_sub = self.create_subscription(
            CanMessage,
            'outgoing_can_commands',
            self.send_can_command,
            10,
        )

        self.data_pub = self.create_publisher(
            CanMessage,
            'recieved_can_messages',
            10,
        )

        self.bus = can.Bus(
            interface = self.get_parameter('can_interface').get_parameter_value().string_value, 
            channel = self.get_parameter('can_channel').get_parameter_value().string_value, 
            is_extended_id = self.get_parameter('is_extended_id').get_parameter_value().string_value,
            bitrate = self.get_parameter('can_bitrate').get_parameter_value().string_value,
        )

    def package_can_to_ros(self, can_command: can.Message)-> CanMessage:
 
        ros_msg = CanMessage()
        ros_msg.arbitration_id = can_command.arbitration_id
        ros_msg.is_extended_id = can_command.is_extended_id
        ros_msg.byte_0 = can_command.data[0]
        ros_msg.byte_1 = can_command.data[1]
        ros_msg.byte_2 = can_command.data[2]
        ros_msg.byte_3 = can_command.data[3]
        ros_msg.byte_4 = can_command.data[4]
        ros_msg.byte_5 = can_command.data[5]
        ros_msg.byte_6 = can_command.data[6]
        ros_msg.byte_7 = can_command.data[7]

        return ros_msg

    def send_can_command(self, msg: CanMessage):
        can_command = can.Message(
            arbitration_id= msg.arbitration_id,
            is_extended_id= msg.is_extended_id,
            data = [
                msg.byte_0,
                msg.byte_1,
                msg.byte_2,
                msg.byte_3,
                msg.byte_4,
                msg.byte_5,
                msg.byte_6,
                msg.byte_7,
            ]
        )

        try:
            with CanSubscriberNode.thread_lock:
                self.bus.send(can_command)
                recieved_message = self.bus.recv(0.10)

                if recieved_message:
                    self.data_pub.publish(self.package_can_to_ros(recieved_message))
                elif recieved_message == None:
                    self.get_logger().error(f"Motor: {msg.arbitration_id} is not connected -> Hardware")
                else:
                    self.get_logger().info(f'did not recieve data (recieved message was of type {type(recieved_message)})')

        except Exception as error:    
            self.get_logger().warn(f'can_subscriber_node:\nError:{error}\nTraceback:{error.with_traceback}')

def main():
    rclpy.init()
    send_can_service = CanSubscriberNode()
    rclpy.spin(send_can_service)
    rclpy.shutdown()


if __name__ == '__main__':
    main()