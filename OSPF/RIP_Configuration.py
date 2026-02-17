import subprocess
import time
from R5_Configuration import ROUTERS,run_show
LAB_PREFIX = "clab-sonic-lab"

def run(cmd, check=True):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=check)
print("\n================ RIP + REDISTRIBUTION (R2) ================\n")

r2 = f"{LAB_PREFIX}-r2"

rip_cmds = [
    "conf t",

    # 🔹 Static routes for redistribution
    "ip route 192.168.2.0/24 Null0",
    "ip route 2.2.2.2/32 Null0",

    # 🔹 RIP configuration
    "router rip",
    "version 2",
    # "network 192.168.2.0/24",
    # "network 2.2.2.2/32",
    "redistribute static",
    "exit",

    # 🔹 OSPF redistribution
    "router ospf",
    "redistribute connected",
    "exit",

    "end"
]

run([
    "docker", "exec", r2,
    "vtysh",
    *sum([["-c", c] for c in rip_cmds], [])
])

print("✅ RIP configured and redistributed into OSPF on R2")

print("\n================ VERIFICATION START ================\n")
# container = f"{LAB_PREFIX}-{r}"
for r in ROUTERS.keys():
    container = f"{LAB_PREFIX}-{r}"

    # 1️⃣ Show routing table
    run_show(container, "show ip ospf route")
    time.sleep(5)
    # 2️⃣ Show OSPF neighbors
    run_show(container, "show ip ospf neighbor")
    run_show(container, "show ip ospf database")

