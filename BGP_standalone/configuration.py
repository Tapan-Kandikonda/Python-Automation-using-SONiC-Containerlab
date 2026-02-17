import subprocess, time

LAB="clab-sonic-lab"

def run(cmd):
    subprocess.run(cmd, check=True)

def wait(container):
    for _ in range(60):
        if subprocess.run(["docker","exec",container,"vtysh","-c","show version"],
                          stdout=subprocess.DEVNULL).returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("FRR not ready")

INTERFACES = {
    "r1":[("Ethernet0","192.168.1.1/24")],
    "r2":[("Ethernet0","192.168.1.2/24"),("Ethernet1","192.168.2.1/24")],
    "r3":[("Ethernet0","192.168.2.2/24")]
}

LOOPS={"r1":"1.1.1.1/32","r2":"2.2.2.2/32","r3":"3.3.3.3/32"}

STATIC = {
    "r1":[("2.2.2.2/32","192.168.1.2")],
    "r2":[("1.1.1.1/32","192.168.1.1"),("3.3.3.3/32","192.168.2.2")],
    "r3":[("2.2.2.2/32","192.168.2.1")]
}
ROUTE_MAP = {
    "r2": ["route-map EBGP-ALLOW permit 10"],
    "r3": ["route-map EBGP-ALLOW permit 10"]
}

POLICY = {
    "r2": True,
    "r3": True
}


BGP = {
    "r1":[
        "router bgp 100",
        "neighbor 2.2.2.2 remote-as 100",
        "neighbor 2.2.2.2 update-source lo",
        "address-family ipv4 unicast",
        "network 1.1.1.1/32",
        "redistribute static",
        "exit-address-family",
        "end"
    ],
    "r2":[
    "router bgp 100",
    "neighbor 1.1.1.1 remote-as 100",
    "neighbor 1.1.1.1 update-source lo",
    "neighbor 3.3.3.3 remote-as 200",
    "neighbor 3.3.3.3 ebgp-multihop",
    "neighbor 3.3.3.3 update-source lo",
    "address-family ipv4 unicast",
    "network 2.2.2.2/32",
    "redistribute static",
    "neighbor 1.1.1.1 route-reflector-client",
    "neighbor 1.1.1.1 next-hop-self",
    "neighbor 3.3.3.3 next-hop-self",
    "neighbor 3.3.3.3 route-map EBGP-ALLOW in",
    "neighbor 3.3.3.3 route-map EBGP-ALLOW out",
    "exit-address-family",
    "end"
    ],

    "r3":[
    "router bgp 200",
    "neighbor 2.2.2.2 remote-as 100",
    "neighbor 2.2.2.2 ebgp-multihop",
    "neighbor 2.2.2.2 update-source lo",
    "address-family ipv4 unicast",
    "network 3.3.3.3/32",
    "redistribute static",
    "neighbor 2.2.2.2 next-hop-self",
    "neighbor 2.2.2.2 route-map EBGP-ALLOW in",
    "neighbor 2.2.2.2 route-map EBGP-ALLOW out",
    "exit-address-family",
    "end"
    ]

}

for r in INTERFACES:
    c=f"{LAB}-{r}"
    wait(c)

    for iface,ip in INTERFACES[r]:
        run(["docker","exec",c,"vtysh","-c","conf t",
             "-c",f"interface {iface}",
             "-c",f"ip address {ip}",
             "-c","exit","-c","exit"])

    run(["docker","exec",c,"vtysh","-c","conf t",
         "-c","interface lo","-c",f"ip address {LOOPS[r]}","-c","end"])

    for net, nh in STATIC[r]:
        run([
            "docker", "exec", c, "vtysh",
            "-c", "conf t",
            "-c", f"ip route {net} {nh}",
            "-c", "end"
        ])
    if r in ROUTE_MAP:
        run([
            "docker", "exec", c, "vtysh",
            "-c", "conf t",
            *sum([["-c", x] for x in ROUTE_MAP[r]], []),
            "-c", "end"
        ])
    if r in POLICY:
        run([
            "docker", "exec", c, "vtysh",
            "-c", "conf t",
            "-c", "ip prefix-list ANY seq 5 permit 0.0.0.0/0 le 32",
            "-c", "route-map EBGP-ALLOW permit 10",
            "-c", "match ip address prefix-list ANY",
            "-c", "end"
        ])

    run(["docker","exec",c,"vtysh",*sum([["-c",x] for x in ["conf t"]+BGP[r]],[])])

print("✅ BGP config pushed")
