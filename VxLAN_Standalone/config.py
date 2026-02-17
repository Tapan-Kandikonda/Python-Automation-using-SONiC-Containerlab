# VXLAN_config_new.py
import subprocess, time

LAB = "clab-vxlan-fabric"

def run(cmd):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=True)

def wait(container):
    for _ in range(60):
        if subprocess.run(
            ["docker","exec",container,"vtysh","-c","show version"],
            stdout=subprocess.DEVNULL
        ).returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("FRR not ready")

# ----------- UNDERLAY IPs -----------

UNDERLAY = {
    "leaf1": [
        "ip link set lo up",   # 🔴 THIS WAS MISSING
        "ip addr add 10.0.12.1/30 dev Ethernet0",
        "ip link set Ethernet0 up",
        "ip addr add 1.1.1.1/32 dev lo"
    ],
    "spine": [
        "ip link set lo up",
        "ip addr add 10.0.12.2/30 dev Ethernet0",
        "ip addr add 10.0.23.1/30 dev Ethernet4",
        "ip link set Ethernet0 up",
        "ip link set Ethernet4 up"
    ],
    "leaf2": [
        "ip link set lo up",   # 🔴 THIS WAS MISSING
        "ip addr add 10.0.23.2/30 dev Ethernet0",
        "ip link set Ethernet0 up",
        "ip addr add 2.2.2.2/32 dev lo"
    ]
}

for r, cmds in UNDERLAY.items():
    c = f"{LAB}-{r}"
    wait(c)
    for cmd in cmds:
        run(["docker","exec",c,"bash","-c",cmd])

# ----------- OSPF -----------

OSPF = {
    "leaf1": [
        "router ospf",
        "router-id 1.1.1.1",
        "network 10.0.12.0/30 area 0",
        "network 1.1.1.1/32 area 0"
    ],
    "spine": [
        "router ospf",
        "router-id 0.0.0.1",
        "network 10.0.12.0/30 area 0",
        "network 10.0.23.0/30 area 0"
    ],
    "leaf2": [
        "router ospf",
        "router-id 2.2.2.2",
        "network 10.0.23.0/30 area 0",
        "network 2.2.2.2/32 area 0"
    ]
}

for r, cmds in OSPF.items():
    c = f"{LAB}-{r}"
    vty = ["docker","exec",c,"vtysh","-c","conf t"]
    for line in cmds:
        vty += ["-c", line]
    vty += ["-c","end","-c","write"]
    run(vty)
time.sleep(30)

# ----------- SERVERS -----------

SERVERS = {
    "server1": "ip addr add 192.168.100.10/24 dev eth0 && ip link set eth0 up",
    "server2": "ip addr add 192.168.100.20/24 dev eth0 && ip link set eth0 up"
}

for s, cmd in SERVERS.items():
    run(["docker","exec",f"{LAB}-{s}","sh","-c",cmd])

# ----------- VXLAN (LEAFS) -----------

VXLAN = {
    "leaf1": [
        "ip link add br-vlan100 type bridge",
        "ip link set br-vlan100 up",
        "ip link set Ethernet4 up",
        "ip link set Ethernet4 master br-vlan100",
        "ip link add vxlan100 type vxlan id 10000 dev Ethernet0 local 1.1.1.1 remote 2.2.2.2 dstport 4789",
        "ip link set vxlan100 up",
        "ip link set vxlan100 master br-vlan100",
        "bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst 2.2.2.2"
    ],
    "leaf2": [
        "ip link add br-vlan100 type bridge",
        "ip link set br-vlan100 up",
        "ip link set Ethernet4 up",
        "ip link set Ethernet4 master br-vlan100",
        "ip link add vxlan100 type vxlan id 10000 dev Ethernet0 local 2.2.2.2 remote 1.1.1.1 dstport 4789",
        "ip link set vxlan100 up",
        "ip link set vxlan100 master br-vlan100",
        "bridge fdb append 00:00:00:00:00:00 dev vxlan100 dst 1.1.1.1"
    ]
}

for r, cmds in VXLAN.items():
    c = f"{LAB}-{r}"
    for cmd in cmds:
        run(["docker","exec",c,"bash","-c",cmd])
time.sleep(20)

print("\n🎯 VXLAN overlay fully configured")
