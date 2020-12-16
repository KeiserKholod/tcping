import gc
import socket
from tcping import errors
import time
from enum import Enum
import tcping.tcp_package as tcp_package
from typing import Optional


class ConnectionType(Enum):
    CONNECT = 1
    RAW_SOCKET = 2


class StatisticsData(float):
    """Contains information about ping duration, destination ip and port
    in case of exception in ping,
     time equals -1 and field is_failed equals True."""

    def __init__(self, time: float, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port
        self.is_failed = False
        if time < 0:
            self.is_failed = True

    def __str__(self):
        """Return string with information about duration,
         destination ip and por and status of a single ping"""

        answer = 'From: [{}:{}];'.format(str(self.ip),
                                         str(self.port))
        if self.is_failed:
            return ' '.join((answer, 'Failed;'))
        return ' '.join((answer, 'Time: {}ms;'
                         .format(str(round(self * 1000, 3)))))


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
                 destination: Optional[str] = None,
                 port: int = 80,
                 timeout: float = 0,
                 use_ipv6: bool = False):
        self.destination = destination
        self.port = int(port)
        self.timeout = float(timeout)
        self.ip = None
        self.use_ipv6: bool = use_ipv6
        self.measures = []

    def do_ping(self, option=ConnectionType.CONNECT) -> StatisticsData:
        """Do one ping and return StatisticsData object."""

        if option == ConnectionType.CONNECT:
            work_time = self.ping_with_connect()
        else:
            work_time = self.ping_with_raw_socket()
        measure = StatisticsData(work_time, ip=self.ip, port=self.port)
        self.measures.append(measure)
        return measure

    def ping_with_raw_socket(self) -> float:
        """Does TCP handshake by raw socket.
         Return duration of handshake; in case of exception return -1."""

        source_ip: str = "192.168.0.1"
        source_port: int = 0
        dest_ip: str = socket.gethostbyname(self.destination)
        if self.ip is None:
            self.ip = dest_ip
        seq: int = 0
        ack_seq: int = 0
        syn_pack = bytes(
            tcp_package.TCPPackage(flags=tcp_package.TCPPackageType.SYN,
                                   source_ip=source_ip,
                                   dest_ip=dest_ip,
                                   dest_port=self.port,
                                   seq=seq,
                                   ack_seq=ack_seq,
                                   source_port=source_port))
        try:
            sock = socket.socket(socket.AF_INET,
                                 socket.SOCK_RAW,
                                 socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.settimeout(self.timeout)
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
                syn_ack_pack = tcp_package \
                    .TCPPackage \
                    .parse_tcp_ipv4_package(response)
                if syn_ack_pack.seq != seq + 1:
                    return -1
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
