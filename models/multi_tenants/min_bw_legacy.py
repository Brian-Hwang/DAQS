import time
import datetime
import utils.guest_manager as gm
import utils.traffic_control as tc
import utils.guest_utils as guest
import utils.host_utils as host
import utils.read_config as cfg


MONITOR_PERIOD = datetime.timedelta(milliseconds=0.3)  # 매니저 실행 주기

IGNORE_BW_THRESHOLD_GBPS = 1  # 1Gbps 이하로 사용 중인 것은 무시

MARGINAL_RATE = 1  # guaranteed에 대해서 적용할 마진 비율
MARGINAL_OFFEST = 1  # guaranteed에 대해서 적용할 마진값

STEP_GBPS = 0.4  # 조정할 속도 단위

TOLERANT_USAGE_RATE = 1.0 - 0.07*2  # 전체 BW 대비 이 비율 이상 사용 중일 때만 더 가혹하게 TC 조절


class MinBandwidthManager:
    """
    최소 BW 보장 매니저
    """

    def __init__(self):
        """
        초기값 설정
        """
        self.host_interface = cfg.read_host_interface()  # 호스트 인터페이스 확인
        self.host_bandwidth = host.get_bandwidth(
            self.host_interface)  # 해당 인터페이스 BW 확인

        self.vms = {}  # 실행 중인 VM의 GuestManager 객체 맵, key: 이름, value: GuestManager 객체
        self.period = MONITOR_PERIOD  # 매니저 실행 주기
        self.last_time = datetime.datetime.now()  # 마지막 매니저 실행 datetime
        self.regulated_speed = -1  # Best-Effort VM에 적용할 속도
        self.guaranteed_vms = cfg.read_guaranteed_vms()  # 보장 VM 목록
        self.running = False  # 매니저 실행 중 여부

        print(f"Manager init. Guaranteed VMs: {self.guaranteed_vms}")

    def start(self):
        """
        매니저 시작
        """
        self.last_time = datetime.datetime.now()
        self.schedule_run()

    def schedule_run(self):
        """
        지정된 시간(self.period) 단위로 매니저 실행
        """
        while True:
            if self.running:  # 실행 중이면 대기
                continue
            duration = self.period - (datetime.datetime.now() - self.last_time)
            duration = duration.total_seconds()
            if duration <= 0:  # 이미 주기가 지났다면 한 주기 더 대기
                self.last_time += self.period
                continue
            time.sleep(duration)
            self.last_time = datetime.datetime.now()
            self.run()

    def loosen_best_effort(self):
        self.regulated_speed += STEP_GBPS
        if self.regulated_speed > self.host_bandwidth:  # 최대 TC 제한
            self.regulated_speed = self.host_bandwidth

    def fasten_best_effort(self):
        self.regulated_speed -= STEP_GBPS
        if self.regulated_speed <= 1:  # 1 이하의 경우 1로 설정 (최소 연결 보장)
            self.regulated_speed = 1

    def run(self):
        """
        매니저 실행
        최소 BW 보장을 위해 Best-Effort VM에 대해 속도 조정
        Guaranteed VM들의 속도가 실제로 보장되고 있는지 확인하여,
        침해받고 있다면 Best-Effort VM의 속도를 낮추고
        일정 margin(MARGINAL_RATE, MARGINAL_OFFEST)을 초과하여 사용 중이라면 
        Best-Effort VM의 속도를 높인다.

        우선 두 개의 VM에 대해서만 적용하도록 한다.
        1개의 Guaranteed VM과 1개의 Best-Effort VM가 있다고 가정함.
        """

        self.running = True

        running_vms = host.get_running_vms()  # 실행 중인 VM 확인
        if running_vms is None:
            self.running = False
            return

        for vm in running_vms:  # VM의 GuestManager 인스턴스 관리
            if vm in self.vms:
                continue
            self.vms[vm] = gm.GuestManager(vm)
        for key, value in self.vms.items():  # 무효한 인스턴스 삭제
            if key not in running_vms:
                del self.vms[key]

        guaranteed_speed = 0  # 보장해야 하는 총 속도 확인 (추후 확장 대비)
        for name, spd in self.guaranteed_vms.items():
            if name in running_vms:
                guaranteed_speed += spd

        print(f"VMs: {running_vms}, Goal guaranteed speed: {guaranteed_speed}")

        current_speed = 0  # Guaranteed VM들의 현재 속도 합
        total_speed = 0  # 모든 VM의 현재 속도 합
        for vm in running_vms:
            spd = self.vms[vm].get_tx_speed_mbps() / (2.0**10)  # Gbps
            if vm in self.guaranteed_vms.keys():
                # guaranteed vm
                current_speed += spd
                total_speed += spd
            else:
                # not guaranteed vm
                total_speed += spd

        if current_speed < IGNORE_BW_THRESHOLD_GBPS:  # 사용중이지 않은 것으로 간주
            self.regulated_speed = -1

        elif current_speed < guaranteed_speed:  # 침해 중, Best-Effort VM에 더 가혹한 TC 적용
            if self.regulated_speed == -1:
                self.regulated_speed = self.host_bandwidth - guaranteed_speed
            else:
                if self.host_bandwidth * TOLERANT_USAGE_RATE <= total_speed:  # 전체 BW 대비 사용량이 일정 비율 이상인 경우에만 조정
                    self.fasten_best_effort()
                elif self.host_bandwidth * TOLERANT_USAGE_RATE > total_speed + STEP_GBPS:  # 여유가 있을 경우 오히려 관대하게 조정해보기
                    self.loosen_best_effort()

        # 초과하여 사용 중, Best-Effort VM에 더 관대한 TC 적용
        elif current_speed > guaranteed_speed * MARGINAL_RATE + MARGINAL_OFFEST:
            if total_speed - current_speed > IGNORE_BW_THRESHOLD_GBPS:  # 다른 VM들이 충분히 사용 중인 경우에만 적용
                self.loosen_best_effort()

        if self.regulated_speed == -1 or self.regulated_speed >= self.host_bandwidth:  # TC 제거
            for vm in running_vms:
                tc.delete_queue_discipline(vm, self.vms[vm].iface)

        elif self.regulated_speed > 0:  # TC 적용
            for vm in running_vms:
                if vm in self.guaranteed_vms.keys():
                    continue
                tc.set_bandwidth_limit_mbps(
                    vm, self.vms[vm].iface, self.regulated_speed * (2.0**10))  # Gbps -> Mbps

        print(
            f"Total speed {total_speed}, guaranteed group {current_speed}, regulated speed {self.regulated_speed}")

        self.running = False


def run_min_bw():
    """
    매니저 생성 후 실행
    """
    manager = MinBandwidthManager()
    manager.start()


if __name__ == "__main__":
    run_min_bw()
