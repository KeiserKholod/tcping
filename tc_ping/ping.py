import gc
import socket
from tc_ping import errors
from tc_ping import statistic as st
from timeit import default_timer as timer


class Ping:
    def __init__(self,
                 destination=None,
                 port=80,
                 pings_count=4,
                 timeout=0,
                 delay=0,
                 payload_size_bytes=32):
        self.destination = destination
        self.pings_count = int(pings_count)
        self.port = int(port)
        self.timeout = float(timeout)
        self.delay = int(delay)
        self.payload_size_bytes = int(payload_size_bytes)
        self.payload = self.__generate_payload()

    def do_pings(self):
        benchmarks = []
        for i in range(0, self.pings_count):
            bench = self.__do_one_ping()
            print(str(bench[0] * 1000))
            benchmarks.append(bench)
        stat = st.Statistic(benchmarks)
        print(stat)

    def __time_benchmark(do_ping):
        def do_benchmark(self):
            gc.disable()
            start_time = timer()
            info = do_ping(self)
            end_time = timer()
            work_time = end_time - start_time
            gc.enable()
            return work_time, info[0], info[1]

        return do_benchmark

    @__time_benchmark
    def __do_one_ping(self):
        is_error = False
        peer_name = ''
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.destination, self.port))
            peer_name = sock.getpeername()
            if self.timeout > 0:
                sock.settimeout(self.timeout)
                sock.sendall(self.payload)
                sock.shutdown(socket.SHUT_RD)
        except socket.gaierror or socket.herror:
            raise errors.InvalidIpOrDomain
        except Exception as e:
            is_error = True
            raise e
        return is_error, peer_name

    def __generate_payload(self):
        return b'a' * self.payload_size_bytes
