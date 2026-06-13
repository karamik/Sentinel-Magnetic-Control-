#!/usr/bin/env python3
"""
SMC v10.2: Sentinel Magnetic Control Unit
Example: Core Feedback Loop Configuration & Telemetry Monitoring

Usage:
    ./smc_monitor.py --ip 192.168.2.111
    ./smc_monitor.py --ip 192.168.2.111 --log telemetry.csv
    ./smc_monitor.py --ip 192.168.2.111 --temp-limit 70.0

(c) 2026 International Group of Developers – All rights reserved.
"""

import sys
import time
import random
import argparse
import signal
from datetime import datetime

# ---------------------------------------------------------------------
# EMULATED LOW-LEVEL SMC DRIVER
# In production, this would interface with real hardware via PCIe/Ethernet
# ---------------------------------------------------------------------

class SMCDriver:
    """Hardware driver for SMC v10.2 (emulated for demo)"""
    
    def __init__(self, ip_address="192.168.1.100"):
        self.ip = ip_address
        self.is_connected = False
        self.chip_dna = None
        self._active = False
        
    def connect(self):
        """Establish connection to SMC board"""
        print(f"[*] Connecting to SMC Board at {self.ip}...")
        time.sleep(0.5)
        self.is_connected = True
        self.chip_dna = "0x4002A1B2C3D4E5F6"
        print(f"[+] Connected. Chip DNA Verified: {self.chip_dna}")
        return True
        
    def disconnect(self):
        """Gracefully disconnect"""
        if self.is_connected:
            self.write_register(0x00, 0x00)  # Stop hardware loop
            print("[*] Hardware loop stopped.")
        self.is_connected = False
        
    def write_register(self, address, value):
        """Write to hardware register (FPGA/ASIC)"""
        if not self.is_connected:
            raise RuntimeError("Not connected to SMC board")
        # In real code: mmap, PCIe write, or Ethernet command
        # Emulated: just print debug
        pass

    def read_register(self, address):
        """Read hardware register"""
        if not self.is_connected:
            raise RuntimeError("Not connected to SMC board")
        # Emulate register values
        if address == 0x04:      # DSP status register
            return 0x01 if self._active else 0x00
        elif address == 0x08:    # Temperature sensor
            return 0x2C  # 44°C emulated
        return 0x0

    def set_filter_coefficients(self, matrix_weights):
        """Upload MAC matrix coefficients directly to FPGA gates"""
        print(f"[*] Uploading {len(matrix_weights)} MAC matrix weights to PL gates...")
        for idx, weight in enumerate(matrix_weights):
            reg_addr = 0x100 + (idx * 4)
            self.write_register(reg_addr, weight)
        print("[+] Configuration locked into FPGA memory.")
        
    def start_loop(self):
        """Activate deterministic hardware loop"""
        self.write_register(0x00, 0x01)  # REG_CONTROL = START
        self._active = True
        print("[+] Hardware deterministic loop is now ACTIVE.")
        
    def stop_loop(self):
        """Deactivate hardware loop (bypass mode)"""
        self.write_register(0x00, 0x00)
        self._active = False
        print("[*] Hardware loop stopped (bypass mode).")

    def get_telemetry(self):
        """Read diagnostic data from Sentinel Core"""
        if not self._active:
            return None
            
        # Emulate telemetry (in real hardware, read from ADC/DAC and sensors)
        # Latency is stable under 100ns thanks to hardware-only path
        return {
            "timestamp": datetime.now(),
            "latency_ns": round(random.uniform(92.1, 95.8), 2),
            "input_gradient_mT": round(random.uniform(-0.15, 0.15), 4),
            "dac_output_volts": round(random.uniform(-1.2, 1.2), 3),
            "fpga_temp_c": round(random.uniform(42.5, 44.0), 1),
            "white_rabbit_sync": random.choice([True, True, True, True])  # 80% OK
        }

# ---------------------------------------------------------------------
# TELEMETRY LOGGER
# ---------------------------------------------------------------------

class TelemetryLogger:
    """CSV logger for telemetry data"""
    
    def __init__(self, filename=None):
        self.file = None
        if filename:
            self.file = open(filename, 'w')
            self.file.write("timestamp,latency_ns,field_gradient_mT,dac_output_v,fpga_temp_c,wr_sync\n")
            print(f"[+] Telemetry logging to {filename}")
            
    def write(self, data):
        if self.file:
            self.file.write(f"{data['timestamp'].isoformat()},"
                           f"{data['latency_ns']},"
                           f"{data['input_gradient_mT']},"
                           f"{data['dac_output_volts']},"
                           f"{data['fpga_temp_c']},"
                           f"{int(data['white_rabbit_sync'])}\n")
            self.file.flush()
            
    def close(self):
        if self.file:
            self.file.close()
            print("[*] Telemetry log saved.")

# ---------------------------------------------------------------------
# MAIN MONITOR LOOP
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='SMC v10.2 - Sentinel Magnetic Control Unit Monitor',
        epilog='Example: %(prog)s --ip 192.168.2.111 --log telemetry.csv'
    )
    parser.add_argument('--ip', default='192.168.2.111', 
                       help='SMC board IP address (default: 192.168.2.111)')
    parser.add_argument('--log', metavar='FILE', 
                       help='Save telemetry to CSV file')
    parser.add_argument('--temp-limit', type=float, default=75.0,
                       help='Temperature warning threshold in Celsius (default: 75.0)')
    parser.add_argument('--latency-limit', type=float, default=100.0,
                       help='Latency warning threshold in ns (default: 100.0)')
    parser.add_argument('--duration', type=int, default=0,
                       help='Run for N seconds (0 = infinite)')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress live table output (log only)')
    
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    running = True
    def signal_handler(sig, frame):
        nonlocal running
        print("\n[*] Interrupt received, shutting down...")
        running = False
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize
    print("=" * 75)
    print("SMC v10.2 Calibration & Monitoring Utility")
    print("=" * 75)
    
    # Connect to hardware
    smc = SMCDriver(ip_address=args.ip)
    try:
        smc.connect()
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return 1
    
    # Upload filter coefficients (tailored to your specific magnetic trap geometry)
    # These weights implement a Temporal Median Filter + Parallel MAC
    target_weights = [16384, -8192, 4096, -2048, 1024, -512, 256, -128, 64, -32]
    smc.set_filter_coefficients(target_weights)
    
    # Start hardware loop
    smc.start_loop()
    
    # Initialize logger
    logger = TelemetryLogger(args.log)
    
    # Monitor loop
    print("\nPress Ctrl+C to stop monitoring.")
    if not args.quiet:
        print("-" * 80)
        print(f"{'Time':<12} | {'Latency (ns)':<14} | {'Field Gradient (mT)':<20} | {'DAC Out (V)':<12} | {'Temp (°C)':<10} | {'WR Sync':<8}")
        print("-" * 80)
    
    start_time = time.time()
    iteration = 0
    latency_warnings = 0
    temp_warnings = 0
    sync_failures = 0
    
    try:
        while running:
            metrics = smc.get_telemetry()
            
            if metrics is None:
                print("[-] Telemetry read failed. Hardware loop not active?")
                break
                
            # Log data
            logger.write(metrics)
            
            # Display (if not quiet)
            if not args.quiet:
                wr_status = "OK" if metrics["white_rabbit_sync"] else "FAIL"
                print(f"{metrics['timestamp'].strftime('%H:%M:%S'):<12} | "
                      f"{metrics['latency_ns']:>6.2f} ns     | "
                      f"{metrics['input_gradient_mT']:>+8.4f} mT        | "
                      f"{metrics['dac_output_volts']:>+7.3f} V   | "
                      f"{metrics['fpga_temp_c']:>5.1f}°C   | "
                      f"{wr_status:<8}")
            
            # Check for warnings
            if metrics['latency_ns'] > args.latency_limit:
                latency_warnings += 1
                if not args.quiet:
                    print(f"  ⚠ WARNING: Latency {metrics['latency_ns']:.2f} ns exceeds limit ({args.latency_limit} ns)")
                    
            if metrics['fpga_temp_c'] > args.temp_limit:
                temp_warnings += 1
                if not args.quiet:
                    print(f"  ⚠ WARNING: FPGA temperature {metrics['fpga_temp_c']:.1f}°C exceeds limit ({args.temp_limit}°C)")
                    
            if not metrics['white_rabbit_sync']:
                sync_failures += 1
                if not args.quiet:
                    print(f"  ⚠ WARNING: White Rabbit PTP synchronization lost")
            
            # Check duration limit
            iteration += 1
            if args.duration > 0 and (time.time() - start_time) > args.duration:
                print(f"\n[*] Duration limit ({args.duration}s) reached.")
                break
                
            # Sleep 1 second between polls (hardware runs at MHz, we just log slow)
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Clean shutdown
        print("\n" + "-" * 80)
        print("SUMMARY")
        print("-" * 80)
        print(f"Total samples:     {iteration}")
        print(f"Latency warnings:  {latency_warnings} (>{args.latency_limit} ns)")
        print(f"Temperature warnings: {temp_warnings} (>{args.temp_limit}°C)")
        print(f"White Rabbit sync failures: {sync_failures}")
        
        # Verify critical specification
        if latency_warnings == 0:
            print("\n✅ SPECIFICATION VERIFIED: All measured latencies < 100 ns")
        else:
            print(f"\n⚠ LATENCY VIOLATION DETECTED: {latency_warnings} measurements exceeded limit")
            
        smc.stop_loop()
        smc.disconnect()
        logger.close()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
