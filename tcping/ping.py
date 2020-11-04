import gc
import socket
from tcping import errors
import time


class StatisticsData(float):
    """Contains information about ping duration, destination ip and port
    in case of exception in ping, time equals -1 and field is_failed equals True."""

    def __init__(self, time: float, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port
        self.is_failed = False
        if time < 0:
            self.is_failed = True


class TimeMeasure:
    """Context manager for ping duration measuring."""

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
    """Contains methods to do async ping and get info about ping."""

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

    async def do_ping(self):
        """Do one ping and return StatisticsData object."""

        work_time = self.ping()
        measure = StatisticsData(work_time, ip=self.ip, port=self.port)
        self.measures.append(measure)
        return measure

    def ping(self) -> float:
        """Do one ping and return time of ping duration.
         In case of exception, return -1."""

        addr = (self.destination, self.port)
        family_addr = socket.AF_INET
        if self.use_ipv6:
            family_addr = socket.AF_INET6
            addr = (*addr, 0, 0)
        sock = socket.socket(family_addr, socket.SOCK_STREAM)
        if self.timeout > 0:
            sock.settimeout(self.timeout)
        try:
            if self.ip is None:
                self.ip = socket.gethostbyname(self.destination)
            with TimeMeasure() as measure:
                sock.connect(addr)
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
        """Return string with information about duration,
         destination ip and por and status of a single ping"""

        if stat_data.is_failed:
            return 'From: [{}:{}]; Failed;'.format(str(stat_data.ip),
                                                   str(stat_data.port))
        return 'From: [{}:{}]; Time: {}ms;'.format(str(stat_data.ip),
                                                   str(stat_data.port),
                                                   str(round(stat_data * 1000, 3)))
