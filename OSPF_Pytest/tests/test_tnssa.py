import subprocess, time, re, logging

LAB="clab-sonic-lab"

def run(c,cmd):
    return subprocess.run(["docker","exec",c,"vtysh","-c",cmd],
                          stdout=subprocess.PIPE,text=True).stdout

def test_ospf_area_1_totally_nssa_behavior():
    r2=f"{LAB}-r2"

    run(f"{LAB}-r1","conf t\nrouter ospf\narea 1 nssa no-summary\nend")
    run(f"{LAB}-r1","clear ip ospf process")

    run(f"{LAB}-r2","conf t\nrouter ospf\narea 1 nssa\nend")
    run(f"{LAB}-r2","clear ip ospf process")
    logging.info("TNSSA configured successfully ")
    time.sleep(60)
    db=run(r2,"show ip ospf database")

    block=re.search(r"Summary Link States.*?(?=\n\s+\S+ Link States|\Z)",db,re.S)
    assert block

    ids=re.findall(r"^\s*(\d+\.\d+\.\d+\.\d+)",block.group(0),re.M)
    assert ids==["0.0.0.0"]

    assert "NSSA-external Link States" in db
    logging.info("TNSSA verified successfully")
