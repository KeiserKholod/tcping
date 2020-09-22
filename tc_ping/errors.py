class PingError(Exception):
    message = 'Error'


class InvalidIpOrDomain(PingError):
    message = 'Invalid IP- address or Domain'
