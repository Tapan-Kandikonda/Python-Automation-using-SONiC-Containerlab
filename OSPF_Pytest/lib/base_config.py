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
    "r2": ("22.22.22.22", [("192.168.1.0/24", 1)]),
    "r3": ("3.3.3.3", [("10.0.1.0/24", 0), ("10.0.2.0/24", 0)]),
    "r4": ("4.4.4.4", [("10.0.2.0/24", 0), ("172.16.1.0/24", 2)]),
    "r5": ("5.5.5.5", [("172.16.1.0/24", 2)]),
}

def vtysh(container, cmds):
    subprocess.run(
        ["docker", "exec", container, "vtysh",
         *sum([["-c", c] for c in cmds], [])],
        check=True
    )

def apply_base_config():
    for r, ifaces in ROUTERS.items():
        c = f"{LAB_PREFIX}-{r}"
        for iface, ip in ifaces:
            vtysh(c, [
                "conf t",
                f"interface {iface}",
                f"ip address {ip}",
                "no shutdown",
                "end"
            ])

    for r, ip in LOOPBACKS.items():
        vtysh(f"{LAB_PREFIX}-{r}", [
            "conf t",
            "interface lo",
            f"ip address {ip}",
            "end"
        ])

    time.sleep(5)

    for r, (rid, networks) in OSPF.items():
        areas = {a for _, a in networks}
        loop_area = min(areas)

        cmds = [
            "conf t",
            "router ospf",
            f"router-id {rid}",
            f"network {rid}/32 area {loop_area}"
        ]
        for net, area in networks:
            cmds.append(f"network {net} area {area}")
        cmds.append("end")

        vtysh(f"{LAB_PREFIX}-{r}", cmds)

    time.sleep(30)
