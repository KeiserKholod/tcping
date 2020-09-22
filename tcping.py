import argparse
from tc_ping import ping as p


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', default=None,
                        help='IP, Domain or URL')
    parser.add_argument('-c', '--count', default='4', dest='pings_count',
                        help='count of pings')
    parser.add_argument('-d', '--delay', default='0', dest='delay',
                        help='time of delay between pings')
    parser.add_argument('-t', '--timeout', default='0', dest='timeout',
                        help='to set timeout')
    parser.add_argument('-p', '--port', default='80', dest='port',
                        help='to set port')
    parser.add_argument('-l', '--payload', default='32', dest='payload_size',
                        help='to set size of the payload to send')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    ping = p.Ping(destination=args.destination, port=args.port,
                  pings_count=args.pings_count, timeout=args.timeout,
                  delay=args.delay, payload_size_bytes=args.payload_size)
    ping.do_pings()
