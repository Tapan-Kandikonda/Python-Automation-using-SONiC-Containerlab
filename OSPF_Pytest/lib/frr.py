import subprocess
import time

LAB_PREFIX = "clab-sonic-lab"
DAEMONS = ["zebra", "bgpd", "ospfd", "ripd"]

def exec_cmd(container, *cmd):
    subprocess.run(["docker", "exec", container, *cmd], check=True)

def enable_frr(routers):
    for r in routers:
        c = f"{LAB_PREFIX}-{r}"
        for d in DAEMONS:
            exec_cmd(c, "sed", "-i", f"s/^{d}=.*/{d}=yes/", "/etc/frr/daemons")
        exec_cmd(c, "service", "frr", "restart")

def wait_for_frr(container, timeout=60):
    for _ in range(timeout):
        r = subprocess.run(
            ["docker", "exec", container, "vtysh", "-c", "show version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if r.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("FRR not ready")
