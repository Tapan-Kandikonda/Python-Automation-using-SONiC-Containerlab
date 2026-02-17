from lib.base_config import vtysh, LAB_PREFIX

def apply_rip():
    vtysh(f"{LAB_PREFIX}-r2", [
        "conf t",
        "ip route 192.168.2.0/24 Null0",
        "ip route 2.2.2.2/32 Null0",

        "router rip",
        "version 2",
        "redistribute static",
        "exit",

        "router ospf",
        "redistribute connected",
        "end"
    ])
