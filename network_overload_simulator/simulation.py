import random
from models import packet

def packet_generator(env, queue, lost_pkt_list):
    i = 0
    while True:
        interval_time = random.expovariate(1/3)

        yield env.timeout(interval_time)
        
        pkt = packet(id=i, arrival_time=env.now)

        if len(queue) <= 4:
            queue.append(pkt)
        else:
            print(f"Time {env.now}: Packet {pkt.id} lost")
            pkt.arrival_time = -1 # -1 means the packet is lost
            lost_pkt_list.append(pkt)

        
        i += 1

        queue_str = " ".join([f"[{p.id}]" for p in queue])
        print(f"Time {env.now}: {queue_str}")

def packet_processor(env, queue, processing_delay_list):
    processing_time = 5
    while True:
        if len(queue) > 0:
            delay = env.now - queue[0].arrival_time
            pkt = queue.pop(0)
            processing_delay_list.append(delay)

            yield env.timeout(processing_time)
            # print(f"{pkt.id} processed at {env.now}")
        else:
            yield env.timeout(1)
