import unittest
from tcping import ping
from tcping import __main__ as tcping
from tcping import errors
from tcping import statistics
from watchdog import watchdog_ping


class TestCorrectPings(unittest.TestCase):
    def test_ping_domain_standart(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        tcp_ping.do_ping()
        self.assertEqual(len(tcp_ping.measures), 1)

    def test_ping_domain_incorrect(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.csom'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)

        with self.assertRaises(errors.InvalidIpOrDomain):
            tcp_ping.do_ping()

    def test_ping_ip_standart(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['64.233.165.101', '-c', '10'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        tcp_ping.do_ping()
        self.assertEqual(len(tcp_ping.measures), 1)

    def test_ping_ip_incorrect(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['64.233.165.101.123.214'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        with self.assertRaises(errors.InvalidIpOrDomain):
            tcp_ping.do_ping()


class TestParsing(unittest.TestCase):
    def test_parsing_with_args(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com',
                                      '-t', '10',
                                      '-p', '443',
                                      '-6'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        self.assertEqual(tcp_ping.use_ipv6, True)
        self.assertEqual(tcp_ping.timeout, 10)
        self.assertEqual(tcp_ping.port, 443)

    def test_parsing_without_args_from_cmd(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        self.assertEqual(tcp_ping.use_ipv6, False)
        self.assertEqual(tcp_ping.timeout, 0)
        self.assertEqual(tcp_ping.port, 80)

    def test_parsing_without_args_at_all(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        tcp_ping = ping.TCPing(destination=args.destination)
        self.assertEqual(tcp_ping.use_ipv6, False)
        self.assertEqual(tcp_ping.timeout, 0)
        self.assertEqual(tcp_ping.port, 80)


class TestStatistics(unittest.TestCase):
    def test_prepare_ping_info(self):
        expected = "From: [127.0.0.1:123]; Time: 51.0ms;"
        single_stat = ping.StatisticsData(0.051, ip='127.0.0.1', port=123)
        ping_info = ping.TCPing.prepare_ping_info(single_stat)
        self.assertEqual(expected, ping_info)

    def test_prepare_ping_info_if_failed(self):
        expected = "From: [127.0.0.1:123]; Failed;"
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        ping_info = ping.TCPing.prepare_ping_info(single_stat)
        self.assertEqual(expected, ping_info)

    def test_statistics_all_successful(self):
        expected = "Statistic tcping for [127.0.0.1:123]:\n" \
                   "Pings count: 4, Successful: 4, Failed: 0\n" \
                   "Fails percentage: 0.0\n" \
                   "Max time: 51.0ms, Min time: 49.0ms, Average time 49.75ms\n"

        measures = []
        single_stat = ping.StatisticsData(0.051, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(0.049, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(0.049, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(0.050, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        statstics = statistics.Statistics(measures, '127.0.0.1', '123')
        self.assertEqual(expected, statstics.__str__())

    def test_statistics_all_failed(self):
        expected = "Statistic tcping for [127.0.0.1:123]:\n" \
                   "Pings count: 4, Successful: 0, Failed: 4\n" \
                   "Fails percentage: 100.0\n" \
                   "Max time: 0.0ms, Min time: 0.0ms, Average time 0.0ms\n"

        measures = []
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        statstics = statistics.Statistics(measures, '127.0.0.1', '123')
        self.assertEqual(expected, statstics.__str__())

    def test_statistics_some_failed(self):
        expected = "Statistic tcping for [127.0.0.1:123]:\n" \
                   "Pings count: 4, Successful: 2, Failed: 2\n" \
                   "Fails percentage: 50.0\n" \
                   "Max time: 50.0ms, Min time: 50.0ms, Average time 50.0ms\n"

        measures = []
        single_stat = ping.StatisticsData(0.050, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(0.050, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        measures.append(single_stat)
        statstics = statistics.Statistics(measures, '127.0.0.1', '123')
        self.assertEqual(expected, statstics.__str__())

    def test_statistics_data_is_float(self):
        single_stat = ping.StatisticsData(0.051, ip='127.0.0.1', port=123)
        self.assertEqual(single_stat, 0.051)

    def test_statistics_data_have_meta(self):
        single_stat = ping.StatisticsData(0.051, ip='127.0.0.1', port=123)
        self.assertEqual(single_stat, 0.051)
        self.assertEqual(single_stat.ip, '127.0.0.1')
        self.assertEqual(single_stat.port, 123)
        self.assertEqual(single_stat.is_failed, False)

    def test_statistics_data_if_failed(self):
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        self.assertEqual(single_stat.is_failed, True)


class TestWatchdog(unittest.TestCase):
    def test_parse_destinations(self):
        raw_destinations = ['google.com',
                            'google.com:443',
                            '127.0.0.1',
                            '127.0.0.1:123']
        expected_destinations = [('google.com', "80"),
                                 ('google.com', "443"),
                                 ('127.0.0.1', "80"),
                                 ('127.0.0.1', "123")]
        parsed_destinations = watchdog_ping \
            .WatchdogPingData.parse_destinations(raw_destinations)
        self.assertEqual(expected_destinations, parsed_destinations)

    def test_init(self):
        raw_destinations = ['google.com',
                            'google.com:443',
                            '127.0.0.1',
                            '127.0.0.1:123']
        parsed_destinations = watchdog_ping \
            .WatchdogPingData \
            .parse_destinations(raw_destinations)
        watchdog_ping_object = watchdog_ping \
            .WatchdogPingData(destinations=parsed_destinations,
                              timeout=1,
                              use_ipv6=True)
        self.assertEqual(watchdog_ping_object.destinations,
                         parsed_destinations)
        self.assertEqual(watchdog_ping_object.timeout, 1)
        self.assertEqual(watchdog_ping_object.use_ipv6, True)

    def test_init_default(self):
        watchdog_ping_object = watchdog_ping.WatchdogPingData()
        self.assertEqual(watchdog_ping_object.destinations, [])
        self.assertEqual(watchdog_ping_object.timeout, 0)
        self.assertEqual(watchdog_ping_object.use_ipv6, False)

    def test_get_pings(self):
        raw_destinations = ['google.com', 'google.com:443']
        pings_expected = [ping.TCPing(destination='google.com',
                                      port=80,
                                      use_ipv6=False,
                                      timeout=1),
                          ping.TCPing(destination='google.com',
                                      port=443,
                                      use_ipv6=False,
                                      timeout=1)]
        parsed_destinations = watchdog_ping \
            .WatchdogPingData \
            .parse_destinations(raw_destinations)
        watchdog_ping_object = watchdog_ping \
            .WatchdogPingData(destinations=parsed_destinations,
                              timeout=1,
                              use_ipv6=False)
        pings = watchdog_ping_object.get_pings()
        self.assertEqual(len(pings_expected), len(pings))
        self.assertEqual(type(pings[0]), ping.TCPing)
        self.assertEqual(type(pings[1]), ping.TCPing)

    def test_get_measures_to_print(self):
        measures_to_print_expected = """+-------------+-------------+------+---------+-----------+
| destination |      ip     | port | time ms | condition |
+-------------+-------------+------+---------+-----------+
|  hemlo.com  |  127.0.0.1  | 123  |   0.05  |    Open   |
|  google.com | 192.168.0.2 | 443  |   0.05  |    Open   |
|   meow.org  | 192.167.2.1 | 123  |    -    |   Closed  |
+-------------+-------------+------+---------+-----------+"""
        measures_with_dest = []
        single_stat = ping.StatisticsData(0.050,
                                          ip='127.0.0.1',
                                          port=123), "hemlo.com"
        measures_with_dest.append(single_stat)
        single_stat = ping.StatisticsData(0.050,
                                          ip='192.168.0.2',
                                          port=443), "google.com"
        measures_with_dest.append(single_stat)
        single_stat = ping.StatisticsData(-1,
                                          ip='192.167.2.1',
                                          port=123), "meow.org"
        measures_with_dest.append(single_stat)

        measures_to_print = watchdog_ping \
            .WatchdogPingData \
            .get_measures_to_print(measures_with_dest)
        self.assertEqual(measures_to_print_expected,
                         measures_to_print.__str__())

    def test_min_max(self):
        measures_with_dest = []
        single_stat = ping.StatisticsData(0.050,
                                          ip='127.0.0.1',
                                          port=123), "hemlo.com"
        measures_with_dest.append(single_stat)
        single_stat = ping.StatisticsData(0.059,
                                          ip='192.168.0.2',
                                          port=443), "google.com"
        measures_with_dest.append(single_stat)
        single_stat = ping.StatisticsData(-1,
                                          ip='192.167.2.1',
                                          port=123), "meow.org"
        measures_with_dest.append(single_stat)
        max, min = watchdog_ping.WatchdogPingData \
            .get_max_and_min_time(measures_with_dest)
        self.assertEqual(max, 0.059)
        self.assertEqual(min, -1)


if __name__ == '__main__':
    unittest.main()
