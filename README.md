**© 2026 International Group of Developers – All rights reserved.** See the LICENSE file for terms.

# SMC v10.2: Sentinel Magnetic Control Unit

### Ultra-Low Latency Deterministic Feedback for Big Science

## [NEW] Evaluation Bitstream Available

**Don't take our word for it—verify the 100ns latency on your own hardware.**  
We have released a pre-compiled **Evaluation Bitstream** for the **AMD/Xilinx ZCU111 RFSoC**.  
Go to RELEASES to download the .bit file and testing instructions.

---

## Overview

The **SMC v10.2** is a hardware‑accelerated control unit designed for ultra‑precise magnetic field stabilisation in high-energy physics and quantum experiments. By offloading the entire feedback loop (from ADC to DAC) into hardened FPGA gates, we eliminate the jitter and latency overhead of traditional CPU-based systems.

**The goal:** Real-time suppression of magnetic field gradients with a deterministic round-trip latency of **< 100 ns**.

---

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

---

## Architecture: The "Precision Filter" Logic

The SMC v10.2 bypasses the Processing System (PS) for all time-critical tasks. Data flows directly from the RF-ADCs to the Programmable Logic (PL) and out through the RF-DACs.

```text
[PHYSICAL WORLD] -> [RF-ADC] -> [SMC CORE: MAC + FILTER] -> [RF-DAC] -> [CORRECTION]
       ^                               |                                     |
       └------------------- < 100ns Deterministic Loop -----------------------┘
```

---

## Theoretical Foundations & Applications

The SMC v10.2 is not just a generic control unit — it is built to meet the extreme demands of next‑generation experiments in condensed matter physics and high‑energy particle physics. We have derived two comprehensive theoretical frameworks that directly inform the performance requirements for magnetic field stabilisation. These frameworks are available in separate open‑source repositories.

### 1. Nickelate Superconductivity & High‑Field Magnets

**Full Theory Repository:**  
[https://github.com/karamik/nickelate-s--theory](https://github.com/karamik/nickelate-s--theory/tree/main)

We have developed a complete microscopic theory of bilayer nickelate superconductors (e.g., La₃Ni₂O₇ under pressure). Key predictions relevant to SMC:

- **Critical temperature:** \(T_c = 26.5\) K at optimal pressure (~14 GPa).
- **Upper critical field:** \(H_{c2}(0) = 95\) T — nearly double the Pauli paramagnetic limit.
- **Field sensitivity:** Superconductivity collapses within a narrow pressure window, requiring extremely stable magnetic field control (drift < \(10^{-5}\) over time).

**Implication for SMC:** To operate magnets based on these materials, the control system must provide deterministic, jitter‑free feedback with sub‑100 ns latency to suppress transient field gradients that could destroy the superconducting phase. The SMC v10.2 directly addresses this need.

### 2. Composite Higgs / Preon Theory & Collider Searches

**Full Theory Repository:**  
[https://github.com/karamik/composite-higgs-hypercolor](https://github.com/karamik/composite-higgs-hypercolor/tree/main)

We have constructed a minimal SU(2)‑hypercolor model where the Higgs boson is a bound state of preons. This predicts new resonances (hyperpions) accessible at HL‑LHC:

- **Hyperpion mass:** \(m_\Pi = 1.2\) TeV, with a broad width \(\Gamma \approx 300\) GeV.
- **Production cross section:** \(\sigma(pp \to \Pi\Pi \to WWWW) \approx 0.5\) fb (at 14 TeV).
- **Search strategy:** Requires high‑luminosity data and precise magnet stability to maintain beam focus and detector acceptance.

**Implication for SMC:** The search for such rare processes demands ultra‑stable magnetic fields in the collider's final‑focus quadrupoles. Any fluctuation on the nanosecond scale can shift the beam spot and distort the reconstructed invariant mass. The SMC's deterministic latency ensures that correction signals arrive before the beam position deviates by more than a micron.

### Why This Matters for SMC Users

By providing these theoretical foundations alongside the hardware, we empower physicists to:
- **Justify** the need for sub‑100 ns feedback in funding proposals.
- **Simulate** the effect of field stability on their specific experiments using our analytical models.
- **Tune** the SMC parameters (DSP weights, filter coefficients) to match the magnetic susceptibility of novel superconductors.

We invite you to explore the full theories in the respective GitHub repositories linked above. They are open‑source and fully reproducible.

---

## Evaluation Model (Test Drive)

The provided evaluation bitstream allows your engineering team to validate performance without an NDA.

### How to Test:

1. **Hardware:** Xilinx ZCU111 Evaluation Kit.
2. **Setup:** Connect a Function Generator to ADC Input 0 and an Oscilloscope to DAC Output 0.
3. **Action:** Flash the .bit file using the provided script:  
   `scripts/flash_me.tcl` (run it from the Vivado Tcl Shell).
4. **Verification:** Observe the real-time filtered output. Measure the delta-t on the scope.

> **Note:** The evaluation model is hard-coded with a **4-hour operational window**. After 4 hours, the DSP core enters bypass mode. A board reset is required to restart the evaluation.

---

## Licensing & Enterprise Version

For production-grade deployment, we provide the **SMC Enterprise License**, which includes:

- **Locked Bitstreams:** Device-specific IP cores (locked to chip DNA).
- **Custom DSP:** Tailored MAC matrix weights and filter coefficients for your specific trap geometry.
- **Support:** Integration with CERN DI/OT crates and EPICS infrastructure.
- **RTL Access:** Available only for strategic partners under specialized licensing.

---

## Contact & Inquiries

**International Group of Developers**  
For full technical specifications, performance whitepapers, and licensing costs:

📧 **Email:** totalprotocol@proton.me  
💬 **Telegram:** @tec_support_bot  

*Geneva | Amsterdam | Dubai*
```
