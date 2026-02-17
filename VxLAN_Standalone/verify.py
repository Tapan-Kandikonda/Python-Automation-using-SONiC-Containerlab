# Basic ping check
import subprocess, time

LAB = "clab-vxlan-fabric"
time.sleep(10)

def run(cmd):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=False)

print("\n📡 Underlay check (leaf1 → leaf2 loopback)")
run(["docker","exec",f"{LAB}-leaf1","ping","-c","3","2.2.2.2"])

print("\n📡 Overlay check (server1 → server2)")
run(["docker","exec",f"{LAB}-server1","ping","-c","3","192.168.100.20"])
