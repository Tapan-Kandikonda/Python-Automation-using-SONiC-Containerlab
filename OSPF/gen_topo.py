import yaml
import os

os.makedirs("lab", exist_ok=True)

topo = {
    "name": "sonic-lab",
    "topology": {
        "nodes": {
            "r1": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r2": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r3": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r4": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r5": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
        },
        "links": [
            {"endpoints": ["r2:Ethernet0", "r1:Ethernet0"]},
            {"endpoints": ["r1:Ethernet1", "r3:Ethernet0"]},
            {"endpoints": ["r3:Ethernet1", "r4:Ethernet0"]},
            {"endpoints": ["r4:Ethernet1", "r5:Ethernet0"]},
        ],
    },
}

with open("lab/topo.yaml", "w") as f:
    yaml.dump(topo, f)

print("✅ Topology generated")
