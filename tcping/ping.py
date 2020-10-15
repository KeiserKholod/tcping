import gc
import socket
from tcping import errors
import time


class StatisticsData(float):
    def __init__(self, time: float, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port
        self.is_failed = False
        if time < 0:
            self.is_failed = True


class time_measure:
    def __init__(self):
        self.start_time = 0
        self.work_time = 0

    def __enter__(self):
        gc.disable()
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.work_time = time.perf_counter() - self.start_time
        gc.enable()


class TCPing:
    def __init__(self,
                 destination=None,
                 port=80,
                 timeout=0,
                 use_ipv6=False):
        self.destination = destination
        self.port = int(port)
        self.timeout = float(timeout)
        self.ip = None
        self.use_ipv6 = use_ipv6
        self.measures = []

    def do_ping(self):
        work_time = self.ping()
        measure = StatisticsData(work_time, ip=self.ip, port=self.port)
        self.measures.append(measure)
        return measure

    def ping(self) -> float:
        addr = (self.destination, self.port)
        family_addr = socket.AF_INET
        if self.use_ipv6:
            family_addr = socket.AF_INET6
            addr = (*addr, 0, 0)
        sock = socket.socket(family_addr, socket.SOCK_STREAM)
        if self.timeout > 0:
            sock.settimeout(self.timeout)
        try:
            with time_measure() as measure:
                sock.connect(addr)
                sock.sendall(b'a')
            if self.ip is None:
                self.ip = sock.getpeername()[0]
            sock.shutdown(socket.SHUT_RD)
            return measure.work_time
        except (socket.gaierror, socket.herror):
            raise errors.InvalidIpOrDomain
        except (ConnectionRefusedError, socket.timeout):
            return -1
        finally:
            sock.close()

    @staticmethod
    def prepare_ping_info(stat_data: StatisticsData):
        if stat_data.is_failed:
            return 'Failed;'
        return 'From: [{}:{}]; Time: {}ms;'.format(str(stat_data.ip),
                                                   str(stat_data.port),
                                                   str(stat_data * 1000))
