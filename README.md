**© 2026 International Group of Developers – All rights reserved.**  
See the [LICENSE](./LICENSE) file for terms.
# SMC v10.2: Sentinel Magnetic Control Unit

## Notice – Proprietary & Confidential

**© 2026 International Group of Developers. All rights reserved.**  
This document provides a high-level overview of a proprietary hardware architecture.  
No license is granted to implement, copy, or distribute the described technology without a written agreement.  
Full technical specifications, performance data, and source code are available **only under a signed Non-Disclosure Agreement (NDA)**.  
For partnership inquiries: **karam1975@proton.me**

---

## Overview

The **SMC v10.2** is a hardware‑accelerated control unit designed for ultra‑precise magnetic field stabilisation in advanced Penning‑Ioffe trap experiments (e.g., antihydrogen gravity measurements).  

The system addresses the challenge of real‑time suppression of magnetic field gradients and non‑characterised radial fields – a known limiting factor in achieving sub‑part‑per‑million measurement accuracy.  

The SMC is implemented as a **Native DI/OT Peripheral Board** (3U CPCI‑S.0), offloading all time‑critical feedback from CPU/OS to deterministic FPGA logic.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Form Factor** | Native DI/OT (3U CPCI‑S.0) |
| **Processing Core** | AMD/Xilinx Zynq UltraScale+ RFSoC |
| **Optical Links** | 8x SFP+ (White Rabbit + Aurora sensor links) |
| **Feedback Latency** | < 100 ns, deterministic, jitter‑free |
| **Processing Pipeline** | Temporal median filter + linear MAC matrix (fixed‑point) |
| **Synchronisation** | White Rabbit PTP (sub‑ns) / Local Genlock |
| **Radiation Tolerance** | TID > 30 krad, SEM controller enabled |
| **Cooling** | Passive conduction (no fans) |
| **Control System** | EPICS native support, Linux RT‑driver |
| **Licensing** | Encrypted bitstream, closed‑source IP |

---

## Architecture (Simplified)

```
[Cryo Sensors] → [SFP+/ADC] → [Median Filter] → [MAC Matrix] → [DAC] → [Correction Coils]
```

- **Temporal Median Filter** (3‑tap, per channel) – rejects impulse noise without phase shift.
- **Linear MAC Matrix** – pre‑computed weights for real‑time field gradient reconstruction.
- **Steady‑State Guard** (optional) – maintains long‑term accuracy.

All stages are implemented in hardened gate‑level logic. No OS, no interrupts.

---

## Integration Example (EPICS)

```epics
record(ai, "$(P)$(R)MagField-RB") {
    field(DTYP, "SMC-S")
    field(INP,  "@SMC_PORT_0")
    field(SCAN, "I/O Intr")
    field(PREC, "7")
}
```

Full device support, register map, and calibration tools are provided under license.

---

## Pilot Deployment (Conceptual)

1. Insert the board into a free CPCI‑S.0 slot of a DI/OT crate.
2. Connect White Rabbit fibre (Port 1) for synchronisation.
3. Load the encrypted bitstream via PCIe.
4. Configure coil‑to‑sensor matrix weights via AXI‑Lite.
5. Start EPICS IOC and verify feedback.

---

## Licensing & Delivery

The SMC v10.2 is delivered as a **hardened hardware module**:

- Encrypted bitstream (FPGA)
- Linux RT‑driver with DMA
- EPICS device support
- Integration documentation

**Source code / RTL is not disclosed.**  
All technical data is shared only under NDA.

---

## Contact

**International Group of Developers**  
Email: `karam1975@proton.me`  
Telegram: `@tec_support_bot`

*Geneva | Amsterdam | DUBAI |
---
