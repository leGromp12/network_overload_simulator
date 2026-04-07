import random
from models import Packet


def packet_generator(env, queue, stats, rate):
    max_queue = 5
    i = 1

    while True:
        yield env.timeout(random.expovariate(rate))

        pkt = Packet(id=i, arrival_time=env.now)
        stats.packet_generated()

        if len(queue) < max_queue:
            queue.append(pkt)
            stats.update_queue(env, len(queue))
        else:
            stats.packet_lost()

        i += 1


def packet_processor(env, queue, stats):
    processing_time = 5

    while True:
        if queue:
            pkt = queue.pop(0)
            stats.update_queue(env, len(queue))

            yield env.timeout(processing_time)

            delay = env.now - pkt.arrival_time
            stats.packet_processed(delay)
        else:
            yield env.timeout(0.1)