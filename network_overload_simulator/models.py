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

        # queue history for single simulation visualization
        self.queue_history = [(0, 0)]

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

        self.queue_history.append((env.now, current_len))

    def finalize_queue(self, current_time):
        time_passed = current_time - self.last_time
        self.area += self.last_queue_len * time_passed
        self.last_time = current_time

        if self.queue_history[-1] != (current_time, self.last_queue_len):
            self.queue_history.append((current_time, self.last_queue_len))

    def get_average_delay(self):
        return sum(self.delays) / len(self.delays) if self.delays else 0

    def get_loss_rate(self):
        return self.lost_packets / self.total_packets if self.total_packets else 0

    def get_average_queue(self, total_time):
        return self.area / total_time if total_time else 0

    def to_dict(self, total_time):
        return {
            "average_delay": self.get_average_delay(),
            "loss_rate": self.get_loss_rate(),
            "average_queue": self.get_average_queue(total_time),
            "total_packets": self.total_packets,
            "processed_packets": self.processed_packets,
            "lost_packets": self.lost_packets,
            "delays": self.delays.copy(),
            "queue_times": [point[0] for point in self.queue_history],
            "queue_lengths": [point[1] for point in self.queue_history],
        }