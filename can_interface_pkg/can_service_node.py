import rclpy, can, threading
from rclpy.node import Node
from robot_interfaces.srv import SendCanCommand

class CanService(Node):
    # thread_lock = threading.Lock()
    
    def __init__(self):
        super().__init__('can_service_node')

        self.declare_parameter('can_srv_name','send_n_reply_can_msg')
        self.declare_parameter('can_interface','socketcan')
        self.declare_parameter('can_channel','can0')
        self.declare_parameter('is_extended_id',False)
        self.declare_parameter('can_bitrate',1000000)

        self.declare_parameter('can_timeout_seconds',0.05)
        self.declare_parameter('debugging',False)


        self.srv = self.create_service(
            SendCanCommand,
            self.get_parameter('can_srv_name').get_parameter_value().string_value,
            self.send_can_command,
        )

        self.bus = can.Bus(
            interface = 'socketcan', # self.get_parameter('can_interface').get_parameter_value().string_value, 
            channel = 'can0', # self.get_parameter('can_channel').get_parameter_value().string_value, 
            is_extended_id = False, # self.get_parameter('is_extended_id').get_parameter_value().bool_value,
            bitrate = 1000000, # self.get_parameter('can_bitrate').get_parameter_value().integer_value,
        )

    def send_can_command(self, request, response) -> SendCanCommand.Response:
        can_command = can.Message(
            arbitration_id= request.arbitration_id,
            is_extended_id= request.is_extended_id,
            data = [
                request.byte_0,
                request.byte_1,
                request.byte_2,
                request.byte_3,
                request.byte_4,
                request.byte_5,
                request.byte_6,
                request.byte_7
                ]
            )
        
        # with CanService.thread_lock:
        self.get_logger().info(f'Sending command {can_command}')

        self.bus.send(can_command)

        response_can_msg: can.Message = self.bus.recv(timeout=0.1)
        self.get_logger().info(f'Recieved response {response_can_msg}')

        response.timestamp = response_can_msg.timestamp
        response.recv_arbitration_id = response_can_msg.arbitration_id
        response.recv_byte_0 = response_can_msg.data[0]
        response.recv_byte_1 = response_can_msg.data[1]
        response.recv_byte_2 = response_can_msg.data[2]
        response.recv_byte_3 = response_can_msg.data[3]
        response.recv_byte_4 = response_can_msg.data[4]
        response.recv_byte_5 = response_can_msg.data[5]
        response.recv_byte_6 = response_can_msg.data[6]
        response.recv_byte_7 = response_can_msg.data[7]

        self.get_logger().info(f'Returning response {response}')
        return response

def main():
    rclpy.init()
    can_srv_node = CanService()
    rclpy.spin(can_srv_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()