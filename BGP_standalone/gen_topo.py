import yaml, os

os.makedirs("lab", exist_ok=True)

topo = {
    "name": "sonic-lab",
    "topology": {
        "nodes": {
            "r1": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r2": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
            "r3": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"},
        },
        "links": [
            {"endpoints": ["r1:Ethernet0", "r2:Ethernet0"]},
            {"endpoints": ["r2:Ethernet1", "r3:Ethernet0"]},
        ],
    },
}

with open("lab/topo.yaml", "w") as f:
    yaml.dump(topo, f)

print("✅ Topology generated")
