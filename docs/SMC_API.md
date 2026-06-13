
# SMC v10.2 — API Reference

**Python Interface for Sentinel Magnetic Control Unit**

---

## Overview

The SMC v10.2 provides a **Python API** for configuration, real-time telemetry monitoring, and deterministic feedback loop control. The API communicates with the FPGA-based control core over Ethernet (TCP/IP) or PCIe, depending on the hardware configuration.

All time-critical operations are executed in hardware (<100 ns). The Python API is for **configuration, calibration, and telemetry logging** — not for the real-time feedback loop itself.

---

## Installation

```bash
pip install smc-driver
```

Or from source:

```bash
git clone https://github.com/karamik/Sentinel-Magnetic-Control-.git
cd Sentinel-Magnetic-Control-
python setup.py install
```

---

## Quick Start

```python
from smc import SMCDriver
import time

# Connect to SMC board
smc = SMCDriver(ip="192.168.2.111")
smc.connect()

# Verify chip DNA (anti-tamper)
print(f"Chip DNA: {smc.get_chip_dna()}")

# Load filter coefficients
coefficients = [16384, -8192, 4096, -2048, 1024]
smc.set_filter_coefficients(coefficients)

# Start hardware feedback loop
smc.start_loop()

# Monitor telemetry
while True:
    telemetry = smc.get_telemetry()
    print(f"Latency: {telemetry['latency_ns']} ns")
    print(f"Field gradient: {telemetry['input_gradient_mT']} mT")
    time.sleep(1)

# Stop loop
smc.stop_loop()
smc.disconnect()
```

---

## Class: `SMCDriver`

### Constructor

```python
SMCDriver(ip=None, device_path=None, timeout=5.0)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `ip` | str | IP address of SMC board (Ethernet mode) |
| `device_path` | str | PCIe device path (e.g., `/dev/smc0`) |
| `timeout` | float | Connection timeout in seconds |

**Note:** Provide either `ip` or `device_path`, not both.

---

### Connection Management

#### `connect()`

Establish connection to SMC board.

```python
smc.connect()
```

**Raises:** `SMCConnectionError` if board not found or authentication fails.

#### `disconnect()`

Close connection and release resources.

```python
smc.disconnect()
```

#### `is_connected() -> bool`

Check if connection is active.

```python
if smc.is_connected():
    print("Connected")
```

---

### Hardware Information

#### `get_chip_dna() -> str`

Read the unique 64-bit chip DNA (eFuse‑locked). Returns hexadecimal string.

```python
dna = smc.get_chip_dna()
print(dna)  # e.g., "0x4002A1B2C3D4E5F6"
```

#### `get_firmware_version() -> str`

Return firmware version.

```python
ver = smc.get_firmware_version()
print(ver)  # e.g., "v10.2.0"
```

#### `get_hardware_temp() -> float`

Read FPGA temperature in Celsius.

```python
temp = smc.get_hardware_temp()
print(f"{temp:.1f}°C")
```

---

### Filter Configuration

#### `set_filter_coefficients(coefficients: List[int])`

Upload MAC matrix coefficients to FPGA hardware.

```python
# Example: 5-tap FIR filter
coefficients = [16384, -8192, 4096, -2048, 1024]
smc.set_filter_coefficients(coefficients)
```

**Notes:**
- Coefficients are 16‑bit signed integers.
- Maximum number of coefficients: 1024 (depends on FPGA resources).
- Operation is **atomic** — coefficients are loaded only after all are written.

#### `get_filter_coefficients() -> List[int]`

Read back current coefficients from hardware.

```python
coeffs = smc.get_filter_coefficients()
print(coeffs)
```

---

### Control Loop

#### `start_loop()`

Activate deterministic hardware feedback loop.

```python
smc.start_loop()
```

**Hardware behavior:** ADC → FPGA (MAC filter) → DAC. Latency <100 ns. Loop continues even if Python client disconnects.

#### `stop_loop()`

Deactivate hardware loop (bypass mode).

```python
smc.stop_loop()
```

**Hardware behavior:** DAC output is zeroed (or set to passive state). ADC still sampled but not fed back.

#### `is_loop_active() -> bool`

Check if hardware loop is running.

```python
if smc.is_loop_active():
    print("Loop active")
else:
    print("Loop stopped")
```

---

### Telemetry

#### `get_telemetry() -> dict`

Read real-time diagnostics. Returns dictionary with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `timestamp` | float | Unix timestamp (seconds) |
| `latency_ns` | float | Round-trip latency (ADC → DAC) in nanoseconds |
| `input_gradient_mT` | float | Measured magnetic field gradient (milliTesla) |
| `dac_output_volts` | float | DAC output voltage |
| `fpga_temp_c` | float | FPGA temperature (°C) |
| `white_rabbit_sync` | bool | White Rabbit PTP sync status |
| `loop_active` | bool | Hardware loop state |

```python
telemetry = smc.get_telemetry()
print(f"Latency: {telemetry['latency_ns']:.2f} ns")
print(f"Field: {telemetry['input_gradient_mT']:.4f} mT")
```

#### `get_telemetry_history(count: int = 100) -> List[dict]`

Retrieve recent telemetry from hardware buffer.

```python
history = smc.get_telemetry_history(1000)
for record in history:
    print(record['latency_ns'])
```

**Note:** Hardware buffer holds up to 10,000 samples. Samples are recorded every 1 ms (1 kHz) regardless of host polling.

---

### White Rabbit Sync

#### `get_wr_status() -> dict`

White Rabbit synchronization status.

| Key | Type | Description |
|-----|------|-------------|
| `locked` | bool | WR lock acquired |
| `offset_ns` | float | Current offset from master (nanoseconds) |
| `drift_ps_per_s` | float | Drift rate (picoseconds per second) |
| `link_quality` | int | 0–100 (100 = perfect) |
| `master_ip` | str | IP of WR master (slave mode only) |

```python
wr = smc.get_wr_status()
if wr['locked']:
    print(f"Offset: {wr['offset_ns']:.3f} ns")
```

#### `wait_wr_lock(timeout: float = 10.0) -> bool`

Wait for White Rabbit lock. Returns `True` if lock acquired within timeout.

```python
if smc.wait_wr_lock(timeout=5.0):
    print("WR synchronized")
else:
    print("Timeout")
```

---

### Configuration Persistence

#### `save_config()`

Save current configuration (coefficients, mode) to onboard flash.

```python
smc.save_config()
```

**Note:** Configuration persists across power cycles.

#### `load_config()`

Load configuration from onboard flash.

```python
smc.load_config()
```

#### `reset_to_defaults()`

Reset all settings to factory defaults.

```python
smc.reset_to_defaults()
```

---

### Low-Level Register Access

#### `write_register(address: int, value: int)`

Write to hardware register (advanced use only).

```python
smc.write_register(0x00, 0x01)  # Start loop
```

#### `read_register(address: int) -> int`

Read hardware register.

```python
status = smc.read_register(0x04)
print(f"DSP status: {status}")
```

---

## Exception Classes

| Exception | Description |
|-----------|-------------|
| `SMCError` | Base exception class |
| `SMCConnectionError` | Connection failed (network/PCIe) |
| `SMCAuthenticationError` | Chip DNA mismatch (tamper detected) |
| `SMCTimeoutError` | Operation timed out |
| `SMCConfigurationError` | Invalid configuration (e.g., wrong coefficients) |

---

## Command-Line Interface (CLI)

The package also provides a command-line utility:

```bash
# Show status
smc-cli --ip 192.168.2.111 status

# Load coefficients from file
smc-cli --ip 192.168.2.111 load-coeffs --file coeffs.txt

# Start loop
smc-cli --ip 192.168.2.111 start

# Monitor telemetry
smc-cli --ip 192.168.2.111 monitor --interval 1

# White Rabbit diagnostics
smc-cli --ip 192.168.2.111 wr-diag

# Save config to flash
smc-cli --ip 192.168.2.111 save-config
```

---

## Examples

### Example 1: Basic Calibration

```python
from smc import SMCDriver
import time

smc = SMCDriver(ip="192.168.2.111")
smc.connect()

# Zero the output
smc.set_filter_coefficients([0])
smc.start_loop()
time.sleep(0.1)

# Read baseline
baseline = smc.get_telemetry()['input_gradient_mT']
print(f"Baseline: {baseline} mT")

# Apply correction
coeffs = [int(16384 * (1 - baseline / 10.0))]
smc.set_filter_coefficients(coeffs)
print("Correction applied")

smc.disconnect()
```

### Example 2: Continuous Monitoring with Logging

```python
from smc import SMCDriver
import csv
import time

smc = SMCDriver(ip="192.168.2.111")
smc.connect()
smc.start_loop()

with open('telemetry.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'latency_ns', 'gradient_mT', 'temp_c'])
    
    for _ in range(3600):  # 1 hour at 1 sample/sec
        t = smc.get_telemetry()
        writer.writerow([t['timestamp'], t['latency_ns'], 
                         t['input_gradient_mT'], t['fpga_temp_c']])
        time.sleep(1)

smc.stop_loop()
smc.disconnect()
```

### Example 3: White Rabbit Synchronized Multi-Node

```python
from smc import SMCDriver
import time

# Master node (provides clock)
master = SMCDriver(ip="192.168.2.1")
master.connect()
master.set_wr_mode("master")
master.start_loop()

# Slave nodes
slaves = []
for i in range(2, 5):
    slave = SMCDriver(ip=f"192.168.2.{i}")
    slave.connect()
    slave.set_wr_mode("slave", master_ip="192.168.2.1")
    slave.wait_wr_lock(timeout=5.0)
    slave.start_loop()
    slaves.append(slave)

# All nodes are now synchronized to <1 ns
print("All nodes synchronized")

# Monitor
while True:
    for s in slaves:
        t = s.get_telemetry()
        print(f"Node {s.ip}: {t['latency_ns']:.2f} ns")
    time.sleep(1)
```

---

## Performance Guarantees

| Operation | Latency | Deterministic |
|-----------|---------|---------------|
| ADC → FPGA → DAC (hardware loop) | **<100 ns** | Yes (constant) |
| `get_telemetry()` call | <1 ms | No (software) |
| `set_filter_coefficients()` | <10 ms | No |
| `start_loop()` / `stop_loop()` | <1 μs | Yes (hardware) |

**Critical:** The real-time feedback loop operates **independently** of Python host. Even if the Python client crashes, the hardware loop continues.

---

## Security

### Chip DNA Verification

Each SMC board has a unique 64‑bit DNA (eFuse‑locked). The driver verifies this DNA on every connection. Tamper attempts (e.g., replacing the FPGA) will fail authentication.

```python
# Will raise SMCAuthenticationError if DNA mismatch
smc.connect()
```

### Bitstream Locking

The evaluation bitstream includes a 4‑hour runtime limit. Production bitstreams are locked to the chip DNA and cannot be used on other boards.

---

## References

- Hardware User Manual: `docs/SMC_HARDWARE.md`
- White Rabbit Synchronization: `docs/WHITE_RABBIT_SYNC.md`
- Example scripts: `examples/`
- Evaluation bitstream: `RELEASES/`

---

## Contact

**International Group of Developers (IGD)**

Email: `totalprotocol@proton.me`  
Telegram: `@tec_support_bot`

*For enterprise licensing and custom DSP development.*

---

## Final Statement

> **"SMC v10.2 — hardware-speed feedback, Python‑easy configuration. Best of both worlds."**

*<100 ns deterministic latency. Sub‑ns synchronization. Ready for big science.*
```
