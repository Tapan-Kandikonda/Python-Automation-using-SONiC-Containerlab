# VXLAN_enable_daemons.py
import subprocess

ROUTERS = ["leaf1", "leaf2", "spine"]
LAB = "clab-vxlan-fabric"
DAEMONS = ["zebra", "ospfd"]

def run(cmd):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=True)

for r in ROUTERS:
    c = f"{LAB}-{r}"
    for d in DAEMONS:
        run(["docker","exec",c,"sed","-i",f"s/^{d}=.*/{d}=yes/","/etc/frr/daemons"])
    run(["docker","exec",c,"service","frr","restart"])

print("✅ OSPF daemons enabled")
