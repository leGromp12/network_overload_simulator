from simulation import packet_generator, packet_processor
import simpy

env = simpy.Environment()
queue = []
env.process(packet_generator(env, queue))
env.process(packet_processor(env, queue))
env.run(until=100)

# for p in queue:
#     print(f"id={p.id}, arrival_time={p.arrival_time}")