from simulation import packet_generator, packet_processor
from models import Stats
from matplotlib.ticker import PercentFormatter
import simpy
import matplotlib.pyplot as plt


SIM_TIME = 100
RUNS_PER_RATE = 3


def run_simulation(rate):
    env = simpy.Environment()
    queue = []
    stats = Stats()

    env.process(packet_generator(env, queue, stats, rate))
    env.process(packet_processor(env, queue, stats))

    env.run(until=SIM_TIME)

    stats.update_queue(env, len(queue))

    return (
        stats.get_average_delay(),
        stats.get_loss_rate(),
        stats.get_average_queue(env.now)
    )


rates = [0.25, 0.5, 0.75, 1, 2]

delays = []
losses = []
queues = []

for rate in rates:
    runs = [run_simulation(rate) for _ in range(RUNS_PER_RATE)]

    avg_delay = sum(r[0] for r in runs) / RUNS_PER_RATE
    loss = sum(r[1] for r in runs) / RUNS_PER_RATE
    avg_queue = sum(r[2] for r in runs) / RUNS_PER_RATE

    print(f"Rate: {rate}, Delay: {avg_delay:.2f}, Loss: {loss:.2%}, Queue: {avg_queue:.2f}")

    delays.append(avg_delay)
    losses.append(loss)
    queues.append(avg_queue)


plt.style.use('seaborn-v0_8-pastel')
fig, axs = plt.subplots(1, 3, figsize=(15, 4))

axs[0].plot(rates, delays, linewidth=2, marker="o", markersize=8, label="Delay")
axs[0].set_title("Average delay")
axs[0].set_xlabel("Rate")
axs[0].set_ylabel("Average delay")
axs[0].grid(True, linestyle='--', alpha=0.6)
axs[0].legend()

axs[1].plot(rates, losses, linewidth=2, marker="o", markersize=8, label="Loss")
axs[1].set_title("Loss rate")
axs[1].set_xlabel("Rate")
axs[1].set_ylabel("Loss rate")
axs[1].yaxis.set_major_formatter(PercentFormatter(1.0))
axs[1].grid(True, linestyle='--', alpha=0.6)
axs[1].legend()

axs[2].plot(rates, queues, linewidth=2, marker="o", markersize=8, label="Queue")
axs[2].set_title("Average queue")
axs[2].set_xlabel("Rate")
axs[2].set_ylabel("Average queue")
axs[2].grid(True, linestyle='--', alpha=0.6)
axs[2].legend()

plt.tight_layout()
plt.show()