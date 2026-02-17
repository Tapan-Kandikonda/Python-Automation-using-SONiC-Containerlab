import pytest
from lib.topo import generate_topology
from lib.lab import deploy_lab
from lib.lab import destroy_lab
from lib.frr import enable_frr, wait_for_frr
from lib.base_config import apply_base_config
from lib.rip import apply_rip


ROUTERS = ["r1", "r2", "r3", "r4", "r5"]

@pytest.fixture(scope="session", autouse=True)
def lab():
    generate_topology()
    deploy_lab()

    enable_frr(ROUTERS)
    for r in ROUTERS:
        wait_for_frr(f"clab-sonic-lab-{r}")

    apply_base_config()
    apply_rip()

    yield
    destroy_lab()

import subprocess
import time
import logging

LAB = "clab-sonic-lab"

# def vty(container, cmds):
#     subprocess.run(
#         ["docker", "exec", container, "vtysh",
#          *sum([["-c", c] for c in cmds], [])],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )

@pytest.fixture(autouse=True)
def cleanup_special_areas():
    yield   # test runs first

    logging.info("🧹 Removing OSPF special-area configurations (stub/NSSA/TNSSA)")

    def vty(container, cmds):
        subprocess.run(
            ["docker", "exec", container, "vtysh",
             *sum([["-c", c] for c in cmds], [])],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    for r in ROUTERS:
        vty(f"{LAB}-{r}", [
            "conf t",
            "router ospf",
            "no area 1 stub",
            "no area 1 stub no-summary",
            "no area 1 nssa",
            "no area 1 nssa no-summary",
            "no area 2 stub",
            "no area 2 stub no-summary",
            "no area 2 nssa",
            "no area 2 nssa no-summary",
            "end"
        ])

    for r in ROUTERS:
        vty(f"{LAB}-{r}", ["clear ip ospf process"])

    logging.info("✅ OSPF special-area configuration cleanup complete")
    time.sleep(30)

