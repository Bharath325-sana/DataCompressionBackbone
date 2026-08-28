from compression.compression_engine import (
    compress_data,
    decompress_data,
    get_compression_stats,
    calculate_hash
)


# Sample data for testing
data = (
    b"Backbone network data compression test. "
    b"This is sample data that will be repeated many times. "
    * 1000
)

algorithms = ["gzip", "brotli", "zstd"]

print("=" * 60)
print("BACKBONE NETWORK DATA COMPRESSION TEST")
print("=" * 60)

print(f"Original data size: {len(data)} bytes")
print()

original_hash = calculate_hash(data)

for algorithm in algorithms:

    compressed, compression_time = compress_data(data, algorithm)

    decompressed, decompression_time = decompress_data(
        compressed,
        algorithm
    )

    stats = get_compression_stats(data, compressed)

    decompressed_hash = calculate_hash(decompressed)

    integrity = original_hash == decompressed_hash

    print(f"Algorithm: {algorithm.upper()}")
    print(f"Compressed size: {stats['compressed_size']} bytes")
    print(f"Compression ratio: {stats['compression_ratio']}")
    print(f"Space/Bandwidth saved: {stats['space_saved_percent']}%")
    print(f"Compression time: {compression_time:.6f} seconds")
    print(f"Decompression time: {decompression_time:.6f} seconds")
    print(f"Integrity check: {'PASSED' if integrity else 'FAILED'}")
    print("-" * 60)