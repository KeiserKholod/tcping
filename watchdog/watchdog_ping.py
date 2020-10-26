from tcping import errors
from tcping import ping
from prettytable import PrettyTable


class WatchdogPingData:
    def __init__(self, destinations=[],
                 timeout=0,
                 use_ipv6=False):
        self.destinations = destinations
        self.timeout = timeout
        self.use_ipv6 = use_ipv6

    @staticmethod
    def parse_destanations(raw_destinations):
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
        pings = []
        for destination in self.destinations:
            wd_ping = ping.TCPing(destination=destination[0], port=destination[1],
                                  timeout=self.timeout, use_ipv6=self.use_ipv6)
            pings.append(wd_ping)
        return pings

    @staticmethod
    def get_measures_to_print(meaures):
        table = PrettyTable()
        table.field_names = ['destination', 'ip', 'port', 'time', 'condition']
        for measure_with_destination in meaures:
            destination = measure_with_destination[1]
            port = measure_with_destination[0].port
            time = measure_with_destination[0]
            ip = measure_with_destination[0].ip
            if measure_with_destination[0].is_failed:
                condition = "Closed"
            else:
                condition = "Open"
            if time < 0:
                time = "-"
            table.add_row([destination, ip, port, time, condition])
        return table
