import argparse
from tcping import errors
from tcping import ping
from tcping import statistics
import logging
import asyncio
import time


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', default=None,
                        help='IP, Domain or URL')
    parser.add_argument('-c', '--count', default='-1', dest='pings_count',
                        help='count of pings, default - works, while would not interrupted by user')
    parser.add_argument('-t', '--timeout', default='0', dest='timeout',
                        help='to set timeout')
    parser.add_argument('-p', '--port', default='80', dest='port',
                        help='to set port')
    parser.add_argument('-d', '--delay', default='0.5', dest='delay',
                        help='delay between pings in seconds')
    parser.add_argument('-6', '--ipv6', action='store_true', dest="use_ipv6",
                        help='to use ipv6')
    parser.add_argument('-o', '--output-level', default='2', dest="output_level",
                        help='0 - only summary statistics; '
                             '1 - write only info for single pings; '
                             '2 - write all; ')
    return parser


async def main():
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                           timeout=args.timeout, use_ipv6=args.use_ipv6)
    pings_count = int(args.pings_count)
    delay = float(args.delay)
    output_level = int(args.output_level)
    try:
        i = 0
        while i != pings_count:
            measure = await tcp_ping.do_ping_with_connect()
            if output_level > 0:
                print(tcp_ping.prepare_ping_info(measure))
            if delay > measure > 0:
                time.sleep(delay - measure)
            i += 1
    except errors.PingError as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(e.message)
        exit(1)
    except KeyboardInterrupt:
        pass
    if output_level in (0, 2):
        if output_level == 2:
            print()
        stat = statistics.Statistics(tcp_ping.measures, tcp_ping.ip, tcp_ping.port)
        print(stat)


if __name__ == '__main__':
    asyncio.run(main())
