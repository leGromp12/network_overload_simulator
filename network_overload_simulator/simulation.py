import random
from models import packet

def packet_generator(env, queue):
    i = 0
    while True:
        interval_time = random.expovariate(1/3)
        yield env.timeout(interval_time)
        pkt = packet(id=i, arrival_time=env.now)
        queue.append(pkt)
        i += 1
        queue_str = " ".join([f"[{p.id}]" for p in queue])
        print(f"Time {env.now}: {queue_str}")

def packet_processor(env, queue):
    processing_time = 5
    while True:
        if len(queue) > 0:
            pkt = queue.pop(0)
            yield env.timeout(processing_time)
            # print(f"{pkt.id} processed at {env.now}")
        else:
            yield env.timeout(1)
