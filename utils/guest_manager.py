import time
from datetime import datetime
from utils import guest_agent
from utils import guest_utils

class GuestManager:
    def __init__(self, name):
        self.name = name
        self.iface = guest_utils.get_last_network_interface(name)
        self.last_time = datetime.now()
        self.last_bytes = -1

    def get_tx_speed_mbps(self):
        """
        Checks the amount of data transmitted by a VM's network interface in Mbps.
        Returns -1 for the first call
        """

        prev_time = self.last_time
        prev_bytes = self.last_bytes

        # Get the current transmitted gbits
        self.last_time = datetime.now()
        self.last_bytes = guest_utils.check_tx_gbits(self.name, self.iface)

        if prev_bytes == -1:
            return -1
        
        time_diff = (self.last_time - prev_time).total_seconds()
        bytes_diff = self.last_bytes - prev_bytes
        return float(bytes_diff) / float(time_diff)
    
        