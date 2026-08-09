import os 
from glob import glob # NEED TO ADD THIS FOR EVERY NEW LAUNCH FILE 
from setuptools import find_packages, setup # NEED TO ADD THIS FOR EVERY NEW LAUNCH FILE 

package_name = 'can_interface_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))), # NEED TO ADD THIS FOR EVERY NEW LAUNCH FILE 
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml'))

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nate',
    maintainer_email='npa00003@mix.wvu.edu',
    description='TODO: Package description',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'can_service_node = can_interface_pkg.can_service_node:main',
            'can_subscriber_node = can_interface_pkg.can_subscriber_node:main',
            'test_client_node = can_interface_pkg.test_client_node:main',
            'motor_data_node = can_interface_pkg.motor_data_node:main',
        ],
    },
)
