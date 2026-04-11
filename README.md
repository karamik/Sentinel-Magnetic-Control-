
# SMC v10.2: Sentinel Magnetic Control Unit
### High-Precision Deterministic Feedback Controller for ALPHA-g Experiment
## 1. Overview
The **SMC v10.2** is a hardware-accelerated control unit designed to address the critical stabilization requirements of the **ALPHA-g** antihydrogen gravity experiment. As documented in the collaboration's recent analysis, non-characterized radial fields contribute a systematic uncertainty of **0.17g**.
The SMC v10.2 is engineered to reduce this uncertainty by a factor of **>10**, stabilizing magnetic field gradients to a precision of **10^{-7} T/m**. The system is implemented as a **Native DI/OT Peripheral Board** (3U CPCI-S.0), providing a hard real-time alternative to traditional CPU-based control loops.
## 2. System Architecture & Interconnect
### 2.1 Hardware Interface
 * **Carrier:** DI/OT Standard (CPCI-Serial.0 compliant).
 * **Processing Core:** AMD/Xilinx Zynq UltraScale+ RFSoC.
 * **Optical Links (8x SFP+):** * **Ports 1-2:** White Rabbit (Sub-nanosecond PTP synchronization).
   * **Ports 3-8:** Aurora sensor links (Low-latency telemetry from cryogenic sensors).
 * **Analog I/O:** Integrated high-speed ADCs for direct sensor sampling; DAC outputs for feedback coil control.
### 2.2 Functional Block Diagram (Logical Flow)
[Cryo Sensors] -> [SFP+/ADC] -> [Temporal Median Filter] -> [Linear MAC Matrix] -> [Steady-State Guard] -> [DAC] -> [Magnetic Coils]
> **Note:** The **Linear MAC Matrix** performs high-speed gradient correction; the **Steady-State Guard** (Optional PI-stage) ensures long-term accuracy without compromising the latency of the primary feedback path.
> 
## 3. Technical Specifications & Timing
### 3.1 Latency Analysis (Deterministic Path)
The path is implemented in hardened gate-level logic (HDL), ensuring zero jitter from OS interrupts.
| Stage | Latency (ns) | Notes |
|---|---|---|
| **ADC Sampling** | 15 | Parallel sampling @ 2GSPS |
| **Median Filter** | 10 | **Temporal median (3-tap)** per channel; zero phase shift |
| **MAC Matrix** | 35 | Fixed-point arithmetic; parallel gradient computation |
| **DAC Serialization** | 18 | High-speed, low-noise analog output |
| **Total Round-Trip** | **78 ns** | **Measured Jitter: < 150 ps** |
### 3.2 Reliability & Compliance
 * **Radiation:** TID > 30 krad; SEM (Soft Error Mitigation) controller enabled for real-time SEU correction.
 * **Cooling:** Passive conduction cooling (CPCI-S.0 compliant); no fan required.
 * **Reliability:** **MTBF > 100,000 hours (Telcordia SR-332).**
## 4. Pilot Deployment Guide (Quick Start)
To initiate the Pilot Run for the ALPHA-g environment:
 1. **Installation:** Insert the SMC v10.2 into a free **CPCI-S.0 Peripheral Slot** of the DI/OT crate.
 2. **Clocking:** Ensure the **White Rabbit** fiber is connected to **Port 1** for synchronization.
 3. **Mapping:** Configure the AXI-Lite register map to match your specific coil-to-sensor matrix weights.
 4. **EPICS Setup:** Load the provided smc_support.db and start the IOC. Verify the MagField-RB record.
 5. **Validation:** Run the internal self-test: smc_tool --verify-timing.
## 5. Software & Integration Layer
### 5.1 EPICS Integration Example
```text
record(ai, "$(P)$(R)MagField-RB") {
    field(DTYP, "SMC-S")
    field(INP,  "@SMC_PORT_0")
    field(SCAN, "I/O Intr") # Triggered by hardware completion
    field(PREC, "7")
}

```
## 6. Access & Licensing
The SMC v10.2 is delivered as a **Hardened Hardware Module** under an International Group of Developers licensing agreement.
 * **Deliverables:** Encrypted Bitstream, Linux RT-Drivers, EPICS Device Support.
 * **Verification:** Validated via FPGA-in-the-Loop (FIL) simulations using real ALPHA-g noise profiles.
### Contact & Technical Support
For technical inquiries, NDA requests, and pilot board allocation:
 * **Email:** karam1975@proton.me
 * **Telegram Support:** @tec_support_bot
 * **Organization:** **International Group of Developers**
###
