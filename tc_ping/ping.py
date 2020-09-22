import socket


class Ping:
    def __init__(self,
                 destination=None,
                 port=80,
                 pings_count=4,
                 timeout=0,
                 delay=0,
                 payload_size_bytes=32):
        self.destination = destination
        self.pings_count = pings_count
        self.port = int(port)
        self.timeout = int(timeout)
        self.delay = int(delay)
        self.payload_size_bytes = int(payload_size_bytes)

    def do_pings(self):
        self.__do_one_ping()

    def __do_one_ping(self):
        payload = self.__generate_payload()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.destination, self.port))
            if self.timeout > 0:
                sock.settimeout(self.timeout)
                sock.sendall(payload)
                sock.shutdown(socket.SHUT_RD)

    def __generate_payload(self):
        return b'a' * self.payload_size_bytes

    def __do_log(self, do_ping):
        """decorator to take time and successfulness of single response"""
        pass
