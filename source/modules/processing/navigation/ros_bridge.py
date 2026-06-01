import rclpy

from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid

class ROSBridge(Node):

    def __init__(self):

        super().__init__("carton_bridge")

        self.scan = None
        self.map = None

        self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

        self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            10
        )

    def scan_callback(self,msg):
        self.scan = msg

    def map_callback(self,msg):
        self.map = msg