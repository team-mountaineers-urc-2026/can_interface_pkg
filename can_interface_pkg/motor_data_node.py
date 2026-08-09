import rclpy  
import can

from datetime import datetime

from rclpy.node import Node
from robot_interfaces.msg import CanCommand, MotorData
from myactuator_lib import Motor

'''
Note:

https://design.ros2.org/articles/legacy_interface_definition.html

    Default values for messages in ROS

        bool it is false
        numeric types it is a 0 value
        string it is an empty string
        arrays it is an array of N elements with its fields zero-initialized
        bounded size arrays and dynamic size arrays it is an empty array []

    (These values will exist in the topics being bagged when doing data logging)

'''
class MotorDataNode(Node):

    def __init__(self):
        super().__init__('motor_data_node')

        self.declare_parameter('incoming_can_reply_topic','recieved_can_messages')
        self.declare_parameter('motor_data_topic_name','motor_data')
        self.declare_parameter('can_topic_name','outgoing_can_commands')
        self.declare_parameter('pub_rate_hz',1.0)
        self.declare_parameter('include_arm',True)

        self.command_generator = Motor(0x141)


        self.reply_subscriber = self.create_subscription(
            CanCommand,
            self.get_parameter('incoming_can_reply_topic').get_parameter_value().string_value,
            self.parse_data,
            10,
        )
        
        self.can_command_publisher = self.create_publisher(
            CanCommand,
            self.get_parameter('can_topic_name').get_parameter_value().string_value,
            10,
        )

        self.motor_data_publisher = self.create_publisher(
            MotorData,
            self.get_parameter('motor_data_topic_name').get_parameter_value().string_value,
            10,
        )

        self.timer = self.create_timer( (1.0/self.get_parameter('pub_rate_hz').get_parameter_value().double_value), self.publish_data_request)

        self.motor_id_mappings_drivebase = {
            0x141 : 'front_left',
            0x142 : 'back_left',
            0x143 : 'front_right',
            0x144 : 'back_right',
        }

        self.motor_id_mappings_arm = {
            0x146 : 'shoulder',
            0x145 : 'elbow',
            0x149 : 'wrist_roll',
            0x148 : 'wrist_pitch',
            0x147 : 'linear_rail',
        }

        self.motor_id_mappings_combined = {**self.motor_id_mappings_arm, **self.motor_id_mappings_drivebase}

        self.error_status_dict: dict[int, str] = {
            0x0002 : "Motor stall",
            0x0004 : "Low pressure",
            0x0008 : "Overvoltage",
            0x0010 : "Overcurrent",
            0x0040 : "Power overrun",
            0x0080 : "Calibration parameter writing error",
            0x0100 : "Speeding",
            0x1000 : "Motor temperature over temperature",
            0x2000 : "Encoder",
        }

        self.break_lock_dict: dict[int, str]= {
            0 : 'locked',
            1 : 'released',
        }

        
    def parse_data(self, msg: CanCommand):

        new_data = MotorData()
        new_data.motor_id = msg.arbitration_id
        new_data.time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        motor_name = self.motor_id_mappings_combined.get(msg.arbitration_id - 256)
        self.get_logger().info(f'motor name: {motor_name}, type: {type(motor_name)}')
      
        if motor_name is not None:
            new_data.motor_name = motor_name

        if msg.byte_0 == 0xa2 or msg.byte_0 == 0x9c: # Speed and Motor Status 2 Reply
            new_data.temperature_celsius = float(msg.byte_1)
            new_data.torque_current_amps = float(((msg.byte_3 << 8) | msg.byte_2) / 100)
            new_data.speed_degrees_per_second = float((msg.byte_5 << 8) | msg.byte_4)
            new_data.angle_degrees = float((msg.byte_7 << 8) | msg.byte_6)
                
        elif msg.byte_0 == 0x9a: # Motor Status 1 Reply
            new_data.temperature_celsius = float(msg.byte_1)

            new_data.break_lock_status = self.break_lock_dict.get(msg.byte_3)
            new_data.voltage_volts = float(((msg.byte_5 << 8) | msg.byte_4) / 10)

            error_status = self.error_status_dict.get(((msg.byte_7 << 8) | msg.byte_6))
            if error_status:
                new_data.error_status = error_status
 
        elif msg.byte_0 == 0x9d: #  Motor Status 3 Reply
            new_data.temperature_celsius = float(msg.byte_1)
            new_data.phase_a_current_amps = float(((msg.byte_3 << 8) | msg.byte_2) / 100)
            new_data.phase_b_current_amps = float(((msg.byte_5 << 8) | msg.byte_4) / 100)
            new_data.phase_c_current_amps = float(((msg.byte_7 << 8) | msg.byte_6) / 100)
        
        self.motor_data_publisher.publish(new_data)


    def package_can_to_ros(self, can_command: can.Message)-> CanCommand:
 
        ros_msg = CanCommand()
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
    
    def publish_data_request(self):

        status_1 = can.Message(
            arbitration_id=321,
            data=[0x9a,0,0,0,0,50,0,0],
            is_extended_id=False
        )

        status_2 = can.Message(
            arbitration_id=321,
            data=[0x9c,0,0,0,0,0,0,0],
            is_extended_id=False
        )

        status_3 = can.Message(
            arbitration_id=321,
            data=[0x9d,0,0,0,0,0,0,0],
            is_extended_id=False
        )

        messages = [status_1,status_2,status_3]

        if self.get_parameter('include_arm').get_parameter_value().bool_value:
            motor_ids = self.motor_id_mappings_combined.keys()
        else:
            motor_ids = self.motor_id_mappings_drivebase.keys()

        for motor_id in motor_ids:
            for message in messages:

                message.arbitration_id = motor_id
                self.get_logger().info(f'arb id: {message.arbitration_id}')
                self.get_logger().info(f'data: {message.data}')

        self.can_command_publisher.publish(self.package_can_to_ros(status_1))


      
def main():
    rclpy.init()
    send_can_service = MotorDataNode()
    rclpy.spin(send_can_service)
    rclpy.shutdown()


if __name__ == '__main__':
    main()


