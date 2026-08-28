import React, { useState } from "react";
import "./App.css";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

function App() {
  const [file, setFile] = useState(null);

  const [algorithm, setAlgorithm] = useState("zstd");

  const [bandwidth, setBandwidth] = useState(10);
  const [routers, setRouters] = useState(3);
  const [latency, setLatency] = useState(10);

  const [result, setResult] = useState(null);
  const [comparison, setComparison] = useState(null);

  const [loading, setLoading] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const [error, setError] = useState("");

  // ==================================================
  // SIMULATION HISTORY
  // ==================================================

  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem("compressionHistory")
      ) || [];
    } catch {
      return [];
    }
  });

  // ==================================================
  // SAVE SIMULATION HISTORY
  // ==================================================

  const saveHistory = (entry) => {
    const newEntry = {
      ...entry,
      id: Date.now(),
      timestamp: new Date().toLocaleString()
    };

    setHistory((previousHistory) => {
      const updatedHistory = [
        newEntry,
        ...previousHistory
      ].slice(0, 20);

      localStorage.setItem(
        "compressionHistory",
        JSON.stringify(updatedHistory)
      );

      return updatedHistory;
    });
  };

  // ==================================================
  // DOWNLOAD COMPRESSED FILE
  // ==================================================

  const downloadCompressedFile = async (
    selectedAlgorithm = algorithm
  ) => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setError("");
    setDownloadLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    const url =
      `http://127.0.0.1:8000/download` +
      `?algorithm=${encodeURIComponent(selectedAlgorithm)}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        let errorMessage = "Unable to download compressed file.";

        try {
          const data = await response.json();

          if (Array.isArray(data.detail)) {
            errorMessage = data.detail
              .map((item) => item.msg)
              .join(", ");
          } else if (data.detail) {
            errorMessage = data.detail;
          }
        } catch {
          // Ignore JSON parsing error
        }

        throw new Error(errorMessage);
      }

      const blob = await response.blob();

      const downloadUrl =
        window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = downloadUrl;

      const originalName =
        file.name || "compressed_file";

      const extensionMap = {
        gzip: ".gz",
        brotli: ".br",
        zstd: ".zst"
      };

      const extension =
        extensionMap[selectedAlgorithm] || ".compressed";

      link.download =
        `${originalName}${extension}`;

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
      console.error(
        "Download error:",
        error
      );

      setError(error.message);

    } finally {
      setDownloadLoading(false);
    }
  };

  // ==================================================
  // RUN SINGLE ALGORITHM SIMULATION
  // ==================================================

  const runSimulation = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setError("");
    setLoading(true);
    setResult(null);

    const formData = new FormData();

    formData.append("file", file);

    const url =
      `http://127.0.0.1:8000/simulate` +
      `?algorithm=${encodeURIComponent(algorithm)}` +
      `&bandwidth_mbps=${encodeURIComponent(bandwidth)}` +
      `&number_of_routers=${encodeURIComponent(routers)}` +
      `&latency_ms=${encodeURIComponent(latency)}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(
            data.detail
              .map((item) => item.msg)
              .join(", ")
          );
        }

        throw new Error(
          data.detail || "Simulation failed."
        );
      }

      console.log(
        "Backend response:",
        data
      );

      setResult(data);

      // Save successful simulation
      saveHistory({
        type: "Single Simulation",
        fileName: file.name,
        algorithm: algorithm.toUpperCase(),

        originalSize:
          data.data?.original_size_bytes ?? 0,

        compressedSize:
          data.data?.compressed_size_bytes ?? 0,

        bandwidthSaved:
          data.data?.bandwidth_saved_percent ?? 0,

        compressionRatio:
          data.data?.compression_ratio ?? "N/A",

        networkImprovement:
          data.network?.network_improvement_percent ?? 0
      });

    } catch (error) {
      console.error(
        "Simulation error:",
        error
      );

      setError(error.message);

    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // COMPARE ALL ALGORITHMS
  // ==================================================

  const compareAlgorithms = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setError("");
    setCompareLoading(true);
    setComparison(null);

    const formData = new FormData();

    formData.append("file", file);

    const url =
      `http://127.0.0.1:8000/compare` +
      `?bandwidth_mbps=${encodeURIComponent(bandwidth)}` +
      `&number_of_routers=${encodeURIComponent(routers)}` +
      `&latency_ms=${encodeURIComponent(latency)}`;

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          throw new Error(
            data.detail
              .map((item) => item.msg)
              .join(", ")
          );
        }

        throw new Error(
          data.detail ||
          "Algorithm comparison failed."
        );
      }

      console.log(
        "Comparison response:",
        data
      );

      setComparison(data);

      // Find best algorithm
      const bestResult =
        data.results?.find(
          (item) =>
            item.algorithm ===
            data.best_algorithm
        );

      // Save comparison to history
      saveHistory({
        type: "Algorithm Comparison",
        fileName: file.name,

        algorithm:
          `Best: ${
            data.best_algorithm?.toUpperCase() ||
            "N/A"
          }`,

        originalSize:
          bestResult?.original_size_bytes ?? 0,

        compressedSize:
          bestResult?.compressed_size_bytes ?? 0,

        bandwidthSaved:
          bestResult?.bandwidth_saved_percent ?? 0,

        compressionRatio:
          bestResult?.compression_ratio ?? "N/A",

        networkImprovement:
          bestResult?.network_improvement_percent ?? 0
      });

    } catch (error) {
      console.error(
        "Comparison error:",
        error
      );

      setError(error.message);

    } finally {
      setCompareLoading(false);
    }
  };

  // ==================================================
  // CHART DATA
  // ==================================================

  const chartData =
    comparison?.results?.map((item) => ({
      algorithm:
        item.algorithm.toUpperCase(),

      compressedSize:
        Number(
          item.compressed_size_bytes
        ) || 0,

      bandwidthSaved:
        Number(
          item.bandwidth_saved_percent
        ) || 0,

      networkImprovement:
        Number(
          item.network_improvement_percent
        ) || 0
    })) || [];

  // ==================================================
  // BAR COLORS
  // ==================================================

  const getBarColor = (algorithmName) => {
    switch (algorithmName) {
      case "GZIP":
        return "#2563eb";

      case "BROTLI":
        return "#16a34a";

      case "ZSTD":
        return "#9333ea";

      default:
        return "#475569";
    }
  };

  // ==================================================
  // CUSTOM BAR LABELS
  // ==================================================

  const renderSizeLabel = (props) => {
    const {
      x,
      y,
      width,
      value
    } = props;

    return (
      <text
        x={x + width / 2}
        y={y - 8}
        textAnchor="middle"
        fontSize={13}
        fontWeight="600"
        fill="#1e293b"
      >
        {Number(value).toLocaleString()}
      </text>
    );
  };

  const renderPercentLabel = (props) => {
    const {
      x,
      y,
      width,
      value
    } = props;

    return (
      <text
        x={x + width / 2}
        y={y - 8}
        textAnchor="middle"
        fontSize={13}
        fontWeight="600"
        fill="#1e293b"
      >
        {Number(value).toFixed(2)}%
      </text>
    );
  };

  // ==================================================
  // PAGE
  // ==================================================

  return (
    <div className="app">

      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="header">

        <h1>
          Backbone Network Data Compression
        </h1>

        <p>
          Data compression and network
          performance optimization
        </p>

      </header>

      <main className="container">

        {/* ==================================================
            INPUT SECTION
        ================================================== */}

        <section className="card">

          <h2>
            Network Simulation
          </h2>

          {/* FILE UPLOAD */}

          <div className="form-group">

            <label>
              Upload Data
            </label>

            <input
              type="file"
              onChange={(event) => {

                setFile(
                  event.target.files[0]
                );

                setError("");
                setResult(null);
                setComparison(null);

              }}
            />

            {file && (
              <p className="file-name">
                Selected: {file.name}
              </p>
            )}

          </div>

          {/* COMPRESSION ALGORITHM */}

          <div className="form-group">

            <label>
              Compression Algorithm
            </label>

            <select
              value={algorithm}
              onChange={(event) =>
                setAlgorithm(
                  event.target.value
                )
              }
            >

              <option value="gzip">
                GZIP
              </option>

              <option value="brotli">
                Brotli
              </option>

              <option value="zstd">
                Zstandard
              </option>

            </select>

          </div>

          {/* NETWORK SETTINGS */}

          <div className="network-grid">

            <div className="form-group">

              <label>
                Bandwidth (Mbps)
              </label>

              <input
                type="number"
                min="1"
                value={bandwidth}
                onChange={(event) =>
                  setBandwidth(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>

            <div className="form-group">

              <label>
                Routers
              </label>

              <input
                type="number"
                min="1"
                value={routers}
                onChange={(event) =>
                  setRouters(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>

            <div className="form-group">

              <label>
                Latency (ms)
              </label>

              <input
                type="number"
                min="0"
                value={latency}
                onChange={(event) =>
                  setLatency(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

            </div>

          </div>

          {/* ERROR */}

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {/* BUTTONS */}

          <div className="button-group">

            <button
              className="simulate-button"
              onClick={runSimulation}
              disabled={
                loading ||
                compareLoading ||
                downloadLoading
              }
            >

              {loading
                ? "Running Simulation..."
                : "Start Simulation"}

            </button>

            <button
              className="compare-button"
              onClick={compareAlgorithms}
              disabled={
                loading ||
                compareLoading ||
                downloadLoading
              }
            >

              {compareLoading
                ? "Comparing Algorithms..."
                : "Compare All Algorithms"}

            </button>

          </div>

        </section>

        {/* ==================================================
            SINGLE SIMULATION RESULTS
        ================================================== */}

        {result && (

          <section className="results">

            <h2>
              Simulation Results
            </h2>

            {/* DOWNLOAD SECTION */}

            <div className="download-section">

              <div>

                <h3>
                  Download Compressed File
                </h3>

                <p>
                  Download the uploaded file
                  compressed using{" "}
                  <strong>
                    {algorithm.toUpperCase()}
                  </strong>.
                </p>

              </div>

              <button
                className="download-button"
                onClick={() =>
                  downloadCompressedFile(
                    algorithm
                  )
                }
                disabled={
                  downloadLoading
                }
              >

                {downloadLoading
                  ? "Preparing Download..."
                  : "⬇ Download Compressed File"}

              </button>

            </div>

            {/* COMPRESSION RESULTS */}

            <h3>
              Compression Results
            </h3>

            <div className="result-grid">

              <div className="result-card">

                <span>
                  Original Size
                </span>

                <strong>
                  {result.data
                    ?.original_size_bytes ??
                    "N/A"}{" "}
                  bytes
                </strong>

              </div>

              <div className="result-card">

                <span>
                  Compressed Size
                </span>

                <strong>
                  {result.data
                    ?.compressed_size_bytes ??
                    "N/A"}{" "}
                  bytes
                </strong>

              </div>

              <div className="result-card">

                <span>
                  Bandwidth Saved
                </span>

                <strong>
                  {result.data
                    ?.bandwidth_saved_percent ??
                    "N/A"}%
                </strong>

              </div>

              <div className="result-card">

                <span>
                  Compression Ratio
                </span>

                <strong>
                  {result.data
                    ?.compression_ratio ??
                    "N/A"}
                </strong>

              </div>

            </div>

            {/* COMPRESSION PERFORMANCE */}

            <div className="comparison">

              <h3>
                Compression Performance
              </h3>

              <p>
                Compression Time:
                <strong>
                  {" "}
                  {result.compression
                    ?.compression_time_seconds ??
                    "N/A"}{" "}
                  seconds
                </strong>
              </p>

              <p>
                Decompression Time:
                <strong>
                  {" "}
                  {result.compression
                    ?.decompression_time_seconds ??
                    "N/A"}{" "}
                  seconds
                </strong>
              </p>

            </div>

            {/* NETWORK PERFORMANCE */}

            <div className="comparison">

              <h3>
                Backbone Network Performance
              </h3>

              <p>
                Network Bandwidth:
                <strong>
                  {" "}
                  {result.network
                    ?.bandwidth_mbps ??
                    "N/A"}{" "}
                  Mbps
                </strong>
              </p>

              <p>
                Number of Routers:
                <strong>
                  {" "}
                  {result.network
                    ?.number_of_routers ??
                    "N/A"}
                </strong>
              </p>

              <p>
                Latency:
                <strong>
                  {" "}
                  {result.network
                    ?.latency_ms_per_router ??
                    "N/A"}{" "}
                  ms
                </strong>
              </p>

              <p>
                Without Compression:
                <strong>
                  {" "}
                  {result.network
                    ?.time_without_compression_seconds ??
                    "N/A"}{" "}
                  seconds
                </strong>
              </p>

              <p>
                With Compression:
                <strong>
                  {" "}
                  {result.network
                    ?.time_with_compression_seconds ??
                    "N/A"}{" "}
                  seconds
                </strong>
              </p>

              <p>
                Network Time Saved:
                <strong>
                  {" "}
                  {result.network
                    ?.network_time_saved_seconds ??
                    "N/A"}{" "}
                  seconds
                </strong>
              </p>

              <p>
                Network Improvement:
                <strong>
                  {" "}
                  {result.network
                    ?.network_improvement_percent ??
                    "N/A"}
                  %
                </strong>
              </p>

            </div>

            {/* DATA INTEGRITY */}

            <div className="integrity">

              <h3>
                Data Integrity
              </h3>

              <p>
                Status:
                <strong>
                  {" "}
                  {result.integrity
                    ?.status ??
                    "N/A"}
                </strong>
              </p>

            </div>

          </section>

        )}

        {/* ==================================================
            ALGORITHM COMPARISON
        ================================================== */}

        {comparison && (

          <section className="results">

            <h2>
              Algorithm Comparison
            </h2>

            <p>
              The same file was tested using
              GZIP, Brotli and Zstandard.
            </p>

            {/* COMPARISON TABLE */}

            <div className="comparison-table">

              <table>

                <thead>

                  <tr>
                    <th>Algorithm</th>
                    <th>Compressed Size</th>
                    <th>Compression Ratio</th>
                    <th>Bandwidth Saved</th>
                    <th>Compression Time</th>
                    <th>Network Improvement</th>
                    <th>Integrity</th>
                  </tr>

                </thead>

                <tbody>

                  {comparison.results?.map(
                    (item) => (

                      <tr
                        key={
                          item.algorithm
                        }
                      >

                        <td>
                          <strong>
                            {item.algorithm.toUpperCase()}
                          </strong>
                        </td>

                        <td>
                          {Number(
                            item.compressed_size_bytes
                          ).toLocaleString()}{" "}
                          bytes
                        </td>

                        <td>
                          {item.compression_ratio}
                        </td>

                        <td>
                          {item.bandwidth_saved_percent}%
                        </td>

                        <td>
                          {item.compression_time_seconds}{" "}
                          sec
                        </td>

                        <td>
                          {item.network_improvement_percent}%
                        </td>

                        <td>
                          {item.integrity}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

            {/* BEST ALGORITHM */}

            <div className="best-algorithm">

              🏆 Best Algorithm:

              <strong>
                {" "}
                {comparison.best_algorithm?.toUpperCase()}
              </strong>

            </div>

            {/* DOWNLOAD BEST ALGORITHM */}

            <div className="download-section">

              <div>

                <h3>
                  Download Best Compression
                </h3>

                <p>
                  Download the file using the
                  best-performing algorithm:
                  {" "}
                  <strong>
                    {comparison.best_algorithm?.toUpperCase()}
                  </strong>
                </p>

              </div>

              <button
                className="download-button"
                onClick={() =>
                  downloadCompressedFile(
                    comparison.best_algorithm
                  )
                }
                disabled={
                  downloadLoading
                }
              >

                {downloadLoading
                  ? "Preparing Download..."
                  : "⬇ Download Best Compressed File"}

              </button>

            </div>

            {/* PERFORMANCE CHARTS */}

            <div className="charts-section">

              <h3>
                Compression Performance Analytics
              </h3>

              {/* COMPRESSED SIZE */}

              <div className="chart-card">

                <h4>
                  Compressed Data Size
                </h4>

                <ResponsiveContainer
                  width="100%"
                  height={360}
                >

                  <BarChart
                    data={chartData}
                    margin={{
                      top: 35,
                      right: 30,
                      left: 30,
                      bottom: 45
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="algorithm"
                      tick={{
                        fontSize: 14,
                        fontWeight: 600
                      }}
                      tickMargin={10}
                    />

                    <YAxis
                      tickFormatter={(value) =>
                        Number(
                          value
                        ).toLocaleString()
                      }
                      label={{
                        value: "Size (bytes)",
                        angle: -90,
                        position: "insideLeft"
                      }}
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${Number(
                          value
                        ).toLocaleString()} bytes`,
                        "Compressed Size"
                      ]}
                    />

                    <Bar
                      dataKey="compressedSize"
                      name="Compressed Size"
                      radius={[
                        6,
                        6,
                        0,
                        0
                      ]}
                      label={
                        renderSizeLabel
                      }
                    >

                      {chartData.map(
                        (entry) => (

                          <Cell
                            key={
                              entry.algorithm
                            }
                            fill={
                              getBarColor(
                                entry.algorithm
                              )
                            }
                          />

                        )
                      )}

                    </Bar>

                  </BarChart>

                </ResponsiveContainer>

              </div>

              {/* BANDWIDTH SAVED */}

              <div className="chart-card">

                <h4>
                  Bandwidth Saved
                </h4>

                <ResponsiveContainer
                  width="100%"
                  height={360}
                >

                  <BarChart
                    data={chartData}
                    margin={{
                      top: 35,
                      right: 30,
                      left: 30,
                      bottom: 45
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="algorithm"
                      tick={{
                        fontSize: 14,
                        fontWeight: 600
                      }}
                      tickMargin={10}
                    />

                    <YAxis
                      unit="%"
                      tickFormatter={(value) =>
                        `${value}%`
                      }
                      label={{
                        value:
                          "Bandwidth Saved (%)",
                        angle: -90,
                        position: "insideLeft"
                      }}
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${Number(
                          value
                        ).toFixed(2)}%`,
                        "Bandwidth Saved"
                      ]}
                    />

                    <Bar
                      dataKey="bandwidthSaved"
                      name="Bandwidth Saved"
                      radius={[
                        6,
                        6,
                        0,
                        0
                      ]}
                      label={
                        renderPercentLabel
                      }
                    >

                      {chartData.map(
                        (entry) => (

                          <Cell
                            key={
                              entry.algorithm
                            }
                            fill={
                              getBarColor(
                                entry.algorithm
                              )
                            }
                          />

                        )
                      )}

                    </Bar>

                  </BarChart>

                </ResponsiveContainer>

              </div>

              {/* NETWORK IMPROVEMENT */}

              <div className="chart-card">

                <h4>
                  Backbone Network Improvement
                </h4>

                <ResponsiveContainer
                  width="100%"
                  height={360}
                >

                  <BarChart
                    data={chartData}
                    margin={{
                      top: 35,
                      right: 30,
                      left: 30,
                      bottom: 45
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="algorithm"
                      tick={{
                        fontSize: 14,
                        fontWeight: 600
                      }}
                      tickMargin={10}
                    />

                    <YAxis
                      unit="%"
                      tickFormatter={(value) =>
                        `${value}%`
                      }
                      label={{
                        value:
                          "Network Improvement (%)",
                        angle: -90,
                        position: "insideLeft"
                      }}
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${Number(
                          value
                        ).toFixed(2)}%`,
                        "Network Improvement"
                      ]}
                    />

                    <Bar
                      dataKey="networkImprovement"
                      name="Network Improvement"
                      radius={[
                        6,
                        6,
                        0,
                        0
                      ]}
                      label={
                        renderPercentLabel
                      }
                    >

                      {chartData.map(
                        (entry) => (

                          <Cell
                            key={
                              entry.algorithm
                            }
                            fill={
                              getBarColor(
                                entry.algorithm
                              )
                            }
                          />

                        )
                      )}

                    </Bar>

                  </BarChart>

                </ResponsiveContainer>

              </div>

            </div>

            {/* ==================================================
                BACKBONE NETWORK VISUALIZATION
            ================================================== */}

            <div className="network-section">

              <h3>
                Backbone Network Topology
              </h3>

              <div className="network-diagram">

                <div className="network-node network-source">
                  SOURCE
                </div>

                {Array.from(
                  {
                    length:
                      comparison.network
                        ?.number_of_routers ||
                      routers
                  },
                  (_, index) => (

                    <React.Fragment
                      key={index}
                    >

                      <div className="network-link">
                      </div>

                      <div className="network-node">
                        R{index + 1}
                      </div>

                    </React.Fragment>

                  )
                )}

                <div className="network-link">
                </div>

                <div className="network-node network-destination">
                  DESTINATION
                </div>

              </div>

              <div className="network-info">

                <div className="network-info-card">

                  <span>
                    Bandwidth
                  </span>

                  <strong>
                    {
                      comparison.network
                        ?.bandwidth_mbps
                    }{" "}
                    Mbps
                  </strong>

                </div>

                <div className="network-info-card">

                  <span>
                    Routers
                  </span>

                  <strong>
                    {
                      comparison.network
                        ?.number_of_routers
                    }
                  </strong>

                </div>

                <div className="network-info-card">

                  <span>
                    Latency
                  </span>

                  <strong>
                    {
                      comparison.network
                        ?.latency_ms_per_router
                    }{" "}
                    ms
                  </strong>

                </div>

              </div>

            </div>

            {/* NETWORK SETTINGS */}

            <div className="comparison">

              <h3>
                Test Network Configuration
              </h3>

              <p>
                Bandwidth:
                <strong>
                  {" "}
                  {
                    comparison.network
                      ?.bandwidth_mbps
                  }{" "}
                  Mbps
                </strong>
              </p>

              <p>
                Routers:
                <strong>
                  {" "}
                  {
                    comparison.network
                      ?.number_of_routers
                  }
                </strong>
              </p>

              <p>
                Latency:
                <strong>
                  {" "}
                  {
                    comparison.network
                      ?.latency_ms_per_router
                  }{" "}
                  ms
                </strong>
              </p>

            </div>

          </section>

        )}

        {/* ==================================================
            SIMULATION HISTORY
        ================================================== */}

        <section className="history-section">

          <div className="history-header">

            <div>

              <h2>
                Simulation History
              </h2>

              <p>
                Previous compression and
                network simulation tests
              </p>

            </div>

            {history.length > 0 && (

              <button
                className="clear-history-button"
                onClick={() => {

                  localStorage.removeItem(
                    "compressionHistory"
                  );

                  setHistory([]);

                }}
              >
                Clear History
              </button>

            )}

          </div>

          {history.length === 0 ? (

            <div className="empty-history">

              <div className="empty-history-icon">
                📊
              </div>

              <h3>
                No simulation history yet
              </h3>

              <p>
                Run a simulation or compare
                algorithms to see your results
                here.
              </p>

            </div>

          ) : (

            <div className="history-table-wrapper">

              <table className="history-table">

                <thead>

                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Algorithm</th>
                    <th>Compressed Size</th>
                    <th>Bandwidth Saved</th>
                    <th>Network Improvement</th>
                  </tr>

                </thead>

                <tbody>

                  {history.map((item) => (

                    <tr
                      key={item.id}
                    >

                      <td>
                        {item.timestamp}
                      </td>

                      <td>

                        <span className="history-type">
                          {item.type}
                        </span>

                      </td>

                      <td>
                        {item.fileName}
                      </td>

                      <td>

                        <strong>
                          {item.algorithm}
                        </strong>

                      </td>

                      <td>
                        {Number(
                          item.compressedSize
                        ).toLocaleString()}{" "}
                        bytes
                      </td>

                      <td>
                        {Number(
                          item.bandwidthSaved
                        ).toFixed(2)}%
                      </td>

                      <td>
                        {Number(
                          item.networkImprovement
                        ).toFixed(2)}%
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </section>

      </main>

    </div>
  );
}

export default App;