
# EPICS Device Support & IOC Integration Manual for SMC v10.2

## 1. Architectural Overview

The SMC v10.2 features native integration with the **Experimental Physics and Industrial Control System (EPICS)** framework. While the critical feedback loop runs entirely inside the FPGA fabric (<100 ns) to ensure deterministic physical boundaries, the control, configuration, and slow-telemetry monitoring layers are exposed to the EPICS network via a specialized Input/Output Controller (IOC).


```
[ EPICS OPI / Control Room ] (CSS / Phoebus)
▲
│ Channel Access (CA) / pva
▼
[ SMC v10.2 EPICS IOC ] (Running on RT-Linux / Host)
▲
│ Python-Binding / low-level driver interface
▼
[ SMC v10.2 Hardware Core ] (AMD/Xilinx RFSoC PL Gates)
└─ <100ns Deterministic Analog Loop (ADC -> MAC -> DAC)
```

The SMC IOC instantiates Process Variables (PVs) that allow control rooms to update matrix coefficients, arm the White Rabbit core, and poll telemetry without introducing jitter to the hardware execution layer.

---

## 2. Process Variable (PV) Registry

All SMC PVs are grouped under the device prefix `$(P):$(R):`, where `$(P)` defines the accelerator sector/trap instance and `$(R)` defines the SMC module ID.

### Control and Configuration PVs

| PV Name | EPICS Type | DTYP | Description |
| :--- | :--- | :--- | :--- |
| `$(P):$(R):LOOP_CMD` | `bo` | Asyn / Stream | Activates (`1`) or Bypasses (`0`) the hardware feedback loop. |
| `$(P):$(R):COEFFS_SET` | `waveform` | Asyn / Stream | Array of 16-bit signed integers for the MAC filter matrix. |
| `$(P):$(R):WR_MODE_CMD`| `mbbo` | Asyn / Stream | Sets White Rabbit mode: `0` (None), `1` (Master), `2` (Slave). |
| `$(P):$(R):SAVE_CONFIG`| `bo` | Asyn / Stream | Triggers atomic flash write of current parameters to EEPROM. |

### Monitoring and Telemetry PVs (1 Hz Standard Scan)

| PV Name | EPICS Type | SCAN | Alarm Limits (HIGH/HIHI) | Description |
| :--- | :--- | :--- | :--- | :--- |
| `$(P):$(R):LATENCY_LOG` | `ai` | `1 second` | 100 ns / 120 ns | Current hardware round-trip time. |
| `$(P):$(R):FIELD_GRAD`  | `ai` | `1 second` | Variable | Measured magnetic gradient (mT). |
| `$(P):$(R):FPGA_TEMP`   | `ai` | `1 second` | 65.0°C / 75.0°C | On-die RFSoC temperature. |
| `$(P):$(R):WR_LOCKED`   | `bi` | `I/O Intr` | Minor on `0` | White Rabbit phase lock validation flag. |
| `$(P):$(R):WR_OFFSET`   | `ai` | `1 second` | 1.0 ns / 5.0 ns | Grandmaster time offset (ns). |

---

## 3. Database Record Definition (`smc_magnetic.db`)

Below is the standard EPICS database configuration template deployed on the server side to interface with the `smc-driver`.

```epics
# Control Loop State
record(bo, "$(P):$(R):LOOP_CMD") {
    field(DESC, "SMC Hardware Loop Switch")
    field(ZNAM, "BYPASS")
    field(ONAM, "ACTIVE")
    field(FLNK, "$(P):$(R):LOOP_STATUS")
}

# Real-Time Latency Monitoring
record(ai, "$(P):$(R):LATENCY_LOG") {
    field(DESC, "SMC Hard Loop Latency")
    field(SCAN, "1 second")
    field(EGU,  "ns")
    field(HOPR, "200")
    field(LOPR, "0")
    field(HIGH, "100")
    field(HIHI, "120")
    field(HHSV, "MAJOR")
    field(HSV,  "MINOR")
}

# White Rabbit Sync Status
record(bi, "$(P):$(R):WR_LOCKED") {
    field(DESC, "White Rabbit Phase Lock status")
    field(SCAN, "I/O Intr")
    field(ZNAM, "UNLOCKED")
    field(ONAM, "LOCKED")
    field(OSV,  "MAJOR")
}

```
## 4. IOC Runtime Initialization Script (st.cmd)
To launch the containerized or bare-metal local operational console for the SMC v10.2 board, the initialization script loads the compiled database and establishes the connection driver path:
```bash
#!/usr/bin/env iocsh

# Environment Setup
epicsEnvSet("IOC", "iocSMC")
epicsEnvSet("TOP", "/epics/apps/smc-ioc")
epicsEnvSet("P", "CERN:ALPHA:TRAP1")
epicsEnvSet("R", "SMC01")
epicsEnvSet("SMC_IP", "192.168.2.111")

# Register support structures
dbLoadDatabase("$(TOP)/dbd/smcCore.dbd")
smcCore_registerRecordDeviceDriver(pdbbase)

# Initialize SMCDriver via Ethernet port (Asyn IP Port driver architecture)
# smcConfigurePort(portName, ipAddress)
smcConfigurePort("SMC_NET_PORT", "$(SMC_IP)")

# Load database instances
dbLoadRecords("$(TOP)/db/smc_magnetic.db", "P=$(P),R=$(R),PORT=SMC_NET_PORT")

# Execute IOC Startup Sequence
iocInit()

# Confirm deployment state
print("=====================================================")
print(" SMC v10.2 EPICS IOC successfully bound to active network")
print(" System Identity: $(P):$(R)")
print("=====================================================")

```
## 5. Alarm Processing and Safe State Recovery
The database configuration utilizes standard EPICS severity actions to enforce safe-state transition logic when hardware boundaries are breached:
 1. **Phase Drift Interruption:** If $(P):$(R):WR_LOCKED transitions to UNLOCKED (Value 0), the OSV field raises a MAJOR alarm state instantly.
 2. **Automated Interlock:** The EPICS alarm handler triggers an automated link event to write 0 to $(P):$(R):LOOP_CMD, dropping the FPGA hardware loop out of action within 1 ms of network failure detection to prevent unaligned magnetic gradient injection into the vacuum vessel.
```


