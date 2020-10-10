import unittest
import argparse
from tc_ping import __main__ as tcping

from tc_ping import ping as p
from tc_ping import errors as e
from tc_ping import statistics as st


class TestCorrectPings(unittest.TestCase):
    def test_ping_domain_standart(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        ping = p.Ping(destination=args.destination, port=args.port,
                      pings_count=args.pings_count, timeout=args.timeout,
                      delay=args.delay, payload_size_bytes=args.payload_size,
                      while_true=args.while_true, use_ipv6=args.use_ipv6)
        stat = ping.do_pings()
        self.assertEqual(stat.benchmarks_count, 4)

    def test_ping_domain_10_times(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com', '-c', '10'])
        ping = p.Ping(destination=args.destination, port=args.port,
                      pings_count=args.pings_count, timeout=args.timeout,
                      delay=args.delay, payload_size_bytes=args.payload_size,
                      while_true=args.while_true, use_ipv6=args.use_ipv6)
        stat = ping.do_pings()
        self.assertEqual(stat.benchmarks_count, 10)


class TestParsing(unittest.TestCase):
    def test_parsing_with_args(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com',
                                      '-t', '10',
                                      '-d', '2',
                                      '-p', '443',
                                      '-l', '65500',
                                      '-c', '3'])
        ping = p.Ping(destination=args.destination, port=args.port,
                      pings_count=args.pings_count, timeout=args.timeout,
                      delay=args.delay, payload_size_bytes=args.payload_size,
                      while_true=args.while_true, use_ipv6=args.use_ipv6)
        self.assertEqual(ping.use_ipv6, False)
        self.assertEqual(ping.while_true, False)
        self.assertEqual(len(ping.payload), 65500)
        self.assertEqual(ping.delay, 2)
        self.assertEqual(ping.timeout, 10)
        self.assertEqual(ping.pings_count, 3)
        self.assertEqual(ping.port, 443)

    def test_parsing_without_args(self):
        cmd_parser = tcping.create_cmd_parser()
        args = cmd_parser.parse_args(['google.com'])
        ping = p.Ping(destination=args.destination, port=args.port,
                      pings_count=args.pings_count, timeout=args.timeout,
                      delay=args.delay, payload_size_bytes=args.payload_size,
                      while_true=args.while_true, use_ipv6=args.use_ipv6)
        self.assertEqual(ping.use_ipv6, False)
        self.assertEqual(ping.while_true, False)
        self.assertEqual(len(ping.payload), 32)
        self.assertEqual(ping.delay, 0)
        self.assertEqual(ping.timeout, 0)
        self.assertEqual(ping.pings_count, 4)
        self.assertEqual(ping.port, 80)


class TestStatistics(unittest.TestCase):
    def test_statistics_all_successful(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
                    "Pings count: 4, Successful: 4, Failed: 0\n" \
                    "Fails percentage: 0.0\n" \
                    "Max time: 51.0ms, Min time: 49.0ms, Average time 49.75ms\n"

        benchmarks = []
        single_stat = p.StatisticsData(0.051, False)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, False)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, False)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.050, False)
        benchmarks.append(single_stat)
        statstics = st.Statistics(benchmarks, '127.0.0.1', '123')
        self.assertEqual(excpected, statstics.__str__())

    def test_statistics_some_failed(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
                    "Pings count: 4, Successful: 2, Failed: 2\n" \
                    "Fails percentage: 50.0\n" \
                    "Max time: 51.0ms, Min time: 49.0ms, Average time 50.0ms\n"

        benchmarks = []
        single_stat = p.StatisticsData(0.051, False)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, False)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, True)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.050, True)
        benchmarks.append(single_stat)
        statstics = st.Statistics(benchmarks, '127.0.0.1', '123')
        self.assertEqual(excpected, statstics.__str__())

    def test_statistics_all_failed(self):
        excpected = "Statistic tcping for [127.0.0.1:123]:\n" \
                    "Pings count: 4, Successful: 0, Failed: 4\n" \
                    "Fails percentage: 100.0\n" \
                    "Max time: 0ms, Min time: 0ms, Average time 0ms\n"

        benchmarks = []
        single_stat = p.StatisticsData(0.051, True)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, True)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.049, True)
        benchmarks.append(single_stat)
        single_stat = p.StatisticsData(0.050, True)
        benchmarks.append(single_stat)
        statstics = st.Statistics(benchmarks, '127.0.0.1', '123')
        self.assertEqual(excpected, statstics.__str__())


if __name__ == '__main__':
    unittest.main()
