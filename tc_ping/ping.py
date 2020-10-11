import gc
import socket
from tc_ping import errors
from tc_ping import statistics as st
from timeit import default_timer as timer
import time


class Ping:
    def __init__(self,
                 destination=None,
                 port=80,
                 pings_count=4,
                 timeout=0,
                 delay=0,
                 payload_size_bytes=32,
                 while_true=False,
                 use_ipv6=False,
                 output_level=2):
        self.destination = destination
        self.pings_count = int(pings_count)
        self.port = int(port)
        self.timeout = float(timeout)
        self.delay = int(delay)
        self.payload_size_bytes = int(payload_size_bytes)
        self.payload = self.__generate_payload()
        self.ip = None
        self.while_true = while_true
        self.use_ipv6 = use_ipv6
        self.output_level = int(output_level)

    def do_pings(self):
        benchmarks = []
        try:
            i = 0
            while True:
                bench = self.__do_one_ping()
                benchmarks.append(bench)
                time.sleep(self.delay)
                i += 1
                if not self.while_true and i == self.pings_count:
                    break
        except KeyboardInterrupt:
            pass
        except errors.PingError:
            raise

        if self.ip is None:
            addr = self.destination
        else:
            addr = self.ip
        stat_data = st.Statistics(benchmarks, addr, self.port)
        return stat_data

    def __time_benchmark(do_ping):
        def do_benchmark(self):
            gc.disable()
            start_time = timer()
            is_error = do_ping(self)
            end_time = timer()
            work_time = end_time - start_time
            gc.enable()
            stat_data = StatisticsData(work_time, is_error)
            return stat_data

        return do_benchmark

    def __write_ping_info(do_ping_after_benchmark):
        def write_info(self):
            stat_data = do_ping_after_benchmark(self)
            local_stat = ''
            if not stat_data.is_failed:
                local_stat = 'From: [{}:{}]: Payload bytes: {};' \
                             ' Time: {}ms;'.format(str(self.ip), str(self.port),
                                                   str(self.payload_size_bytes),
                                                   str(stat_data.time * 1000))
            else:
                local_stat = 'Failed'
            if self.output_level > 0:
                print(local_stat)
            return stat_data

        return write_info

    @__write_ping_info
    @__time_benchmark
    def __do_one_ping(self):
        is_error = False
        peer_name = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.use_ipv6:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            if self.timeout > 0:
                sock.settimeout(self.timeout)
            if not self.use_ipv6:
                sock.connect((self.destination, self.port))
            else:
                sock.connect((self.destination, self.port, 0, 0))
            peer_name = sock.getpeername()
            sock.sendall(self.payload)
            sock.shutdown(socket.SHUT_RD)
        except (socket.gaierror, socket.herror):
            raise errors.InvalidIpOrDomain
        except Exception as e:
            is_error = True
        if not is_error:
            if self.ip is None:
                self.ip = peer_name[0]
        return is_error

    def __generate_payload(self):
        return b'a' * self.payload_size_bytes


class StatisticsData:
    def __init__(self, time, is_failed):
        self.time = time
        self.is_failed = is_failed
