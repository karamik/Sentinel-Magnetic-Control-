
**© 2026 International Group of Developers – All rights reserved.** See the LICENSE file for terms.
# SMC v10.2: Sentinel Magnetic Control Unit
### Ultra-Low Latency Deterministic Feedback for Big Science
## [NEW] Evaluation Bitstream Available
**Don't take our word for it—verify the 100ns latency on your own hardware.** We have released a pre-compiled **Evaluation Bitstream** for the **AMD/Xilinx ZCU111 RFSoC**.
Go to RELEASES to download the .bit file and testing instructions.
## Overview
The **SMC v10.2** is a hardware‑accelerated control unit designed for ultra‑precise magnetic field stabilisation in high-energy physics and quantum experiments. By offloading the entire feedback loop (from ADC to DAC) into hardened FPGA gates, we eliminate the jitter and latency overhead of traditional CPU-based systems.
**The goal:** Real-time suppression of magnetic field gradients with a deterministic round-trip latency of **< 100 ns**.
## Key Features
| Feature | Specification |
|---|---|
| **Core Architecture** | AMD/Xilinx Zynq UltraScale+ RFSoC |
| **Deterministic Latency** | **< 100 ns** (Pin-to-Pin, including DSP) |
| **Processing Power** | Parallel MAC Matrix + Temporal Median Filtering |
| **Clock Sync** | White Rabbit PTP (Sub-nanosecond accuracy) |
| **Form Factor** | Native DI/OT (3U CPCI‑S.0) or Custom RFSoC Carrier |
| **Reliability** | Radiation-hardened design principles (TID > 30 krad) |
| **Integration** | EPICS / Linux RT-Driver / Python API |
## Architecture: The "Precision Filter" Logic
The SMC v10.2 bypasses the Processing System (PS) for all time-critical tasks. Data flows directly from the RF-ADCs to the Programmable Logic (PL) and out through the RF-DACs.
```text
[PHYSICAL WORLD] -> [RF-ADC] -> [SMC CORE: MAC + FILTER] -> [RF-DAC] -> [CORRECTION]
       ^                               |                                     |
       └------------------- < 100ns Deterministic Loop -----------------------┘

```
## Evaluation Model (Test Drive)
The provided evaluation bitstream allows your engineering team to validate performance without an NDA.
### How to Test:
 1. **Hardware:** Xilinx ZCU111 Evaluation Kit.
 2. **Setup:** Connect a Function Generator to ADC Input 0 and an Oscilloscope to DAC Output 0.
 3. **Action:** Flash the .bit file using the provided flash_me.tcl script.
 4. **Verification:** Observe the real-time filtered output. Measure the delta-t on the scope.
> **Note:** The evaluation model is hard-coded with a **4-hour operational window**. After 4 hours, the DSP core enters bypass mode. A board reset is required to restart the evaluation.
> 
## Licensing & Enterprise Version
For production-grade deployment, we provide the **SMC Enterprise License**, which includes:
 * **Locked Bitstreams:** Device-specific IP cores (locked to chip DNA).
 * **Custom DSP:** Tailored MAC matrix weights and filter coefficients for your specific trap geometry.
 * **Support:** Integration with CERN DI/OT crates and EPICS infrastructure.
 * **RTL Access:** Available only for strategic partners under specialized licensing.
## Contact & Inquiries
**International Group of Developers** For full technical specifications, performance whitepapers, and licensing costs:
📧 **Email:** karam1975@proton.me
💬 **Telegram:** @tec_support_bot
*Geneva | Amsterdam | Dubai*
---
