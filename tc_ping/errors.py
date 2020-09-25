class PingError(Exception):
    message = 'Error'


class InvalidIpOrDomain(PingError):
    message = 'Invalid IP-address or Domain'


class ConnectionError(PingError):
    message = 'failed to establish connection'


class StatisticsError(PingError):
    message = 'count of the benchmarks must be greater than zero'
