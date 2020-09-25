class StatisticsData:
    def __init__(self, time, is_failed, ip_and_port):
        self.time = time
        self.is_failed = is_failed
        self.ip = ip_and_port[0]
        self.port = int(ip_and_port[1])
