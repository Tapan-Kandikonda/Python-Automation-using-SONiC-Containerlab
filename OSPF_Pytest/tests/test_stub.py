import subprocess, time,logging

LAB="clab-sonic-lab"

def run(c,cmd):
    return subprocess.run(
        ["docker","exec",c,"vtysh","-c",cmd],
        stdout=subprocess.PIPE,
        text=True
    ).stdout

def test_ospf_area_2_stub_behavior():
    print("\n[STEP] Configure stub area on r4 and r5")

    for r in ["r4","r5"]:
        run(f"{LAB}-{r}", "conf t\nrouter ospf\narea 2 stub\nend")
        run(f"{LAB}-{r}", "clear ip ospf process")
    logging.info("Area 2 Stub Configuration successful)")
    print("[STEP] Waiting for OSPF convergence")
    time.sleep(60)

    print("[STEP] Validating routes on r5")
    out = run(f"{LAB}-r5", "show ip ospf route")

    # print(out)

    assert "0.0.0.0/0" in out, "Default route missing"
    assert "N E" not in out, "External routes present in stub"
    assert "N IA" in out, "Inter-area routes missing"
    logging.info("Area 2 Stub Stub Validated")

def test_ospf_area_1_stub_behavior():
    print("\n[STEP] Configure stub area on r1 and r2")

    for r in ["r1", "r2"]:
        run(f"{LAB}-{r}", "conf t\nrouter ospf\narea 1 stub\nend")
        run(f"{LAB}-{r}", "clear ip ospf process")

    logging.info("Area 1 Stub Configuration successful")
    print("[STEP] Waiting for OSPF convergence")
    time.sleep(60)

    print("[STEP] Validating routes on r2")
    out = run(f"{LAB}-r2", "show ip ospf route")

    # print(out)

    assert "0.0.0.0/0" in out, "Default route missing"
    assert "N E" not in out, "External routes present in stub"
    assert "N IA" in out, "Inter-area routes missing"
    logging.info("Area 1 Stub Validated")

