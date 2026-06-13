
# White Rabbit PTP Synchronization for SMC v10.2

**Sub-nanosecond accuracy for distributed deterministic feedback**

---

## Overview

The SMC v10.2 integrates **White Rabbit (WR)** — an enhanced Precision Time Protocol (PTP) that achieves sub-nanosecond synchronization over standard fiber optic links. Originally developed at CERN for the Large Hadron Collider (LHC) timing distribution, White Rabbit allows multiple SMC nodes to coordinate magnetic field corrections with deterministic phase alignment across kilometers of distance.

For applications like **antimatter trapping (CERN ALPHA)** or **plasma stabilization (tokamaks)**, synchronized multiple SMC nodes are essential. A single SMC can stabilize one magnetic coil. White Rabbit ensures that ten SMC nodes, distributed around a reactor, apply corrections at exactly the same moment — with jitter below 1 nanosecond.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHITE RABBIT — DISTRIBUTED SYNCHRONIZATION               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                │
│   │   SMC #1    │      │   SMC #2    │      │   SMC #N    │                │
│   │  (Master)   │◄────►│  (Slave)    │◄────►│  (Slave)    │                │
│   └──────┬──────┘      └──────┬──────┘      └──────┬──────┘                │
│          │                    │                    │                        │
│          └────────────────────┼────────────────────┘                        │
│                               │                                             │
│                    ┌──────────┴──────────┐                                 │
│                    │   WR FIBER NETWORK  │                                 │
│                    │   (sub-ns accuracy) │                                 │
│                    └─────────────────────┘                                 │
│                                                                              │
│   All SMC nodes share a common notion of time with <1 ns error               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why Sub‑Nanosecond Synchronization Matters

### Problem: Without synchronization

If two SMC nodes apply corrections at slightly different times:

| Time offset | Effect |
|-------------|--------|
| 10 ns | Phase error in magnetic field → plasma instability |
| 100 ns | Coil currents misaligned → reduced trapping efficiency |
| 1 μs | Complete loss of field homogeneity → experiment fails |

### Solution: With White Rabbit

| Parameter | Without WR | With WR |
|-----------|------------|---------|
| Node‑to‑node jitter | 1–10 μs (PTP only) | **<1 ns** |
| Phase accuracy | Poor | **Deterministic** |
| Scalability | Limited to single node | **Unlimited distributed nodes** |
| Deterministic latency | No | **Yes (<100 ns + constant offset)** |

**White Rabbit transforms SMC from a single‑node controller into a distributed real‑time grid.**

---

## Technical Specifications (White Rabbit on SMC)

| Parameter | Value |
|-----------|-------|
| **Synchronization accuracy** | <1 ns (node‑to‑node) |
| **Timebase stability** | <1 ppb (GPS‑disciplined OCXO optional) |
| **Fiber optic link** | 1 Gb/s bidirectional (standard SFP) |
| **Maximum distance** | >10 km between nodes |
| **Protocol** | White Rabbit (IEEE 1588‑2008 extension) |
| **Deterministic latency** | <100 ns (each node) + fixed offset |
| **Clock source** | Internal OCXO / External 10 MHz / GPS‑DO |

### White Rabbit Grandmaster Options

| Source | Accuracy | Application |
|--------|----------|-------------|
| **Internal OCXO** | <1 ppb (holdover) | Standalone, up to 10 nodes |
| **GPS‑disciplined** | <1 ns UTC | Distributed experiments (CERN, ITER) |
| **External 10 MHz** | Application‑dependent | Integration with facility master clock |

---

## Hardware Implementation

### SMC v10.2 White Rabbit Interface

The RFSoC device contains dedicated SERDES transceivers. One transceiver is allocated to the White Rabbit link. The SMC's programmable logic implements:

- **WR PTP core** — hardware timestamping (<1 ns resolution)
- **Clock phase alignment** — digitally controlled oscillator (DCO) to align local clock
- **Deterministic latency compensation** — fixed delay through FPGA fabric

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMC v10.2 — WR IMPLEMENTATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  RFSoC (Zynq UltraScale+)                                           │   │
│   │                                                                      │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│   │  │   SERDES    │───▶│  WR PTP     │───▶│  DCO       │              │   │
│   │  │  (GTY)      │    │  Core       │    │  (Clock)   │              │   │
│   │  └─────────────┘    └─────────────┘    └──────┬──────┘              │   │
│   │                                                │                     │   │
│   │                                                ▼                     │   │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│   │  │  ADC        │    │  MAC/FIR    │    │  DAC       │              │   │
│   │  │  (RF-ADC)   │───▶│  Filter     │───▶│  (RF-DAC)  │              │   │
│   │  └─────────────┘    └─────────────┘    └─────────────┘              │   │
│   │                           ▲                                          │   │
│   │                           │ (all operations aligned to WR clock)    │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Connection Diagram

```
        ┌──────────────┐                          ┌──────────────┐
        │  SMC #1      │◄────── Fiber (WR) ──────►│  SMC #2      │
        │  (Master)    │                          │  (Slave)     │
        └──────┬───────┘                          └──────┬───────┘
               │                                         │
               │                               ┌─────────┴─────────┐
               │                               │                   │
        ┌──────┴───────┐                 ┌─────┴─────┐        ┌─────┴─────┐
        │  Coil Driver │                 │  Sensor  │        │  Sensor  │
        └──────────────┘                 └──────────┘        └──────────┘
```

**Multiple SMC nodes, one common timebase. Corrections applied simultaneously.**

---

## Software API (WR Control)

### Python Example: Checking Synchronization Status

```python
from smc_driver import SMCDriver

smc = SMCDriver(ip="192.168.2.111")
smc.connect()

# Check White Rabbit status
wr_status = smc.get_wr_status()
print(f"White Rabbit locked: {wr_status['locked']}")
print(f"Clock offset: {wr_status['offset_ns']:.3f} ns")
print(f"Fiber link quality: {wr_status['link_quality']}")

# Wait for lock if needed
if not wr_status['locked']:
    print("Waiting for WR lock...")
    smc.wait_wr_lock(timeout=10)  # seconds
    print("Lock acquired.")
```

### Configuration via Command Line

```bash
# Configure SMC as WR master (only one master per network)
smc-config --wr-mode master --wr-port sfp1

# Configure SMC as WR slave
smc-config --wr-mode slave --wr-master-ip 192.168.2.1

# Monitor synchronization quality
smc-monitor --wr-stats
```

---

## Testing & Validation

### How to verify sub‑nanosecond synchronization

| Step | Equipment | Expected result |
|------|-----------|-----------------|
| 1 | Two SMC boards with WR link | Both report `wr_locked = True` |
| 2 | 1 PPS output from each SMC | Phase difference <1 ns (oscilloscope) |
| 3 | Run for 24 hours | Drift <10 ns (due to OCXO stability) |
| 4 | Insert 1 km fiber delay | Automatic compensation, phase still <1 ns |

### Built‑in diagnostic command

```bash
smc-monitor --wr-diag

Output:
WR Status:
  Link: UP (1 Gb/s)
  Mode: Slave
  Master IP: 192.168.2.1
  Offset: +0.23 ns
  Drift: 0.04 ns/s
  Temperature: 43.2°C
```

---

## Applications That Require White Rabbit

| Application | Why WR is required |
|-------------|---------------------|
| **Antimatter trapping (CERN ALPHA)** | Multiple magnetic coils must maintain field homogeneity to keep antihydrogen stable |
| **Tokamak plasma stabilization (ITER, SPARC)** | 10+ magnetic field sensors and actuators distributed around the torus must act in phase |
| **Quantum computing (ion traps)** | Phase coherence across array of trap electrodes |
| **Synchronized beamlines (XFEL, synchrotron)** | Timing distribution across kilometer‑scale facilities |

**Without WR, distributed SMC nodes would drift apart over time. With WR, they remain phase‑locked indefinitely.**

---

## White Rabbit vs Other Synchronization Methods

| Method | Accuracy | Range | Deterministic | SMC support |
|--------|----------|-------|---------------|-------------|
| **PTP (IEEE 1588)** | 1–10 μs | Unlimited | No | ❌ |
| **GPS‑DO** | <10 ns | Global | No (jitter) | ⚠️ (external) |
| **Direct clock distribution** | <100 ps | Short (<10 m) | Yes | ✅ (SMA input) |
| **White Rabbit** | **<1 ns** | >10 km | **Yes** | ✅ (SFP) |

**White Rabbit is the only method that combines sub‑ns accuracy, deterministic latency, and long‑distance fiber links.**

---

## Troubleshooting

### Issue: WR link does not lock

| Possible cause | Solution |
|----------------|----------|
| Fiber cable disconnected | Check physical connection |
| Wrong SFP module | Use SFP rated for 1 Gb/s, single‑mode fiber |
| Two masters on same network | Ensure only one master per WR network |
| Clock source unstable | Check external 10 MHz (if used) |

### Issue: Offset drifts over time

| Possible cause | Solution |
|----------------|----------|
| OCXO aging | Let system warm up for 30 minutes |
| Temperature variation | Ensure proper cooling (SMC monitors temp) |
| GPS‑DO unlocked | Check GPS antenna signal |

### Issue: High jitter

| Possible cause | Solution |
|----------------|----------|
| Non‑WR switch in network | Connect SMC nodes directly (point‑to‑point) or use WR‑capable switch |
| Software timestamping | SMC uses hardware timestamping, verify with `--wr-stats` |

---

## White Rabbit Network Topologies

### Point‑to‑point (two SMC nodes)

```
┌─────────┐        ┌─────────┐
│ SMC #1  │◄──────►│ SMC #2  │
│ (Master)│  Fiber │ (Slave) │
└─────────┘        └─────────┘
```

**Best for:** Small experiments, dual‑coil systems

### Star (one master, multiple slaves)

```
                    ┌─────────┐
               ┌───►│ SMC #2  │
               │    └─────────┘
┌─────────┐    │    ┌─────────┐
│ SMC #1  │────┼───►│ SMC #3  │
│ (Master)│    │    └─────────┘
└─────────┘    │    ┌─────────┐
               └───►│ SMC #4  │
                    └─────────┘
```

**Best for:** Tokamaks, centralized control rooms

### Daisy‑chain (cascaded)

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ SMC #1  │◄──►│ SMC #2  │◄──►│ SMC #3  │
│ (Master)│    │ (Slave) │    │ (Slave) │
└─────────┘    └─────────┘    └─────────┘
```

**Best for:** Long linear facilities (beamlines, accelerators)

---

## References

- White Rabbit project: [https://ohwr.org/project/white-rabbit](https://ohwr.org/project/white-rabbit)
- IEEE 1588‑2008 (PTP) standard
- CERN White Rabbit specification (WR‑PTP)
- SMC v10.2 Hardware User Manual (see `docs/SMC_HARDWARE.md`)

---

## Contact

**International Group of Developers (IGD)**

Email: `totalprotocol@proton.me`  
Telegram: `@tec_support_bot`

*For White Rabbit integration support and custom timing solutions.*

---

## Final Statement

> **"White Rabbit turns SMC nodes into a synchronized swarm. Sub‑nanosecond accuracy. Deterministic latency. Unlimited scale."**

**SMC v10.2 — not just a controller. A distributed time‑machine for big science.**
```
