from struct import *
import socket


class TCPPackage:
    def __init__(self, flags={"fin": 0,
                              "syn": 1,
                              "rst": 0,
                              "psh": 0,
                              "ack": 0,
                              "urg": 0},
                 source_ip="127.0.0.1",
                 dest_ip="87.250.250.242",
                 source_port=1234,
                 dest_port=80,
                 window_size=5840,
                 seq=0,
                 ack_seq=0,
                 ttl=255,
                 id=54321,
                 use_ipv6=False
                 ):
        self.flags = flags
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.source_port = source_port
        self.dest_port = dest_port
        self.window_size = window_size
        self.seq = seq
        self.ack_seq = ack_seq
        self.check = 0
        self.urg_ptr = 0
        self.ttl = ttl
        # Id of this packet, random number
        self.id = id
        self.use_ipv6 = use_ipv6

    # checksum functions needed for calculation checksum
    @staticmethod
    def calculate_checksum(message) -> int:
        sum = 0
        # loop taking 2 characters at a time
        for i in range(0, len(message), 2):
            sum += (ord(message[i]) << 8) + (ord(message[i + 1]))

        sum = (sum >> 16) + (sum & 0xffff)
        # s = s + (s >> 16);
        # complement and mask to 4 byte short
        sum = ~sum & 0xffff

        return sum

    def get_tcp_package(self) -> bytes:
        package = 0
        if self.use_ipv6:
            pass
        else:
            package = self.get_ipv4_headers() + self.get_tcp_headers()
        return package

    def get_tcp_headers(self) -> bytes:
        doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
        offset_res = (doff << 4) + 0
        window = socket.htons(self.window_size)
        tcp_flags = self.flags["fin"] + \
                    (self.flags["syn"] << 1) + \
                    (self.flags["rst"] << 2) + \
                    (self.flags["psh"] << 3) + \
                    (self.flags["ack"] << 4) + \
                    (self.flags["urg"] << 5)

        # pre-build to calculate checksum
        tcp_headers = pack('!HHLLBBHHH', self.source_port, self.dest_port, self.seq, self.ack_seq, offset_res,
                           tcp_flags,
                           window, self.check, self.urg_ptr)

        # pseudo header fields
        source_address = socket.inet_aton(self.source_ip)
        dest_address = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_headers)

        pseudo_headers = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
        pseudo_headers += tcp_headers

        self.check = TCPPackage.calculate_checksum(pseudo_headers.decode("1251"))
        # get tcp headers with checksum
        tcp_headers = pack('!HHLLBBHHH', self.source_port, self.dest_port, self.seq, self.ack_seq, offset_res,
                           tcp_flags,
                           window, self.check, self.urg_ptr)
        return tcp_headers

    def get_ipv4_headers(self) -> bytes:
        ihl = 5
        version = 4
        tos = 0
        tot_len = 20 + 20
        frag_off = 0
        protocol = socket.IPPROTO_TCP
        check = 10
        source_addr = socket.inet_aton(self.source_ip)
        dest_addr = socket.inet_aton(self.dest_ip)
        ihl_version = (version << 4) + ihl

        ip_header = pack('!BBHHHBBH4s4s', ihl_version, tos, tot_len, self.id, frag_off, self.ttl, protocol, check,
                         source_addr,
                         dest_addr)
        return ip_header
