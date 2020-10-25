from watchdog import watchdog_ping
import argparse
from tcping import errors
import logging
import time
import sys
import os


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destinations', default=None, nargs="*",
                        help='IP\'s, Domain\'s or URL\'s with ports')
    parser.add_argument('-t', '--timeout', default='0', dest='timeout',
                        help='to set timeout')
    parser.add_argument('-d', '--delay', default='0', dest='delay',
                        help='delay between pings in seconds')
    parser.add_argument('-6', '--ipv6', action='store_true', dest="use_ipv6",
                        help='to use ipv6')
    parser.add_argument('-o', '--output-level', default='2', dest="output_level",
                        help='0 - only summary statistics; '
                             '1 - write only info for single pings; '
                             '2 - write all; ')
    return parser


if __name__ == '__main__':
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    try:
        destinations = watchdog_ping.WatchdogPingData.parse_destanations(args.destinations)
        watchdog_ping_data = watchdog_ping.WatchdogPingData(destinations=destinations,
                                                            timeout=args.timeout, use_ipv6=args.use_ipv6)
        delay = int(args.delay)
        pings = watchdog_ping_data.get_pings()
        while True:
            measures = []
            for tcp_ping in pings:
                measure = tcp_ping.do_ping()
                measure_with_destination = measure, tcp_ping.destination
                measures.append(measure_with_destination)
            table = watchdog_ping.WatchdogPingData.get_measures_to_print(measures)
            if sys.platform.lower().startswith("win"):
                os.system("cls")
            else:
                if sys.platform.lower().startswith("darwin") or \
                        sys.platform.lower().startswith("linux"):
                    os.system("clear")
                else:
                    pass
            print(table.__str__())
            time.sleep(delay)
    except errors.PingError as e:
        logging.basicConfig(level=logging.INFO)
        logging.error(e.message)
        exit(1)
    except KeyboardInterrupt:
        pass
