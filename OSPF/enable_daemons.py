import subprocess

ROUTERS = ["r1", "r2", "r3","r4","r5"]
LAB_PREFIX = "clab-sonic-lab"
DAEMONS = ["zebra", "bgpd", "ospfd", "ripd"]

def run(cmd, check=True):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=check)

for r in ROUTERS:
    container = f"{LAB_PREFIX}-{r}"
    print(f"\n⚙️ Enabling FRR daemons on {container}")

    # 1️⃣ Enable daemons in /etc/frr/daemons
    for d in DAEMONS:
        run([
            "docker", "exec", container,
            "sed", "-i",
            f"s/^{d}=.*/{d}=yes/",
            "/etc/frr/daemons"
        ])

    # 2️⃣ Restart FRR the WORKING way (inside container)
    print("🔄 Restarting FRR using service frr restart")
    run([
        "docker", "exec", container,
        "service", "frr", "restart"
    ])

print("\n✅ FRR daemons enabled and restarted correctly")
