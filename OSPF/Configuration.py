import subprocess
import time


LAB_PREFIX = "clab-sonic-lab"

ROUTERS = {
    "r1": [("Ethernet0", "192.168.1.1/24"), ("Ethernet1", "10.0.1.1/24")],
    "r2": [("Ethernet0", "192.168.1.2/24"), ("Ethernet1", "192.168.2.1/24")],
    "r3": [("Ethernet0", "10.0.1.2/24"), ("Ethernet1", "10.0.2.1/24")],
    "r4": [("Ethernet0", "10.0.2.2/24"), ("Ethernet1", "172.16.1.1/24")],
    "r5": [("Ethernet0", "172.16.1.2/24")],
}


LOOPBACKS = {
    "r1": "1.1.1.1/32",
    "r2": "2.2.2.2/32",
    "r3": "3.3.3.3/32",
    "r4": "4.4.4.4/32",
    "r5": "5.5.5.5/32",
}
OSPF = {
    "r1": ("1.1.1.1", [("192.168.1.0/24", 1), ("10.0.1.0/24", 0)]),
    "r2": ("22.22.22.22", [("192.168.1.0/24", 1)]),  # 🔴 router-id ≠ loopback
    "r3": ("3.3.3.3", [("10.0.1.0/24", 0), ("10.0.2.0/24", 0)]),
    "r4": ("4.4.4.4", [("10.0.2.0/24", 0), ("172.16.1.0/24", 2)]),
    "r5": ("5.5.5.5", [("172.16.1.0/24", 2)]),
}


def run(cmd, check=True):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=check)


def wait_for_frr(container, timeout=60):
    print(f"⏳ Waiting for FRR (zebra) on {container}")
    for _ in range(timeout):
        result = subprocess.run(
            ["docker", "exec", container, "vtysh", "-c", "show version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            print("✅ FRR is ready")
            return
        time.sleep(1)

    raise RuntimeError(f"FRR not ready on {container} after {timeout}s")
def run_show(container, command):
    print(f"\n{container} :: {command}")
    subprocess.run(
        ["docker", "exec", container, "vtysh", "-c", command],
        check=True
    )

# def ping(container, ip, seconds=5):
#     print(f"📡 {container} :: ping {ip} (timeout={seconds}s)")
#     subprocess.run(
#         [
#             "docker", "exec", container,
#             "timeout", str(seconds),
#             "vtysh",
#             "-c", f"ping {ip}"
#         ],
#         check=False  # timeout exits with non-zero, this is EXPECTED
#     )


for r, ifaces in ROUTERS.items():
    container = f"{LAB_PREFIX}-{r}"

    wait_for_frr(container)

    print(f"\n🔧 Configuring interfaces on {container}")
    for iface, ip in ifaces:
        run([
            "docker", "exec", container,
            "vtysh",
            "-c", "configure terminal",
            "-c", f"interface {iface}",
            "-c", f"ip address {ip}",
            "-c", "no shutdown",
            "-c", "exit",
            "-c", "exit",
        ])

print("\n✅ Interface configuration completed")


def run(cmd):
    subprocess.run(cmd, check=True)

for r, ip in LOOPBACKS.items():
    run([
        "docker", "exec", f"{LAB_PREFIX}-{r}",
        "vtysh",
        "-c", "configure terminal",
        "-c", "interface lo",
        "-c", f"ip address {ip}",
        "-c", "exit",
        "-c", "exit"
    ])

print("✅ Loopbacks configured")
time.sleep(5)


print("\n================ INTERFACE VERIFICATION ================\n")


for r in ROUTERS.keys():
    container = f"{LAB_PREFIX}-{r}"
    run_show(container, "show interface brief")

print("\n================ INTERFACE CHECK COMPLETE ================")


def run(cmd):
    subprocess.run(cmd, check=True)

for r, (rid, networks) in OSPF.items():
    # Collect all areas the router participates in
    areas = {area for _, area in networks}

    # Assign loopback to the lowest-numbered area
    loopback_area = min(areas)

    cmds = [
        "conf t",
        "router ospf",
        f"router-id {rid}",
        f"network {rid}/32 area {loopback_area}",  # ✅ lowest area
    ]

    for net, area in networks:
        cmds.append(f"network {net} area {area}")

    cmds.append("end")

    run([
        "docker", "exec", f"{LAB_PREFIX}-{r}",
        "vtysh",
        *sum([["-c", c] for c in cmds], [])
    ])

    print(f"✅ Base OSPF + loopback configured on {r}")

print("Waiting for OSPF to come up")
time.sleep(30)

# print("\n================ RIP + REDISTRIBUTION (R2) ================\n")
#
# r2 = f"{LAB_PREFIX}-r2"
#
# rip_cmds = [
#     "conf t",
#
#     # 🔹 Static routes for redistribution
#     "ip route 192.168.2.0/24 Null0",
#     "ip route 2.2.2.2/32 Null0",
#
#     # 🔹 RIP configuration
#     "router rip",
#     "version 2",
#     "network 192.168.2.0/24",
#     "network 2.2.2.2/32",
#     "redistribute static",
#     "exit",
#
#     # 🔹 OSPF redistribution
#     "router ospf",
#     "redistribute connected",
#     "exit",
#
#     "end"
# ]
#
# run([
#     "docker", "exec", r2,
#     "vtysh",
#     *sum([["-c", c] for c in rip_cmds], [])
# ])
#
# print("✅ RIP configured and redistributed into OSPF on R2")


#
# print("\n================ VERIFICATION START ================\n")
# # container = f"{LAB_PREFIX}-{r}"
# for r in ROUTERS.keys():
#     container = f"{LAB_PREFIX}-{r}"
#
#     # 1️⃣ Show routing table
#     run_show(container, "show ip ospf route")
#     time.sleep(15)
#     # 2️⃣ Show OSPF neighbors
#     run_show(container, "show ip ospf neighbor")
#
#     # 3️⃣ Ping all other loopbacks
#
#     # for target, loop_ip in LOOPBACKS.items():
#     #     if target == r:
#     #         continue
#     #
#     #     ip_only = loop_ip.split("/")[0]
#     #     ping(container, ip_only)
#
# print("\n================ VERIFICATION COMPLETE ================")

