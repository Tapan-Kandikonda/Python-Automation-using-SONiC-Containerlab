# VXLAN_gen_topo.py
import yaml, os

os.makedirs("lab", exist_ok=True)

topo = {
    "name": "vxlan-fabric",
    "topology": {
        "nodes": {
            "leaf1": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "spine": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "leaf2": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "server1": {"kind": "linux", "image": "alpine", "network-mode": "none"},
            "server2": {"kind": "linux", "image": "alpine", "network-mode": "none"},
        },
        "links": [
            {"endpoints": ["leaf1:Ethernet0", "spine:Ethernet0"]},
            {"endpoints": ["leaf2:Ethernet0", "spine:Ethernet4"]},
            {"endpoints": ["server1:eth0", "leaf1:Ethernet4"]},
            {"endpoints": ["server2:eth0", "leaf2:Ethernet4"]},
        ],
    },
}

with open("lab/topo.yaml", "w") as f:
    yaml.dump(topo, f)

print("✅ VXLAN topology generated")
