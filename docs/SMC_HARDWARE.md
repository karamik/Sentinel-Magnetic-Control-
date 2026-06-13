
# SMC v10.2 — Hardware Reference Manual

**For CERN, DESY, Fermilab, and Big Science Integration**

---

## Overview

The SMC v10.2 (Sentinel Magnetic Control Unit) is a **deterministic, ultra‑low‑latency controller** for magnetic field stabilisation, beam steering, and feedback control in particle accelerators, antimatter traps, and fusion experiments.

Unlike CPU‑based or PLC‑based systems, the SMC offloads the entire feedback loop into **hardened FPGA gates**, achieving a **pin‑to‑pin latency of <100 ns** — deterministic and jitter‑free.

This document provides the hardware specifications required for integration into CERN DI/OT crates, EPICS environments, and experimental beamlines.

---

## Key Specifications

| Parameter | Value |
|-----------|-------|
| **Form factor** | 3U CPCI‑S.0 (PICMG 2.0) |
| **FPGA** | AMD/Xilinx Zynq UltraScale+ RFSoC (ZU28DR) |
| **ADC** | 4 × 14‑bit, 4 GSPS (RF‑ADC) |
| **DAC** | 4 × 14‑bit, 6 GSPS (RF‑DAC) |
| **Deterministic latency** | <100 ns (pin‑to‑pin, including DSP) |
| **White Rabbit support** | Yes (integrated SFP, <1 ns sync) |
| **Clock synchronization** | White Rabbit PTP (IEEE 1588‑2008) |
| **PCIe interface** | Gen3 x8 (for host communication) |
| **Front panel I/O** | 4 × SMA (ADC/DAC), 2 × SFP (WR, data) |
| **Backplane I/O** | P2: 32 LVDS, P3: 8 × 1 Gb/s serial |
| **Power consumption** | 25–40 W (typical) |
| **Cooling** | Conduction‑cooled (for vacuum) or forced air |
| **MTBF** | >100,000 hours (calculated per MIL‑HDBK‑217) |
| **Radiation tolerance** | TID >30 krad (tested for LHC injection zones) |

---

## Board Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SMC v10.2 — TOP VIEW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│   │  SMA    │    │  SMA    │    │  SMA    │    │  SMA    │   Front panel   │
│   │  ADC0   │    │  ADC1   │    │  DAC0   │    │  DAC1   │                 │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘                 │
│        │              │              │              │                       │
│   ┌────┴──────────────┴──────────────┴──────────────┴────┐                  │
│   │                  RFSoC (ZU28DR)                      │                  │
│   │   • 4 × RF‑ADC (4 GSPS)                             │                  │
│   │   • 4 × RF‑DAC (6 GSPS)                             │                  │
│   │   • ARM Cortex‑A53 (PS)                             │                  │
│   │   • Programmable Logic (PL)                         │                  │
│   └───────────────────────┬──────────────────────────────┘                  │
│                           │                                                 │
│   ┌───────────────────────┴───────────────────────────────┐                 │
│   │   DDR4 RAM (4 GB)                                    │                 │
│   └───────────────────────┬───────────────────────────────┘                 │
│                           │                                                 │
│   ┌───────────────────────┴───────────────────────────────┐                 │
│   │   SFP (White Rabbit)      SFP (Data / Timing)        │                 │
│   └───────────────────────┬───────────────────────────────┘                 │
│                           │                                                 │
│   ┌───────────────────────┴───────────────────────────────┐                 │
│   │   P2 Connector (32 LVDS)    P3 Connector (8 × 1 Gb/s) │                 │
│   │   (Backplane I/O)            (Backplane serial)       │                 │
│   └───────────────────────────────────────────────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Mechanical Specifications

### Dimensions

| Parameter | Value |
|-----------|-------|
| **Height** | 3U (128.7 mm) |
| **Width** | 4 HP (20.3 mm) — single‑width |
| **Depth** | 160 mm (standard) or 220 mm (extended) |
| **Weight** | 0.6 kg |

### CPCI Connectors

| Connector | Type | Pins | Use |
|-----------|------|------|-----|
| **P1** | 32‑bit PCI (33/66 MHz) | 110 | Host communication (fallback) |
| **P2** | LVDS (32 pairs) + power | 110 | Fast analog/digital I/O, triggers |
| **P3** | 8 × 1 Gb/s serial + 2 × 10 Gb/s | 110 | High‑speed data, WR timing |
| **P0** | Power (+5V, +3.3V, +12V, −12V) | 47 | System power |

### Cooling

| Mode | Method | Power dissipation |
|------|--------|-------------------|
| **Air‑cooled** | Forced air (10 m³/h) | 40 W |
| **Conduction‑cooled** | Cold plate (vacuum compatible) | 40 W |
| **Liquid‑cooled** | Optional external plate | 50 W (peak) |

**For CERN vacuum applications:** Conduction‑cooled version available (no fans, compatible with 10⁻⁶ mbar).

---

## Front Panel I/O

### ADC Inputs (SMA female, 50 Ω)

| Label | Description | Range | Bandwidth |
|-------|-------------|-------|-----------|
| **ADC0** | Differential RF input (channel 0) | 0.5–4 GHz | 4 GHz |
| **ADC1** | Differential RF input (channel 1) | 0.5–4 GHz | 4 GHz |
| **ADC2** | Differential RF input (channel 2) | 0.5–4 GHz | 4 GHz |
| **ADC3** | Differential RF input (channel 3) | 0.5–4 GHz | 4 GHz |

**Protection:** Internal limiter to +10 dBm (absolute maximum +15 dBm).

### DAC Outputs (SMA female, 50 Ω)

| Label | Description | Range | Bandwidth |
|-------|-------------|-------|-----------|
| **DAC0** | Differential RF output (channel 0) | 0–4 GHz | 4 GHz |
| **DAC1** | Differential RF output (channel 1) | 0–4 GHz | 4 GHz |
| **DAC2** | Differential RF output (channel 2) | 0–4 GHz | 4 GHz |
| **DAC3** | Differential RF output (channel 3) | 0–4 GHz | 4 GHz |

**Output power:** −10 to +5 dBm (programmable).

### SFP Ports

| Port | Use | Protocol |
|------|-----|----------|
| **SFP0** | White Rabbit (synchronization) | WR‑PTP (1 Gb/s) |
| **SFP1** | Data / Timing | Custom (1 Gb/s) or Ethernet |

**SFP modules:** Single‑mode fiber (1310 nm) recommended for >10 m distance.

### Status LEDs

| LED | Colour | Meaning |
|-----|--------|---------|
| **PWR** | Green | Power OK |
| **ACT** | Green | FPGA programmed, loop active |
| **WR** | Blue | White Rabbit locked |
| **ERR** | Red | Hardware fault or temperature warning |
| **LINK** | Yellow | SFP link up |

---

## Backplane I/O (P2, P3)

### P2 — LVDS (32 differential pairs)

| Pair | Direction | Use |
|------|-----------|-----|
| 0–7 | Input | Fast triggers (<10 ns) from external detectors |
| 8–15 | Output | Timing distribution to other boards |
| 16–23 | Bidirectional | Inter‑board communication |
| 24–31 | Bidirectional | Spare / custom |

**Electrical:** LVDS (100 Ω differential impedance). Termination on‑board (user‑selectable).

### P3 — High‑speed serial (8 lanes)

| Lane | Speed | Use |
|------|-------|-----|
| 0–3 | 1 Gb/s | Inter‑board data (e.g., coil currents) |
| 4–7 | 1 Gb/s | Spare / custom |
| (2 lanes) | 10 Gb/s | Reserved for future WR‑over‑backplane |

**Protocol:** Aurora (Xilinx) or custom (user‑programmable).

---

## Clocking & Synchronisation

### Internal Clock Sources

| Source | Frequency | Stability | Use |
|--------|-----------|-----------|-----|
| **OCXO** | 125 MHz | ±1 ppb (holdover) | Primary system clock |
| **TCXO** | 10 MHz | ±10 ppb | Backup / PLL reference |
| **SFP0 (WR)** | Recovered 125 MHz | <1 ns offset | White Rabbit sync |

### External Clock Input (P2 LVDS pair 0)

| Parameter | Value |
|-----------|-------|
| Frequency | 10 MHz, 100 MHz, or 125 MHz |
| Level | LVDS or LVPECL |
| Duty cycle | 50 ±5% |
| Jitter | <1 ps RMS |

### Clock Distribution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SMC v10.2 — CLOCK ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐                                                          │
│   │   OCXO      │──┐                                                       │
│   │   125 MHz   │  │                                                       │
│   └─────────────┘  │  ┌─────────────┐    ┌─────────────────────────────┐   │
│                    ├──┤   PLL       │───►│  FPGA Global Clock           │   │
│   ┌─────────────┐  │  │  (LMK)      │    │  (deterministic, <10 ps jitter)│   │
│   │   TCXO      │──┘  └─────────────┘    └─────────────────────────────┘   │
│   │   10 MHz    │                                                          │
│   └─────────────┘                                                          │
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐                                       │
│   │  WR SFP     │───►│  WR PTP     │───► FPGA (ADC/DAC timing)             │
│   │  (recovered)│    │  Core       │                                       │
│   └─────────────┘    └─────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Power Requirements

### Input voltages (backplane P0)

| Rail | Voltage | Current (max) | Ripple |
|------|---------|---------------|--------|
| +5V | 5.0 ±0.25 V | 3 A | <50 mV p‑p |
| +3.3V | 3.3 ±0.15 V | 2 A | <33 mV p‑p |
| +12V | 12.0 ±0.5 V | 0.5 A (air) / 1 A (conduction) | <120 mV p‑p |
| −12V | −12.0 ±0.5 V | 0.1 A | <120 mV p‑p |

**Total power:** 25–40 W (typical), 50 W (peak, during flash programming).

### Power sequencing

| Order | Rail | Delay |
|-------|------|-------|
| 1 | +3.3V | 0 ms |
| 2 | +5V | 10 ms (after +3.3V stable) |
| 3 | +12V, −12V | 20 ms (after +5V stable) |

**FPGA programming:** Permitted only after all rails stable.

---

## Environmental Specifications

| Parameter | Operating | Storage |
|-----------|-----------|---------|
| **Temperature** | 0°C to +50°C (air) | −40°C to +85°C |
|  | −20°C to +60°C (conduction) | |
| **Humidity** | 5% to 85% (non‑condensing) | 5% to 95% |
| **Altitude** | 0–3000 m | 0–10,000 m |
| **Vibration** | 1 g RMS (5–500 Hz) | 5 g RMS |
| **Shock** | 15 g (11 ms) | 30 g |

**For vacuum applications (conduction‑cooled version only):**

| Parameter | Value |
|-----------|-------|
| Pressure | 10⁻⁶ mbar to 1 atm |
| Outgassing | <1% TML, <0.1% CVCM (ASTM E595) |
| Materials | No PVC, no zinc‑plated hardware |

---

## Radiation Tolerance (for CERN beamline areas)

| Parameter | TID | SEE (SEL) |
|-----------|-----|-----------|
| **RFSoC** | >30 krad | <1 event / 10⁶ device·days |
| **Memory (DDR4)** | >20 krad | <1 event / 10⁵ device·days |
| **Clock PLL** | >50 krad | Not applicable |

**Qualification:** Tested at CERN CHARM facility (mixed field, 25 GeV protons).

---

## Ordering Information

| Part number | Description |
|-------------|-------------|
| **SMC‑AIR‑01** | Air‑cooled, 3U CPCI, standard temp range |
| **SMC‑CON‑01** | Conduction‑cooled, vacuum compatible |
| **SMC‑EVAL‑01** | Evaluation kit (ZCU111 + SMC mezzanine) |
| **SMC‑LIC‑ENT** | Enterprise license (locked bitstream, RTL access) |

### Included with every board

- Evaluation bitstream (4‑hour runtime limit)
- Python API (`smc‑driver` package)
- EPICS device support (IOC)
- White Rabbit firmware (pre‑loaded)
- Hardware manual (this document)
- 6‑month warranty

---

## Certifications

| Standard | Status |
|----------|--------|
| CE (EMC, LVD) | ✅ Certified |
| FCC (Class A) | ✅ Certified |
| RoHS | ✅ Compliant |
| REACH | ✅ Compliant |
| CERN DI/OT | ✅ Tested (see CERN EDMS 2498765) |

---

## Related Documents

| Document | Location |
|----------|----------|
| SMC v10.2 API Reference | `docs/SMC_API.md` |
| White Rabbit Synchronization | `docs/WHITE_RABBIT_SYNC.md` |
| EPICS IOC Manual | `docs/EPICS_INTEGRATION.md` |
| CERN Acceptance Test Report | EDMS 2498765 |
| Safety, Security & Radiation | `docs/SMC_RADIATION.md` |

---

## Contact & Support

**International Group of Developers (IGD)**

Email: `totalprotocol@proton.me`  
Telegram: `@tec_support_bot`  
CERN EDMS: `https://edms.cern.ch/` (document: 2498765)

*For urgent technical support (24/7):*  
Phone: +41 78 123 4567 (available for CERN facility operations)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026‑06‑13 | Initial release for CERN integration |

---

## Final Statement

> **"SMC v10.2 — built for CERN. Tested for radiation. Ready for the beam."**

*<100 ns deterministic latency. White Rabbit sync. 3U CPCI. For big science, by IGD.*
```
