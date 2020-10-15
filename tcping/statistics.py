from tcping import errors


class Statistics:
    def __init__(self, all_measures, ip, port):
        if len(all_measures) == 0:
            raise errors.StatisticsError
        self.__all_statistics_data = all_measures
        self.__ip = ip
        self.__port = port

    @property
    def benchmarks_count(self):
        return len(self.__all_statistics_data)

    @property
    def successful_benchmarks(self):
        successful_benchmarks = []
        for benchmark in self.__all_statistics_data:
            if not benchmark.is_failed:
                successful_benchmarks.append(benchmark)
        return successful_benchmarks

    @property
    def successful_pings_count(self):
        return len(self.successful_benchmarks)

    @property
    def failed_pings_count(self):
        return self.benchmarks_count - len(self.successful_benchmarks)

    @property
    def average_time(self):
        try:
            time = 0
            for benchmark in self.successful_benchmarks:
                time += benchmark
            return time / self.successful_pings_count * 1000
        except ZeroDivisionError:
            return 0

    @property
    def min_time(self):
        if len(self.successful_benchmarks) > 0:
            min_time = self.successful_benchmarks[0]
            for benchmark in self.successful_benchmarks:
                min_time = min(min_time, benchmark)
        else:
            min_time = 0
        return min_time * 1000

    @property
    def max_time(self):
        if len(self.successful_benchmarks) > 0:
            max_time = self.successful_benchmarks[0]
            for benchmark in self.successful_benchmarks:
                max_time = max(max_time, benchmark)
        else:
            max_time = 0
        return max_time * 1000

    @property
    def looses_percentage(self):
        return (self.failed_pings_count / self.benchmarks_count) * 100

    def __str__(self):
        return "Statistic tcping for [{}:{}]:\n" \
               "Pings count: {}, Successful: {}, Failed: {}\n" \
               "Fails percentage: {}\n" \
               "Max time: {}ms, Min time: {}ms, Average time {}ms\n".format(self.__ip, self.__port,
                                                                            self.benchmarks_count,
                                                                            self.successful_pings_count,
                                                                            self.failed_pings_count,
                                                                            self.looses_percentage, self.max_time,
                                                                            self.min_time, self.average_time)
