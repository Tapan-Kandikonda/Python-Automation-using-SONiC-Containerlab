import subprocess

def deploy_lab(topo="lab/topo.yaml"):
    subprocess.run(["containerlab", "deploy", "-t", topo], check=True)

def destroy_lab(topo="lab/topo.yaml"):
    subprocess.run(["containerlab", "destroy", "-t", topo, "--cleanup"], check=False)
