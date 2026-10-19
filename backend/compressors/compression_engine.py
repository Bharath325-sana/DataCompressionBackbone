import gzip
import time
import hashlib

try:
    import zstandard as zstd
except ImportError:
    zstd = None

try:
    import brotli
except ImportError:
    brotli = None

try:
    import lz4.frame
except ImportError:
    lz4 = None

def calculate_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def get_compression_stats(original_data: bytes, compressed_data: bytes) -> dict:
    orig_size = len(original_data)
    comp_size = len(compressed_data)
    ratio = round(orig_size / comp_size, 4) if comp_size > 0 else 0.0
    space_saved = round(((orig_size - comp_size) / orig_size) * 100, 2) if orig_size > 0 else 0.0
    return {
        "original_size": orig_size,
        "compressed_size": comp_size,
        "compression_ratio": ratio,
        "space_saved_percent": space_saved
    }

def compress_data(data: bytes, algorithm: str = "zstd") -> tuple[bytes, float]:
    algo = algorithm.lower().strip()
    start = time.perf_counter()

    if algo == "gzip":
        compressed = gzip.compress(data)
    elif algo in ("zstd", "zstandard"):
        if zstd is None:
            raise RuntimeError("zstandard is not installed. Run 'pip install zstandard'.")
        cctx = zstd.ZstdCompressor(level=3)
        compressed = cctx.compress(data)
    elif algo == "brotli":
        if brotli is None:
            raise RuntimeError("brotli is not installed. Run 'pip install brotli'.")
        compressed = brotli.compress(data)
    elif algo == "lz4":
        if lz4 is None:
            raise RuntimeError("lz4 is not installed. Run 'pip install lz4'.")
        compressed = lz4.frame.compress(data)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    elapsed = time.perf_counter() - start
    return compressed, elapsed

def decompress_data(compressed_data: bytes, algorithm: str = "zstd") -> tuple[bytes, float]:
    algo = algorithm.lower().strip()
    start = time.perf_counter()

    if algo == "gzip":
        decompressed = gzip.decompress(compressed_data)
    elif algo in ("zstd", "zstandard"):
        if zstd is None:
            raise RuntimeError("zstandard is not installed. Run 'pip install zstandard'.")
        dctx = zstd.ZstdDecompressor()
        decompressed = dctx.decompress(compressed_data, max_output_size=1024 * 1024 * 1024)
    elif algo == "brotli":
        if brotli is None:
            raise RuntimeError("brotli is not installed. Run 'pip install brotli'.")
        decompressed = brotli.decompress(compressed_data)
    elif algo == "lz4":
        if lz4 is None:
            raise RuntimeError("lz4 is not installed. Run 'pip install lz4'.")
        decompressed = lz4.frame.decompress(compressed_data)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    elapsed = time.perf_counter() - start
    return decompressed, elapsed
