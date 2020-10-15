import unittest

from tcping import ping
from tcping import statistics
from tcping import __main__ as tcping
from tcping import errors


class TestCorrectPings(unittest.TestCase):
    def test_ping_domain_standart(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        pings_count = int(args.pings_count)
        one_measure = tcp_ping.do_ping()
        self.assertEqual(len(tcp_ping.measures), 1)

    def test_ping_domain_incorrect(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.csom'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        pings_count = int(args.pings_count)
        with self.assertRaises(errors.InvalidIpOrDomain):
            one_measure = tcp_ping.do_ping()

    def test_ping_ip_standart(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['64.233.165.101', '-c', '10'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        pings_count = int(args.pings_count)
        one_measure = tcp_ping.do_ping()
        self.assertEqual(len(tcp_ping.measures), 1)

    def test_ping_ip_incorrect(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['64.233.165.101.123.214'])
        tcp_ping = ping.TCPing(destination=args.destination, port=args.port,
                               timeout=args.timeout, use_ipv6=args.use_ipv6)
        pings_count = int(args.pings_count)
        with self.assertRaises(errors.InvalidIpOrDomain):
            one_measure = tcp_ping.do_ping()


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
        expected = "Failed;"
        single_stat = ping.StatisticsData(-1, ip='127.0.0.1', port=123)
        ping_info = ping.TCPing.prepare_ping_info(single_stat)
        self.assertEqual(expected, ping_info)

    def test_statistics_all_successful(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
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
        self.assertEqual(excpected, statstics.__str__())

    def test_statistics_all_failed(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
                    "Pings count: 4, Successful: 0, Failed: 4\n" \
                    "Fails percentage: 100.0\n" \
                    "Max time: 0ms, Min time: 0ms, Average time 0ms\n"

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
        self.assertEqual(excpected, statstics.__str__())

    def test_statistics_some_failed(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
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
        self.assertEqual(excpected, statstics.__str__())

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


if __name__ == '__main__':
    unittest.main()
