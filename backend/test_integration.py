from compression.compression_engine import (
    compress_data,
    decompress_data,
    get_compression_stats,
    calculate_hash
)

from network.network_simulator import (
    simulate_backbone_network
)


# --------------------------------------------------
# Sample data
# --------------------------------------------------

data = (
    b"Backbone network data compression test. "
    b"This data represents information travelling "
    b"through a backbone network. "
    * 10000
)


# --------------------------------------------------
# Network configuration
# --------------------------------------------------

BANDWIDTH_MBPS = 10
ROUTERS = 3
LATENCY_MS = 10


print("=" * 70)
print("DATA COMPRESSION FOR BACKBONE NETWORK")
print("=" * 70)

print(f"Original data size: {len(data)} bytes")
print()


# --------------------------------------------------
# Scenario 1: WITHOUT COMPRESSION
# --------------------------------------------------

print("SCENARIO 1: WITHOUT COMPRESSION")
print("-" * 70)

uncompressed_result = simulate_backbone_network(
    data_size_bytes=len(data),
    bandwidth_mbps=BANDWIDTH_MBPS,
    number_of_routers=ROUTERS,
    latency_ms=LATENCY_MS
)

print(
    f"Data transmitted: "
    f"{uncompressed_result['data_size_bytes']} bytes"
)

print(
    f"Network transmission time: "
    f"{uncompressed_result['total_network_time_seconds']} seconds"
)

print()


# --------------------------------------------------
# Scenario 2: WITH COMPRESSION
# --------------------------------------------------

algorithm = "zstd"

print(f"SCENARIO 2: WITH {algorithm.upper()} COMPRESSION")
print("-" * 70)

original_hash = calculate_hash(data)

compressed_data, compression_time = compress_data(
    data,
    algorithm
)

stats = get_compression_stats(
    data,
    compressed_data
)

compressed_result = simulate_backbone_network(
    data_size_bytes=len(compressed_data),
    bandwidth_mbps=BANDWIDTH_MBPS,
    number_of_routers=ROUTERS,
    latency_ms=LATENCY_MS
)

decompressed_data, decompression_time = decompress_data(
    compressed_data,
    algorithm
)

decompressed_hash = calculate_hash(
    decompressed_data
)

integrity = original_hash == decompressed_hash


print(
    f"Compressed data size: "
    f"{stats['compressed_size']} bytes"
)

print(
    f"Bandwidth saved: "
    f"{stats['space_saved_percent']}%"
)

print(
    f"Compression time: "
    f"{compression_time:.6f} seconds"
)

print(
    f"Network transmission time: "
    f"{compressed_result['total_network_time_seconds']} seconds"
)

print(
    f"Decompression time: "
    f"{decompression_time:.6f} seconds"
)

print(
    f"Integrity check: "
    f"{'PASSED' if integrity else 'FAILED'}"
)

print()


# --------------------------------------------------
# Comparison
# --------------------------------------------------

time_without = (
    uncompressed_result[
        "total_network_time_seconds"
    ]
)

time_with = (
    compressed_result[
        "total_network_time_seconds"
    ]
)

time_saved = time_without - time_with

print("=" * 70)
print("COMPARISON")
print("=" * 70)

print(
    f"Network time without compression: "
    f"{time_without} seconds"
)

print(
    f"Network time with compression: "
    f"{time_with} seconds"
)

print(
    f"Network transmission time saved: "
    f"{time_saved:.6f} seconds"
)

print("=" * 70)