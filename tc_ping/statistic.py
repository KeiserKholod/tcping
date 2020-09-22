class Statistic:
    def __init__(self, all_benchmarks):
        self.__all_benchmarks = all_benchmarks
        self.__ip = all_benchmarks[0][2][0]
        self.__port = all_benchmarks[0][2][1]

    @property
    def benchmarks_count(self):
        return len(self.__all_benchmarks)

    @property
    def successful_benchmarks(self):
        successful_benchmarks = []
        for benchmark in self.__all_benchmarks:
            if not benchmark[1]:
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
        time = 0
        for benchmark in self.successful_benchmarks:
            time += benchmark[0]
        return time / self.successful_pings_count * 1000

    @property
    def min_time(self):
        min_time = self.successful_benchmarks[0][0]
        for benchmark in self.successful_benchmarks:
            min_time = min(min_time, benchmark[0])
        return min_time * 1000

    @property
    def max_time(self):
        max_time = self.successful_benchmarks[0][0]
        for benchmark in self.successful_benchmarks:
            max_time = max(max_time, benchmark[0])
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
