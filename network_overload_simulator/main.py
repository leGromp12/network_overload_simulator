from simulation import packet_generator, packet_processor
import simpy
from models import Stats

stats = Stats()

env = simpy.Environment()

queue = []

# starts the processess until 100 time units
env.process(packet_generator(env, queue, stats))
env.process(packet_processor(env, queue, stats))
env.run(until=100)



total_packets = stats.total_packets
lost_packets = stats.lost_packets
processed_packets = total_packets - lost_packets

loss_rate = (lost_packets / total_packets) if total_packets else 0.0


stats.update_queue(env, len(queue))

# displaying statistics 

print(f"Total packets: {total_packets}")
print(f"Processed packets: {processed_packets}")
print(f"Lost packets: {lost_packets}")

print(f"Loss rate: {loss_rate:.2%}")

print(f"Average delay: {stats.get_average_delay()}\nMaximum delay: {stats.get_max_delay()}\nMinimum delay: {stats.get_min_delay()}")


print("Average queue:", stats.get_average_queue(env.now))
