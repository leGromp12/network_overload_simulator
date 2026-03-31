class Packet():
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time

    def __repr__(self):
        return f"packet(id={self.id}, arrival_time={self.arrival_time})"
        
class Stats():
    def __init__(self):
        self.total_packets = 0
        self.processed_packets = 0
        self.lost_packets = 0

        self.delays = []



    def packet_generated(self):
        self.total_packets += 1

    def packet_processed(self, delay):
        self.processed_packets += 1
        self.delays.append(delay)

    def packet_lost(self):
        self.lost_packets += 1
