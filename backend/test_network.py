from network.network_simulator import simulate_backbone_network


data_size = 10 * 1024 * 1024  # 10 MB


result = simulate_backbone_network(
    data_size_bytes=data_size,
    bandwidth_mbps=10,
    number_of_routers=3,
    latency_ms=10
)


print("=" * 60)
print("BACKBONE NETWORK SIMULATION")
print("=" * 60)

print(f"Data size: {result['data_size_bytes']} bytes")
print(f"Bandwidth: {result['bandwidth_mbps']} Mbps")
print(f"Routers: {result['number_of_routers']}")
print(
    f"Latency per router: "
    f"{result['latency_ms_per_router']} ms"
)

print(
    f"Transmission time: "
    f"{result['transmission_time_seconds']} seconds"
)

print(
    f"Total latency: "
    f"{result['total_latency_seconds']} seconds"
)

print(
    f"Total network time: "
    f"{result['total_network_time_seconds']} seconds"
)

print("=" * 60)