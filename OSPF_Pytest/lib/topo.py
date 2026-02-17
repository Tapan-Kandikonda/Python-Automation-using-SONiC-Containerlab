import yaml
import os

def generate_topology(path="lab/topo.yaml"):
    os.makedirs("lab", exist_ok=True)

    topo = {
        "name": "sonic-lab",
        "topology": {
            "nodes": {
                f"r{i}": {"kind": "sonic-vs", "image": "docker-sonic-vs:latest"}
                for i in range(1, 6)
            },
            "links": [
                {"endpoints": ["r2:Ethernet0", "r1:Ethernet0"]},
                {"endpoints": ["r1:Ethernet1", "r3:Ethernet0"]},
                {"endpoints": ["r3:Ethernet1", "r4:Ethernet0"]},
                {"endpoints": ["r4:Ethernet1", "r5:Ethernet0"]},
            ],
        },
    }

    with open(path, "w") as f:
        yaml.dump(topo, f)
