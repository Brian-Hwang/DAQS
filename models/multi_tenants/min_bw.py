import time
from datetime import datetime
import utils.guest_manager as gm
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg


IGNORE_BW_THRESHOLD_GBPS = 1 # 1Gbps 이하로 사용 중인 것은 무시

MARGINAL_RATE = 1.1 # guaranteed에 대해서 적용할 마진 비율
MARGINAL_OFFEST = 0 # guaranteed에 대해서 적용할 마진값

STEP_GBPS = 1 # 조정할 속도 단위


class MinBandwidthManager:

    def __init__(self):
        self.host_interface = cfg.read_host_interface()
        self.host_bandwidth = host.get_bandwidth(self.host_interface)

        self.vms = {}
        self.last_time = -1
        self.period = 1 # 주기 1초
        self.last_time = datetime.now()
        self.regulated_speed = -1
        self.guaranteed_vms = cfg.read_guaranteed_vms()

    def start(self):
        self.last_time = datetime.now()
        self.run()


    def schedule_run(self):
        # 주기적으로 실행하게끔 시간 보정
        while True:
            # 이미 주기가 지났다면 한 주기 더 대기
            if datetime.now() - self.last_time > self.period:
                self.last_time += self.period
                continue            
            time.sleep(self.period - (datetime.now() - self.last_time))
            break
        self.last_time = datetime.now()
        self.run()

    
    def run(self):
        vms = host.get_running_vms()
        if vms is None:
            self.schedule_run()

        for vm in vms:
            if vm in self.vms.keys():
                continue
            self.vms[vm] = gm.GuestManager(vm)

        for key, value in self.vms.items():
            if key not in vms:
                del self.vms[key]

        # Assume that there are two VMs
        # one is guaranteed, the other is not.

        guaranteed_speed = 0
        for name, spd in self.guaranteed_vms:
            if name in vms.keys():
                guaranteed_speed += spd
        
        current_speed = 0       
        total_speed = 0
        for vm in vms:
            spd = self.vms[vm].get_tx_speed_mbps() / (2.0**10) # Gbps
            if vm in self.guaranteed_vms.keys():
                # guaranteed vm
                current_speed += spd
                total_speed += spd
            else:
                # not guaranteed vm
                total_speed += spd

        if current_speed < IGNORE_BW_THRESHOLD_GBPS: # 사용중이지 않은 것으로 간주
            self.regulated_speed = -1        

        if current_speed < guaranteed_speed: # 침해 중
            if self.regulated_speed == -1:
                self.regulated_speed = self.host_bandwidth - guaranteed_speed
            else:
                self.regulated_speed -= STEP_GBPS
        
        if current_speed > guaranteed_speed * MARGINAL_RATE + MARGINAL_OFFEST: # 초과하여 사용 중
            if self.total_speed - self.current_speed > IGNORE_BW_THRESHOLD_GBPS: # 다른 것이 사용 중인 경우에
                self.regulated_speed += STEP_GBPS

        if self.regulated_speed > 0:
            for vm in vms:
                if vm in self.guaranteed_vms.keys():
                    continue
                tc.set_bandwidth_limit(vm, self.vms[vm].iface, self.regulated_speed)

        self.schedule_run()
            

if __name__ == "__main__":
    manager = MinBandwidthManager()
    manager.start()
