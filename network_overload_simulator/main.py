from simulation import packet_generator, packet_processor
import simpy

from models import Stats

stats = Stats()

env = simpy.Environment()

queue = []
processing_delay_list = []
# stats = {"total_packets": 0, "lost_packets": 0, }

env.process(packet_generator(env, queue, stats))
env.process(packet_processor(env, queue, processing_delay_list))
env.run(until=100)


# 1. Скільки всього пройшло пакетів
# 2. Скільки оброблено пакетів 
# 3. Скільки втрачено пакетів
# Для кожного пакету зберігається час створення та час завершення, також вираховується довжина черги в різний час процесу роботи симуляції. 
# За допомогою цих даних рахується:
# 1. Відсоток втрат пакетів
# 2. Середня затримка
# 3. Максимальна затримка
# 4. Середня довжина черги


total_packets = stats["total_packets"]
lost_packets = stats["lost_packets"]
processed_packets = total_packets - lost_packets


loss_rate = (lost_packets / total_packets) if total_packets else 0.0
average_delay = (sum(processing_delay_list) / len(processing_delay_list)) if processing_delay_list else 0
min_delay = min(processing_delay_list) if processing_delay_list else 0
max_delay = max(processing_delay_list) if processing_delay_list else 0

print(f"Total packets: {total_packets}")
print(f"Processed packets: {processed_packets}")
print(f"Lost packets: {lost_packets}")

print(f"Loss rate: {loss_rate:.2%}")

if processing_delay_list:
    print(f"Average delay: {average_delay}\nMaximum delay: {max_delay}\nMinimum delay: {min_delay}")
else:
    print("No packets where processed")
