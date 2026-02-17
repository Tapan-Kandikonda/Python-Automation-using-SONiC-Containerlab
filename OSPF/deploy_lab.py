import subprocess

subprocess.run(
    ["containerlab", "deploy", "-t", "lab/topo.yaml"],
    check=True
)

print("✅ Containerlab deployed")
