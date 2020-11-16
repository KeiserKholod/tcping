import gc
import socket
from tcping import errors
import time
from enum import Enum
import tcping.tcp_package as tcp_package


class Option(Enum):
    CONNECT = 1
    RAW_SOCKET = 2


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

    async def do_ping(self, option=Option.CONNECT):
        """Do one ping and return StatisticsData object."""
        if option == Option.CONNECT:
            work_time = self.ping_with_connect()
        else:
            work_time = 0
        measure = StatisticsData(work_time, ip=self.ip, port=self.port)
        self.measures.append(measure)
        return measure

    def ping_with_raw_socket(self):
        """Does TCP handshake by raw socket.
         Return duration of handshake; in case of exception return -1."""

        syn_flags = {"fin": 0,

                     "syn": 1,
                     "rst": 0,
                     "psh": 0,
                     "ack": 0,
                     "urg": 0}
        ack_flags = {"fin": 0,
                     "syn": 0,
                     "rst": 0,
                     "psh": 0,
                     "ack": 1,
                     "urg": 0}
        source_ip = "192.168.0.1"
        source_port = 1234
        dest_ip = socket.gethostbyname(self.destination)
        seq = 0
        ack_seq = 0
        syn_pack = tcp_package.TCPPackage(flags=syn_flags, source_ip=source_ip,
                                          dest_ip=dest_ip, dest_port=self.port,
                                          seq=seq, ack_seq=ack_seq,
                                          source_port=source_port).__bytes__()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            with TimeMeasure() as measure:
                # send syn
                sock.sendto(syn_pack, (dest_ip, self.port))
                response = None
                # recive ack
                while measure.work_time <= self.timeout and response is None:
                    response = sock.recvfrom(4096)[0]
                    if response is not None:
                        if not (response[1] == socket.inet_aton(dest_ip)):
                            response = None
                if response is None:
                    return -1
                syn_ack_pack = tcp_package.TCPPackage.parse_tcp_ipv4_package(response)
                if syn_ack_pack.seq != seq + 1:
                    return -1
                seq = syn_ack_pack.seq + 1
                ack_seq = syn_ack_pack.ack_seq + 1
                ack_pack = tcp_package.TCPPackage(flags=ack_flags, source_ip=source_ip,
                                                  dest_ip=dest_ip, dest_port=self.port,
                                                  seq=seq, ack_seq=ack_seq,
                                                  source_port=source_port).__bytes__()
                sock.sendto(ack_pack, (dest_ip, self.port))
            return measure.work_time
        except (socket.gaierror, socket.herror):
            raise errors.InvalidIpOrDomain

    def ping_with_connect(self) -> float:
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
