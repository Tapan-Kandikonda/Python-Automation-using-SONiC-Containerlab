import subprocess

LAB_PREFIX = "clab-sonic-lab"

def vtysh(container, *cmds):
    subprocess.run(
        ["docker", "exec", container, "vtysh",
         *sum([["-c", c] for c in cmds], [])],
        check=True
    )

def clear_ospf(router):
    vtysh(f"{LAB_PREFIX}-{router}", "clear ip ospf process")
