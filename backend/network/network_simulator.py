import time


def calculate_transmission_time(data_size_bytes, bandwidth_mbps):
    """
    Calculate the time required to transmit data
    over a network link.
    """

    data_size_bits = data_size_bytes * 8
    bandwidth_bits_per_second = bandwidth_mbps * 1_000_000

    transmission_time = (
        data_size_bits / bandwidth_bits_per_second
    )

    return transmission_time


def simulate_backbone_network(
    data_size_bytes,
    bandwidth_mbps=10,
    number_of_routers=3,
    latency_ms=10
):
    """
    Simulate transmission of data through a backbone network.
    """

    transmission_time = calculate_transmission_time(
        data_size_bytes,
        bandwidth_mbps
    )

    total_latency = (
        number_of_routers * latency_ms
    ) / 1000

    total_network_time = (
        transmission_time + total_latency
    )

    return {
        "data_size_bytes": data_size_bytes,
        "bandwidth_mbps": bandwidth_mbps,
        "number_of_routers": number_of_routers,
        "latency_ms_per_router": latency_ms,
        "transmission_time_seconds": round(
            transmission_time, 6
        ),
        "total_latency_seconds": round(
            total_latency, 6
        ),
        "total_network_time_seconds": round(
            total_network_time, 6
        )
    }