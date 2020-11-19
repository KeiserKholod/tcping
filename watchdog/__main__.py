from watchdog import watchdog_ping
import argparse
from tcping import errors
import logging
import time
from asciimatics.screen import Screen


def create_cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('destinations', default=None, nargs="*",
                        help='IP\'s, Domain\'s or URL\'s with ports')
    parser.add_argument('-t', '--timeout', default='0', dest='timeout',
                        help='to set timeout')
    parser.add_argument('-d', '--delay', default='0.5', dest='delay',
                        help='delay between pings in seconds')
    parser.add_argument('-6', '--ipv6', action='store_true', dest="use_ipv6",
                        help='to use ipv6')
    parser.add_argument('-o', '--output-level',
                        default='2',
                        dest="output_level",
                        help='0 - only summary statistics; '
                             '1 - write only info for single pings; '
                             '2 - write all; ')
    return parser


def show_watchdog_tui(screen):
    cmd_parser = create_cmd_parser()
    args = cmd_parser.parse_args()
    if len(args.destinations) == 0:
        cmd_parser.print_help()
    else:
        last_info = ""
        try:
            destinations = watchdog_ping \
                .WatchdogPingData.parse_destinations(args.destinations)
            watchdog_ping_data = watchdog_ping \
                .WatchdogPingData(destinations=destinations,
                                  timeout=args.timeout,
                                  use_ipv6=args.use_ipv6)
            delay = float(args.delay)
            pings = watchdog_ping_data.get_pings()
            while True:
                measures = []
                for tcp_ping in pings:
                    measure = tcp_ping.do_ping()
                    measure_with_destination = measure, tcp_ping.destination
                    measures.append(measure_with_destination)
                table = watchdog_ping \
                    .WatchdogPingData \
                    .get_measures_to_print(measures)
                screen.clear()
                last_info = table.__str__()
                lines = table.__str__().split("\n")
                i = 0
                for line in lines:
                    i += 1
                    screen.print_at(line, 0, i)
                ev = screen.get_key()
                if ev in (ord('Q'), ord('q')):
                    return
                screen.refresh()
                max_time, min_time = watchdog_ping \
                    .WatchdogPingData \
                    .get_max_and_min_time(measures)
                if max_time < delay and min_time > 0:
                    time.sleep(delay - max_time)
        except errors.PingError as e:
            logging.basicConfig(level=logging.INFO)
            logging.error(e.message)
            exit(1)
        except KeyboardInterrupt:
            print(last_info)


if __name__ == '__main__':
    Screen.wrapper(show_watchdog_tui)
