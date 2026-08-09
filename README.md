# can_interface_pkg

## Overview

This ROS 2 package provides a set of nodes for interacting with a Controller Area Network (CAN) bus. The package includes two nodes: `can_service_node` and `can_subscriber_node`. These nodes allow you to send and receive CAN messages, facilitating communication with devices on the CAN bus.

## Nodes

### Node: can_service_node

This node provides a service to send CAN commands. It initializes a CAN bus and sends messages based on incoming service requests.

#### Parameters

- **can_srv_name**: Name of the ROS service for sending and receiving CAN commands (default: 'send_n_recv_can_msg').
- **can_interface**: Type of CAN interface (default: 'socketcan').
- **can_channel**: CAN channel to be used (default: 'can0').
- **is_extended_id**: Flag indicating whether extended CAN identifiers are used (default: False).
- **can_bitrate**: Bitrate of the CAN bus in bits per second (default: 1000000).
- **can_timeout_seconds**: Timeout for sending and receiving CAN messages in seconds (default: 0.05).
- **debugging**: Enable or disable debugging output (default: False).

#### Services

- **/send_n_recv_can_msg**: Service for sending CAN commands and receiving the corresponding response.

### Node: can_subscriber_node

This node subscribes to a specified ROS topic for incoming CAN commands and sends them over the CAN bus.

#### Parameters

- **can_topic_name**: ROS topic name for incoming CAN commands (default: 'outgoing_can_commands').
- **can_interface**: Type of CAN interface (default: 'socketcan').
- **can_channel**: CAN channel to be used (default: 'can0').
- **is_extended_id**: Flag indicating whether extended CAN identifiers are used (default: False).
- **can_bitrate**: Bitrate of the CAN bus in bits per second (default: 1000000).
- **can_timeout_seconds**: Timeout for sending CAN messages in seconds (default: 0.05).
- **debugging**: Enable or disable debugging output (default: False).

#### Subscribed Topics

- **/outgoing_can_commands**: Incoming CAN commands to be sent over the CAN bus, with message type `robot_interfaces/CanCommand`.

## Building and Running

1. Clone this package into your ROS 2 workspace. This will probably be inside of your virtual machine.

If you are cloning with ssh:
```bash
cd <path_to_your_workspace>
cd src
git clone git@github.com:wvu-urc/can_interface_pkg.git
```

If you are cloning with a token:
```bash
cd <path_to_your_workspace>
cd src
git clone https://github.com/wvu-urc/can_interface_pkg.git
```

2. Build the ROS 2 workspace.

```bash
cd ..
colcon build
```

3. Source the ROS 2 workspace.

```bash
source install/setup.bash
```

4. Run the `can_service_node`.

```bash
ros2 run can_interface_pkg can_service_node
```

5. Open a new terminal (Ctrl + Shift + n) and run the `can_subscriber_node`.

```bash
ros2 run can_interface_pkg can_subscriber_node
```

6. Ensure that the `outgoing_can_commands` topic is being published with appropriate `robot_interfaces/CanCommand` messages.

## Additional Notes

- Make sure the CAN bus is properly connected and accessible at the specified channel.
- Check the udev rules for your CAN interface to ensure proper permissions.
- For debugging, you can set the `debugging` parameter to True in the launch files or directly from the command line.

## Known Limitations
There are no known limitations of this package. CAN itself can be difficult to work with, if you are having trouble getting it to work check the following things:

run `candump can0` or whatever you have your network named as, this will show you the actual commands being sent

If you are using MyActuator Motors, Each motor (addressed at 0x1XX) will respond at 0x2XX. These are hexadecimal so make sure you aren't accidentally using decimal

If the buffer is being filled up that most likely means that a motor or device isn't present on the network. Ensure all wires are plugged in correctly and each motor can be controlled independently when it is the only thing on the CAN Network.

If worse comes to worse, start with one motor that works over CAN and slowly change things effectivly 'sneaking' it onto the robot. Robots know when you are trying to get something to work and sometimes sabotage your efforts but they can be tricked if things are done slowly enough.
