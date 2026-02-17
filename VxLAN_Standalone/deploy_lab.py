# VXLAN_deploy_lab.py
import subprocess

subprocess.run(["containerlab", "destroy", "-t", "lab/topo.yaml"])
subprocess.run(["containerlab", "deploy", "-t", "lab/topo.yaml"], check=True)

print("✅ VXLAN lab deployed")
