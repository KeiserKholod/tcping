import struct
import socket
import enum


class TCPPackageType(enum.IntFlag):
    URG = 1
    ACK = 2
    PSH = 4
    RST = 8
    SYN = 16
    FIN = 32


class TCPPackage:
    def __init__(self, flags: TCPPackageType = TCPPackageType.SYN,
                 source_ip: str = "127.0.0.1",
                 dest_ip: str = "87.250.250.242",
                 source_port: int = 0,
                 dest_port: int = 80,
                 window_size: int = 5840,
                 seq: int = 0,
                 ack_seq: int = 0,
                 ttl: int = 255,
                 pack_id: int = 54321,
                 use_ipv6: bool = False,
                 data: bytes = b''
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
        self.id = pack_id
        self.use_ipv6 = use_ipv6
        self.data = data

    # checksum functions needed for calculation checksum
    @staticmethod
    def calculate_checksum(message: str) -> int:
        sum = 0
        # loop taking 2 characters at a time
        for i in range(0, len(message), 2):
            sum += (ord(message[i]) << 8) + (ord(message[i + 1]))

        sum = (sum >> 16) + (sum & 0xffff)
        # s = s + (s >> 16);
        # complement and mask to 4 byte short
        sum = ~sum & 0xffff

        return sum

    def __bytes__(self) -> bytes:
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
        tcp_flags = self.flags
        # pre-build to calculate checksum
        tcp_headers = struct.pack('!HHLLBBHHH',
                                  self.source_port,
                                  self.dest_port,
                                  self.seq,
                                  self.ack_seq,
                                  offset_res,
                                  tcp_flags,
                                  window,
                                  self.check,
                                  self.urg_ptr)

        # pseudo header fields
        source_address = socket.inet_aton(self.source_ip)
        dest_address = socket.inet_aton(self.dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_headers)

        pseudo_headers = struct.pack('!4s4sBBH',
                                     source_address,
                                     dest_address,
                                     placeholder,
                                     protocol,
                                     tcp_length)
        pseudo_headers += tcp_headers

        self.check = TCPPackage \
            .calculate_checksum(pseudo_headers.decode("1251"))
        # get tcp headers with checksum
        tcp_headers = struct.pack('!HHLLBBHHH',
                                  self.source_port,
                                  self.dest_port,
                                  self.seq,
                                  self.ack_seq,
                                  offset_res,
                                  tcp_flags,
                                  window, self.check,
                                  self.urg_ptr)
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
        ip_header = struct.pack('!BBHHHBBH4s4s',
                                ihl_version,
                                tos,
                                tot_len,
                                self.id,
                                frag_off,
                                self.ttl,
                                protocol,
                                check,
                                source_addr,
                                dest_addr)
        return ip_header

    @staticmethod
    # не получается сделать тайпинг на обьект текущего класса
    def parse_tcp_ipv4_package(raw_data):
        package = TCPPackage()
        TCPPackage.parse_ipv4_headers(package, raw_data[:40])
        TCPPackage.parse_tcp_headers(package, raw_data[:40])
        return package

    @staticmethod
    def parse_ipv4_headers(tcp_pack, raw_data: bytes):
        headers = struct.unpack('!BBHHHBBH4s4sHHLLBBHHH', raw_data)
        # ipv4
        # ihl_version = headers[0]
        # tos = headers[1]
        # tot_len = headers[2]
        tcp_pack.id = headers[3]
        # frag_off = headers[4]
        tcp_pack.ttl = headers[5]
        # protocol = headers[6]
        # check = headers[7]
        source_addr = headers[8]
        tcp_pack.source_ip = socket.inet_ntoa(source_addr)
        dest_addr = headers[9]
        tcp_pack.dest_ip = socket.inet_ntoa(dest_addr)

    @staticmethod
    def parse_tcp_headers(tcp_pack, raw_data: bytes):
        headers = struct.unpack('!BBHHHBBH4s4sHHLLBBHHH', raw_data)
        # tcp
        tcp_pack.source_port = headers[10]
        tcp_pack.dest_port = headers[11]
        tcp_pack.seq = headers[12]
        tcp_pack.ack_seq = headers[13]
        tcp_pack.offset_res = headers[14]
        tcp_pack.flags = headers[15]
        tcp_pack.window = socket.ntohs(headers[16])
        tcp_pack.check = headers[17]
        tcp_pack.urg_ptr = headers[18]
