import rclpy, time, can
from robot_interfaces.srv import SendCanCommand
from geometry_msgs.msg import Twist
from rclpy.node import Node
from myactuator_lib import Motor as mt

class CanTestClient(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        
        self.can_service_client = self.create_client(SendCanCommand, 'send_n_reply_can_msg')
        while not self.can_service_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        
        self.joy_sub = self.create_subscription(Twist, 'cmd_vel', self.spin_callback, 10)

        self.req = SendCanCommand.Request()

    def send_request(self, can_msg: can.Message):
        self.req.arbitration_id = can_msg.arbitration_id
        self.req.is_extended_id = can_msg.is_extended_id
        self.req.byte_0 = can_msg.data[0]
        self.req.byte_1 = can_msg.data[1]
        self.req.byte_2 = can_msg.data[2]
        self.req.byte_3 = can_msg.data[3]
        self.req.byte_4 = can_msg.data[4]
        self.req.byte_5 = can_msg.data[5]
        self.req.byte_6 = can_msg.data[6]
        self.req.byte_7 = can_msg.data[7]
        self.future = self.can_service_client.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
    
    def spin_callback(self, twist_msg):
        motor = mt(0x141)
        msg = motor.Speed_Closed_loop_Control_Command(twist_msg.linear.x * 100)
        response = self.send_request(msg)
        self.get_logger().info(f'response: {response}')


def main():
    rclpy.init()
    can_service_client = CanTestClient()
    rclpy.spin(can_service_client)
    can_service_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()