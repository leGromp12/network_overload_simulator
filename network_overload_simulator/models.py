class Packet:
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time


class Stats:
    def __init__(self):
        self.total_packets = 0
        self.processed_packets = 0
        self.lost_packets = 0

        self.delays = []

        self.last_time = 0
        self.last_queue_len = 0
        self.area = 0

    def packet_generated(self):
        self.total_packets += 1

    def packet_processed(self, delay):
        self.processed_packets += 1
        self.delays.append(delay)

    def packet_lost(self):
        self.lost_packets += 1

    def update_queue(self, env, current_len):
        time_passed = env.now - self.last_time
        self.area += self.last_queue_len * time_passed

        self.last_time = env.now
        self.last_queue_len = current_len

    def get_average_delay(self):
        return sum(self.delays) / len(self.delays) if self.delays else 0

    def get_loss_rate(self):
        return self.lost_packets / self.total_packets if self.total_packets else 0

    def get_average_queue(self, total_time):
        return self.area / total_time