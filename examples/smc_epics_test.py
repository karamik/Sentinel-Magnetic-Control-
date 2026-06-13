#!/usr/bin/env python3
"""
EPICS Test Client for SMC v10.2
Requires: pip install epics (pyepics) or caproto
Run this script on a machine that can access the SMC IOC (e.g., control room host).

Usage:
    ./smc_epics_test.py --host 192.168.2.111
    ./smc_epics_test.py --prefix CERN:ALPHA:TRAP1:SMC01
"""

import time
import sys
import argparse
import logging

try:
    from epics import PV, ca
except ImportError:
    print("pyepics not installed. Run: pip install epics")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SMCEpicsClient:
    """EPICS client for SMC v10.2"""

    def __init__(self, prefix, timeout=5.0):
        self.prefix = prefix
        self.timeout = timeout
        self.pvs = {}
        self._connect_pvs()

    def _connect_pvs(self):
        """Create PV objects for all relevant process variables"""
        pv_list = [
            "LOOP_CMD", "LOOP_STATUS",
            "LATENCY_LOG", "FIELD_GRAD", "FPGA_TEMP",
            "WR_LOCKED", "WR_OFFSET",
            "COEFFS_SET", "COEFFS_UPLOAD",
            "SAVE_CONFIG", "ALARM_SUMMARY", "LAST_ALARM"
        ]
        for name in pv_list:
            full_name = f"{self.prefix}:{name}"
            self.pvs[name] = PV(full_name, auto_monitor=False, timeout=self.timeout)
            logger.debug(f"Connected PV: {full_name}")

    def start_loop(self):
        """Activate hardware feedback loop"""
        logger.info("Starting hardware loop...")
        self.pvs["LOOP_CMD"].put(1, wait=True)
        time.sleep(0.1)
        status = self.pvs["LOOP_STATUS"].get()
        logger.info(f"Loop status: {status}")

    def stop_loop(self):
        """Deactivate hardware loop (bypass)"""
        logger.info("Stopping hardware loop...")
        self.pvs["LOOP_CMD"].put(0, wait=True)

    def upload_coefficients(self, coeffs):
        """Write array of coefficients and trigger upload"""
        if len(coeffs) > 32:
            logger.warning("Max 32 coefficients, truncating.")
            coeffs = coeffs[:32]
        logger.info(f"Uploading coefficients: {coeffs}")
        self.pvs["COEFFS_SET"].put(coeffs, wait=True)
        self.pvs["COEFFS_UPLOAD"].put(1, wait=True)

    def get_telemetry(self):
        """Return dictionary with current telemetry values"""
        telemetry = {
            "latency_ns": self.pvs["LATENCY_LOG"].get(),
            "field_gradient_mT": self.pvs["FIELD_GRAD"].get(),
            "fpga_temp_c": self.pvs["FPGA_TEMP"].get(),
            "wr_locked": self.pvs["WR_LOCKED"].get(),
            "wr_offset_ns": self.pvs["WR_OFFSET"].get(),
            "alarm_summary": self.pvs["ALARM_SUMMARY"].get(),
        }
        return telemetry

    def monitor(self, duration=60, interval=1):
        """Monitor telemetry and print to console"""
        start = time.time()
        logger.info(f"Monitoring for {duration} seconds...")
        while time.time() - start < duration:
            data = self.get_telemetry()
            print(f"\rLatency: {data['latency_ns']:.2f} ns | "
                  f"Gradient: {data['field_gradient_mT']:.3f} mT | "
                  f"Temp: {data['fpga_temp_c']:.1f}°C | "
                  f"WR lock: {data['wr_locked']} | "
                  f"Alarm: {data['alarm_summary']}", end="")
            time.sleep(interval)
        print()

    def simulate_alarm(self):
        """Force a major alarm by writing unrealistic value (for testing only)"""
        logger.warning("Simulating alarm: Writing 200 ns latency PV (if writable)")
        # Not all alarm PVs may be writable; this is a demonstration
        self.pvs["LATENCY_LOG"].put(150.0, wait=True)
        time.sleep(1)
        logger.info(f"Alarm summary after injection: {self.pvs['ALARM_SUMMARY'].get()}")


def main():
    parser = argparse.ArgumentParser(description="SMC v10.2 EPICS Test Client")
    parser.add_argument("--prefix", default="CERN:ALPHA:TRAP1:SMC01", help="EPICS PV prefix")
    parser.add_argument("--host", help="Optional host:port for Channel Access (default uses environment)")
    parser.add_argument("--monitor", action="store_true", help="Run telemetry monitor")
    parser.add_argument("--duration", type=int, default=30, help="Monitor duration in seconds")
    parser.add_argument("--test-coeffs", action="store_true", help="Upload test coefficients")
    parser.add_argument("--simulate-alarm", action="store_true", help="Simulate an alarm condition")
    args = parser.parse_args()

    if args.host:
        # Optional: Set EPICS_CA_ADDR_LIST environment variable
        import os
        os.environ["EPICS_CA_ADDR_LIST"] = args.host

    client = SMCEpicsClient(prefix=args.prefix)

    # Basic connectivity test
    try:
        client.pvs["LOOP_STATUS"].get(timeout=2.0)
    except Exception as e:
        logger.error(f"Failed to connect to IOC at prefix {args.prefix}: {e}")
        sys.exit(1)

    logger.info("Connected to SMC EPICS IOC")

    if args.test_coeffs:
        example_coeffs = [16384, -8192, 4096, -2048, 1024]
        client.upload_coefficients(example_coeffs)

    if args.monitor:
        client.start_loop()
        client.monitor(duration=args.duration)
        client.stop_loop()

    if args.simulate_alarm:
        client.simulate_alarm()

    logger.info("Test completed.")


if __name__ == "__main__":
    main()
