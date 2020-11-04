from tcping import errors
from tcping import ping
from prettytable import PrettyTable


class WatchdogPingData:
    """Contains methods  to get asyncio tasks, group of Ping objects and
     table with information about group of pings."""

    def __init__(self, destinations=[],
                 timeout=0,
                 use_ipv6=False):
        self.destinations = destinations
        self.timeout = timeout
        self.use_ipv6 = use_ipv6

    @staticmethod
    def parse_destinations(raw_destinations):
        """Method, parse from group of strings lke 'domain_or_port:[port]' and return tuple."""

        destinations_result = []
        for destination in raw_destinations:
            parts = destination.split(":")
            if len(parts) > 1:
                try:
                    destinations_result.append((parts[0], parts[1]))
                except Exception:
                    raise errors.InvalidPort
            else:
                destinations_result.append((parts[0], "80"))
        return destinations_result

    def get_pings(self):
        """Method, make ping objects from destinations and return list of pings."""

        pings = []
        for destination in self.destinations:
            wd_ping = ping.TCPing(destination=destination[0], port=destination[1],
                                  timeout=self.timeout, use_ipv6=self.use_ipv6)
            pings.append(wd_ping)
        return pings

    @staticmethod
    def create_tasks_from_pings(pings, ioloop):
        """Static method, takes list of ping objects and asyncio loop.
        Return list of asyncio tasks from ping.do_ping() method."""

        tasks = []
        for ping in pings:
            tasks.append(ioloop.create_task(ping.do_ping()))
        return tasks

    @staticmethod
    def get_max_and_min_time(measures_with_destinations):
        """Method, returns maximum and minimum time of group of measures + destinations tuples."""

        max = 0
        min = float("inf")
        for measure in measures_with_destinations:
            if max < measure[0]:
                max = measure[0]
            if min > measure[0]:
                min = measure[0]
        return max, min

    @staticmethod
    def get_measures_to_print(meaures):
        """Method, takes list of tuples (measure, destination) and
         return table with information about time, ip and port status for group of measures."""

        table = PrettyTable()
        table.field_names = ['destination', 'ip', 'port', 'time ms', 'condition']
        for measure_with_destination in meaures:
            destination = measure_with_destination[1]
            port = measure_with_destination[0].port
            time = round(measure_with_destination[0], 3)
            ip = measure_with_destination[0].ip
            if measure_with_destination[0].is_failed:
                condition = "Closed"
            else:
                condition = "Open"
            if time < 0:
                time = "-"
            table.add_row([destination, ip, port, time, condition])
        return table
