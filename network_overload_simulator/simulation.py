import random

from models import Packet

def packet_generator(env, queue, stats):
    max_queue = 5
    i = 0
    while True:
        interval_time = random.expovariate(1/3)

        yield env.timeout(interval_time)
        
        pkt = Packet(id=i, arrival_time=env.now)
        packet_generated()

        if len(queue) < max_queue:
            queue.append(pkt)
        else:
            print(f"Time {env.now}: Packet {pkt.id} lost")
            packet_lost()

        i += 1

        queue_str = " ".join([f"[{p.id}]" for p in queue])
        print(f"Time {env.now}: {queue_str}")

def packet_processor(env, queue, stats):
    processing_time = 5
    while True:
        if len(queue) > 0:
            pkt = queue.pop(0)

            yield env.timeout(processing_time)

            delay = env.now - pkt.arrival_time
            packet_processed(delay)
        else:
            yield env.timeout(0.1)
