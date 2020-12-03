from watchdog import watchdog_ping
import argparse
from tcping import errors
from tcping import ping
import logging
import time
from asciimatics.screen import Screen
from concurrent.futures import ProcessPoolExecutor


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
                measures_to_print = []
                futures = []
                with ProcessPoolExecutor(max_workers=2) as executor:
                    for tcp_ping in pings:
                        future = executor.submit(ping.TCPing.do_ping, tcp_ping)
                        futures.append(future)
                measures = [future.result() for future in futures]
                for measure in measures:
                    measure_with_destination = measure, tcp_ping.destination
                    measures_to_print.append(measure_with_destination)
                table = watchdog_ping \
                    .WatchdogPingData \
                    .get_measures_to_print(measures_to_print)
                screen.clear()
                last_info = str(table)
                lines = str(table).split("\n")
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
                    .get_max_and_min_time(measures_to_print)
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
