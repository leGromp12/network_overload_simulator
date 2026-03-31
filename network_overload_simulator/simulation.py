import random

from models import Packet

def packet_generator(env, queue, stats):
    max_queue = 5
    i = 1
    while True:
        interval_time = random.expovariate(1/3)

        yield env.timeout(interval_time)
        
        # adds and tracks packets
        pkt = Packet(id=i, arrival_time=env.now)
        stats.packet_generated()

        if len(queue) < max_queue:
            queue.append(pkt)
            stats.update_queue(env, len(queue))

        else:
            stats.packet_lost()
            #print(f"Time {env.now}: Packet {pkt.id} lost")

        i += 1
        # queue_str = " ".join([f"[{p.id}]" for p in queue])
        # print(f"Time {env.now}: {queue_str}")

def packet_processor(env, queue, stats):
    processing_time = 5
    while True:
        if len(queue) > 0:
            pkt = queue.pop(0)
            stats.update_queue(env, len(queue)) 
            # processess packet and then waits some time
            yield env.timeout(processing_time)

            delay = env.now - pkt.arrival_time #collects delays for all of the processed packets for statistics
            stats.packet_processed(delay)
        else:
            yield env.timeout(0.1)
