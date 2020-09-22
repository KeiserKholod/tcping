import gc
import socket
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
        self.timeout = int(timeout)
        self.delay = int(delay)
        self.payload_size_bytes = int(payload_size_bytes)
        self.payload = self.__generate_payload()

    def do_pings(self):
        for i in range(0, self.pings_count):
            print(self.__do_one_ping() * 1000)

    def __time_benchmark(do_ping):
        def do_benchmark(self):
            gc.disable()
            start_time = timer()
            do_ping(self)
            end_time = timer()
            work_time = end_time - start_time
            gc.enable()
            return work_time

        return do_benchmark

    @__time_benchmark
    def __do_one_ping(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.destination, self.port))
            if self.timeout > 0:
                sock.settimeout(self.timeout)
                sock.sendall(self.payload)
                sock.shutdown(socket.SHUT_RD)

    def __generate_payload(self):
        return b'a' * self.payload_size_bytes
