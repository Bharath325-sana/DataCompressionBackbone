from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import uuid
from datetime import datetime

from compression.compression_engine import (
    compress_data,
    decompress_data,
    get_compression_stats,
    calculate_hash
)

from network.network_simulator import (
    simulate_backbone_network
)

from security.security_engine import (
    encrypt_data,
    decrypt_data,
    calculate_sha256
)


# ==================================================
# APPLICATION
# ==================================================

app = FastAPI(
    title="Backbone Network Data Compression System",
    description="Data compression, security and backbone network simulation system",
    version="2.0.0"
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# SUPPORTED ALGORITHMS
# ==================================================

SUPPORTED_ALGORITHMS = [
    "gzip",
    "brotli",
    "zstd"
]


# ==================================================
# STORAGE DIRECTORY
# ==================================================

STORAGE_DIR = "storage"

os.makedirs(STORAGE_DIR, exist_ok=True)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "message": "Backbone Network Data Compression System is running!",
        "version": "2.0.0"
    }


# ==================================================
# GET SUPPORTED ALGORITHMS
# ==================================================

@app.get("/algorithms")
def get_algorithms():
    return {
        "supported_algorithms": SUPPORTED_ALGORITHMS
    }


# ==================================================
# COMPRESS FILE
# ==================================================

@app.post("/compress")
async def compress_file(
    algorithm: str,
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # VALIDATE ALGORITHM
    # ----------------------------------------------

    if algorithm not in SUPPORTED_ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported compression algorithm"
        )

    # ----------------------------------------------
    # READ FILE
    # ----------------------------------------------

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    # ----------------------------------------------
    # ORIGINAL HASH
    # ----------------------------------------------

    original_hash = calculate_hash(data)

    # ----------------------------------------------
    # COMPRESS
    # ----------------------------------------------

    compressed_data, compression_time = compress_data(
        data,
        algorithm
    )

    # ----------------------------------------------
    # STATISTICS
    # ----------------------------------------------

    stats = get_compression_stats(
        data,
        compressed_data
    )

    return {
        "filename": file.filename,
        "algorithm": algorithm,

        "original_size_bytes":
            stats["original_size"],

        "compressed_size_bytes":
            stats["compressed_size"],

        "compression_ratio":
            stats["compression_ratio"],

        "bandwidth_saved_percent":
            stats["space_saved_percent"],

        "compression_time_seconds":
            round(compression_time, 6),

        "original_hash":
            original_hash
    }


# ==================================================
# COMPLETE SECURE PROCESS
#
# UPLOAD
#   ↓
# COMPRESS
#   ↓
# SECURE / ENCRYPT
#   ↓
# STORE
#   ↓
# RETRIEVE
#   ↓
# DECRYPT
#   ↓
# DECOMPRESS
#   ↓
# VERIFY
#   ↓
# OUTPUT
# ==================================================

@app.post("/process")
async def complete_process(
    algorithm: str,
    file: UploadFile = File(...)
):

    # ==================================================
    # STEP 1 — VALIDATE
    # ==================================================

    if algorithm not in SUPPORTED_ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported compression algorithm"
        )

    # ==================================================
    # STEP 2 — UPLOAD
    # ==================================================

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    original_size = len(data)

    # ==================================================
    # STEP 3 — ORIGINAL HASH
    # ==================================================

    original_hash = calculate_sha256(data)

    # ==================================================
    # STEP 4 — COMPRESS
    # ==================================================

    compressed_data, compression_time = compress_data(
        data,
        algorithm
    )

    compression_stats = get_compression_stats(
        data,
        compressed_data
    )

    compressed_size = len(compressed_data)

    # ==================================================
    # STEP 5 — SECURE / ENCRYPT
    # ==================================================

    encrypted_data = encrypt_data(
        compressed_data
    )

    encrypted_size = len(encrypted_data)

    encrypted_hash = calculate_sha256(
        encrypted_data
    )

    # ==================================================
    # STEP 6 — STORE
    # ==================================================

    unique_id = str(uuid.uuid4())

    safe_filename = (
        f"{unique_id}_{file.filename}.encrypted"
    )

    storage_path = os.path.join(
        STORAGE_DIR,
        safe_filename
    )

    with open(storage_path, "wb") as stored_file:
        stored_file.write(encrypted_data)

    # ==================================================
    # STEP 7 — VERIFY STORAGE
    # ==================================================

    if not os.path.exists(storage_path):
        raise HTTPException(
            status_code=500,
            detail="Failed to store encrypted data"
        )

    stored_size = os.path.getsize(
        storage_path
    )

    # ==================================================
    # STEP 8 — READ STORED DATA
    # ==================================================

    with open(storage_path, "rb") as stored_file:
        stored_encrypted_data = stored_file.read()

    stored_hash = calculate_sha256(
        stored_encrypted_data
    )

    storage_integrity = (
        encrypted_hash == stored_hash
    )

    # ==================================================
    # STEP 9 — DECRYPT
    # ==================================================

    decrypted_compressed_data = decrypt_data(
        stored_encrypted_data
    )

    # ==================================================
    # STEP 10 — DECOMPRESS
    # ==================================================

    decompressed_data, decompression_time = (
        decompress_data(
            decrypted_compressed_data,
            algorithm
        )
    )

    # ==================================================
    # STEP 11 — VERIFY ORIGINAL DATA
    # ==================================================

    decompressed_hash = calculate_sha256(
        decompressed_data
    )

    verification_passed = (
        original_hash == decompressed_hash
    )

    # ==================================================
    # STEP 12 — FINAL STATUS
    # ==================================================

    if verification_passed:
        verification_status = "PASSED"
    else:
        verification_status = "FAILED"

    # ==================================================
    # STEP 13 — OUTPUT
    # ==================================================

    return {

        "filename": file.filename,

        "algorithm": algorithm,

        "process_id": unique_id,

        "workflow": {

            "upload": "COMPLETED",

            "compression": "COMPLETED",

            "security": "COMPLETED",

            "storage": "COMPLETED",

            "decompression": "COMPLETED",

            "verification":
                verification_status,

            "output":
                "COMPLETED"
        },

        "compression": {

            "original_size_bytes":
                original_size,

            "compressed_size_bytes":
                compressed_size,

            "compression_ratio":
                compression_stats[
                    "compression_ratio"
                ],

            "bandwidth_saved_percent":
                compression_stats[
                    "space_saved_percent"
                ],

            "compression_time_seconds":
                round(
                    compression_time,
                    6
                ),

            "decompression_time_seconds":
                round(
                    decompression_time,
                    6
                )
        },

        "security": {

            "encryption":
                "COMPLETED",

            "encrypted_size_bytes":
                encrypted_size,

            "original_sha256":
                original_hash,

            "encrypted_sha256":
                encrypted_hash
        },

        "storage": {

            "status":
                "STORED",

            "filename":
                safe_filename,

            "stored_size_bytes":
                stored_size,

            "storage_integrity":
                "PASSED"
                if storage_integrity
                else "FAILED",

            "stored_sha256":
                stored_hash
        },

        "verification": {

            "status":
                verification_status,

            "original_hash":
                original_hash,

            "decompressed_hash":
                decompressed_hash,

            "data_integrity":
                "VERIFIED"
                if verification_passed
                else "FAILED"
        },

        "output": {

            "original_file":
                file.filename,

            "processed_successfully":
                verification_passed,

            "message":
                "File compressed, secured, stored, "
                "decompressed and verified successfully."
                if verification_passed
                else
                "Data verification failed."
        },

        "timestamp":
            datetime.now().isoformat()
    }


# ==================================================
# SIMULATE BACKBONE NETWORK
# ==================================================

@app.post("/simulate")
async def simulate(
    algorithm: str,
    bandwidth_mbps: float,
    number_of_routers: int,
    latency_ms: float,
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # VALIDATE ALGORITHM
    # ----------------------------------------------

    if algorithm not in SUPPORTED_ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported compression algorithm"
        )

    # ----------------------------------------------
    # VALIDATE BANDWIDTH
    # ----------------------------------------------

    if bandwidth_mbps <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bandwidth must be greater than zero"
        )

    # ----------------------------------------------
    # VALIDATE ROUTERS
    # ----------------------------------------------

    if number_of_routers <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of routers must be greater than zero"
        )

    # ----------------------------------------------
    # VALIDATE LATENCY
    # ----------------------------------------------

    if latency_ms < 0:
        raise HTTPException(
            status_code=400,
            detail="Latency cannot be negative"
        )

    # ----------------------------------------------
    # READ DATA
    # ----------------------------------------------

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    # ----------------------------------------------
    # ORIGINAL HASH
    # ----------------------------------------------

    original_hash = calculate_hash(data)

    # ----------------------------------------------
    # WITHOUT COMPRESSION
    # ----------------------------------------------

    uncompressed_network = (
        simulate_backbone_network(
            data_size_bytes=len(data),
            bandwidth_mbps=bandwidth_mbps,
            number_of_routers=number_of_routers,
            latency_ms=latency_ms
        )
    )

    # ----------------------------------------------
    # COMPRESSION
    # ----------------------------------------------

    compressed_data, compression_time = (
        compress_data(
            data,
            algorithm
        )
    )

    compression_stats = (
        get_compression_stats(
            data,
            compressed_data
        )
    )

    # ----------------------------------------------
    # WITH COMPRESSION
    # ----------------------------------------------

    compressed_network = (
        simulate_backbone_network(
            data_size_bytes=len(compressed_data),
            bandwidth_mbps=bandwidth_mbps,
            number_of_routers=number_of_routers,
            latency_ms=latency_ms
        )
    )

    # ----------------------------------------------
    # DECOMPRESSION
    # ----------------------------------------------

    decompressed_data, decompression_time = (
        decompress_data(
            compressed_data,
            algorithm
        )
    )

    # ----------------------------------------------
    # INTEGRITY
    # ----------------------------------------------

    decompressed_hash = calculate_hash(
        decompressed_data
    )

    integrity_passed = (
        original_hash == decompressed_hash
    )

    # ----------------------------------------------
    # NETWORK PERFORMANCE
    # ----------------------------------------------

    time_without_compression = (
        uncompressed_network[
            "total_network_time_seconds"
        ]
    )

    time_with_compression = (
        compressed_network[
            "total_network_time_seconds"
        ]
    )

    network_time_saved = (
        time_without_compression
        - time_with_compression
    )

    if time_without_compression > 0:

        network_improvement_percent = (
            network_time_saved
            / time_without_compression
        ) * 100

    else:

        network_improvement_percent = 0

    # ----------------------------------------------
    # RESULT
    # ----------------------------------------------

    return {

        "filename":
            file.filename,

        "algorithm":
            algorithm,

        "data": {

            "original_size_bytes":
                compression_stats[
                    "original_size"
                ],

            "compressed_size_bytes":
                compression_stats[
                    "compressed_size"
                ],

            "compression_ratio":
                compression_stats[
                    "compression_ratio"
                ],

            "bandwidth_saved_percent":
                compression_stats[
                    "space_saved_percent"
                ]
        },

        "compression": {

            "compression_time_seconds":
                round(
                    compression_time,
                    6
                ),

            "decompression_time_seconds":
                round(
                    decompression_time,
                    6
                )
        },

        "network": {

            "bandwidth_mbps":
                bandwidth_mbps,

            "number_of_routers":
                number_of_routers,

            "latency_ms_per_router":
                latency_ms,

            "time_without_compression_seconds":
                time_without_compression,

            "time_with_compression_seconds":
                time_with_compression,

            "network_time_saved_seconds":
                round(
                    network_time_saved,
                    6
                ),

            "network_improvement_percent":
                round(
                    network_improvement_percent,
                    2
                )
        },

        "integrity": {

            "status":
                "PASSED"
                if integrity_passed
                else "FAILED",

            "original_hash":
                original_hash,

            "decompressed_hash":
                decompressed_hash
        }
    }


# ==================================================
# COMPARE ALL COMPRESSION ALGORITHMS
# ==================================================

@app.post("/compare")
async def compare_algorithms(
    bandwidth_mbps: float = 10,
    number_of_routers: int = 3,
    latency_ms: float = 10,
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # VALIDATION
    # ----------------------------------------------

    if bandwidth_mbps <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bandwidth must be greater than zero"
        )

    if number_of_routers <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of routers must be greater than zero"
        )

    if latency_ms < 0:
        raise HTTPException(
            status_code=400,
            detail="Latency cannot be negative"
        )

    # ----------------------------------------------
    # READ FILE
    # ----------------------------------------------

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    # ----------------------------------------------
    # ORIGINAL HASH
    # ----------------------------------------------

    original_hash = calculate_hash(data)

    comparison_results = []

    # ----------------------------------------------
    # TEST ALGORITHMS
    # ----------------------------------------------

    for algorithm in SUPPORTED_ALGORITHMS:

        compressed_data, compression_time = (
            compress_data(
                data,
                algorithm
            )
        )

        stats = get_compression_stats(
            data,
            compressed_data
        )

        decompressed_data, decompression_time = (
            decompress_data(
                compressed_data,
                algorithm
            )
        )

        decompressed_hash = calculate_hash(
            decompressed_data
        )

        integrity_passed = (
            original_hash == decompressed_hash
        )

        # ------------------------------------------
        # NETWORK
        # ------------------------------------------

        uncompressed_network = (
            simulate_backbone_network(
                data_size_bytes=len(data),
                bandwidth_mbps=bandwidth_mbps,
                number_of_routers=number_of_routers,
                latency_ms=latency_ms
            )
        )

        compressed_network = (
            simulate_backbone_network(
                data_size_bytes=len(compressed_data),
                bandwidth_mbps=bandwidth_mbps,
                number_of_routers=number_of_routers,
                latency_ms=latency_ms
            )
        )

        time_without_compression = (
            uncompressed_network[
                "total_network_time_seconds"
            ]
        )

        time_with_compression = (
            compressed_network[
                "total_network_time_seconds"
            ]
        )

        network_time_saved = (
            time_without_compression
            - time_with_compression
        )

        if time_without_compression > 0:

            network_improvement_percent = (
                network_time_saved
                / time_without_compression
            ) * 100

        else:

            network_improvement_percent = 0

        comparison_results.append({

            "algorithm":
                algorithm,

            "original_size_bytes":
                stats["original_size"],

            "compressed_size_bytes":
                stats["compressed_size"],

            "compression_ratio":
                stats["compression_ratio"],

            "bandwidth_saved_percent":
                stats["space_saved_percent"],

            "compression_time_seconds":
                round(
                    compression_time,
                    6
                ),

            "decompression_time_seconds":
                round(
                    decompression_time,
                    6
                ),

            "network_time_saved_seconds":
                round(
                    network_time_saved,
                    6
                ),

            "network_improvement_percent":
                round(
                    network_improvement_percent,
                    2
                ),

            "integrity":
                "PASSED"
                if integrity_passed
                else "FAILED"
        })

    # ----------------------------------------------
    # BEST ALGORITHM
    # ----------------------------------------------

    best_algorithm = max(
        comparison_results,
        key=lambda result:
            result["bandwidth_saved_percent"]
    )

    # ----------------------------------------------
    # RESULT
    # ----------------------------------------------

    return {

        "filename":
            file.filename,

        "original_size_bytes":
            len(data),

        "network": {

            "bandwidth_mbps":
                bandwidth_mbps,

            "number_of_routers":
                number_of_routers,

            "latency_ms_per_router":
                latency_ms
        },

        "results":
            comparison_results,

        "best_algorithm":
            best_algorithm["algorithm"]
    }