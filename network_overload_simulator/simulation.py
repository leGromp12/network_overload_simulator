import random

import simpy

from models import Packet, Stats


def packet_generator(env, queue, stats, rate, max_queue, logger=None):
    packet_id = 1

    while True:
        yield env.timeout(random.expovariate(rate))

        packet = Packet(id=packet_id, arrival_time=env.now)
        stats.packet_generated()

        if len(queue) < max_queue:
            queue.append(packet)
            stats.update_queue(env, len(queue))
            if logger:
                logger(f"Packet {packet_id} queued at t={env.now:.2f}, q={len(queue)}")
        else:
            stats.packet_lost()
            if logger:
                logger(f"Packet {packet_id} dropped at t={env.now:.2f}, q={len(queue)}")

        packet_id += 1


def packet_processor(env, queue, stats, processing_time, logger=None):
    while True:
        if queue:
            packet = queue.pop(0)
            stats.update_queue(env, len(queue))

            yield env.timeout(processing_time)

            delay = env.now - packet.arrival_time
            stats.packet_processed(delay)
            if logger:
                logger(
                    f"Packet {packet.id} processed at t={env.now:.2f}, delay={delay:.2f}"
                )
        else:
            yield env.timeout(0.1)


def _run_once(arrival_rate, processing_time, max_queue, simulation_time, logger=None):
    env = simpy.Environment()
    queue = []
    stats = Stats()

    env.process(
        packet_generator(env, queue, stats, arrival_rate, max_queue, logger=logger)
    )
    env.process(packet_processor(env, queue, stats, processing_time, logger=logger))
    env.run(until=simulation_time)
    stats.finalize_queue(env.now)
    return stats.to_dict(simulation_time)


def run_single_simulation(config, logger=None):
    if logger:
        logger("Backend single simulation started")

    result = _run_once(
        arrival_rate=config["arrival_rate"],
        processing_time=config["processing_time"],
        max_queue=config["max_queue"],
        simulation_time=config["simulation_time"],
        logger=logger,
    )

    if logger:
        logger("Backend single simulation finished")

    return result


def run_series_simulation(config, logger=None):
    rates = config["rates_list"]
    runs_per_rate = config["runs_per_rate"]

    delays = []
    losses = []
    queues = []

    if logger:
        logger("Backend series simulation started")

    for rate in rates:
        if logger:
            logger(f"Running series point for arrival rate {rate}")

        rate_delays = []
        rate_losses = []
        rate_queues = []

        for run_index in range(runs_per_rate):
            if logger:
                logger(f"Rate {rate}: run {run_index + 1}/{runs_per_rate}")
            result = _run_once(
                arrival_rate=rate,
                processing_time=config["processing_time"],
                max_queue=config["max_queue"],
                simulation_time=config["simulation_time"],
            )
            rate_delays.append(result["average_delay"])
            rate_losses.append(result["loss_rate"])
            rate_queues.append(result["average_queue"])

        delays.append(sum(rate_delays) / len(rate_delays))
        losses.append(sum(rate_losses) / len(rate_losses))
        queues.append(sum(rate_queues) / len(rate_queues))

    if logger:
        logger("Backend series simulation finished")

    return {"rates": rates, "delays": delays, "losses": losses, "queues": queues}