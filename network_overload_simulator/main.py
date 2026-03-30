from simulation import packet_generator, packet_processor
import simpy

env = simpy.Environment()
queue = []
processing_delay_list = []
lost_pkt_list = []
env.process(packet_generator(env, queue, lost_pkt_list))
env.process(packet_processor(env, queue, processing_delay_list))
env.run(until=100)

print(f"Average delay: {sum(processing_delay_list) / len(processing_delay_list)}")
print(f"Lost packet count: {len(lost_pkt_list)}")
print(f"Lost packet list: {lost_pkt_list}")