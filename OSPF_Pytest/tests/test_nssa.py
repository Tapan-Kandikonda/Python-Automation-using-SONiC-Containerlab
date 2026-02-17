import subprocess, time,logging
logger = logging.getLogger(__name__)

LAB="clab-sonic-lab"

def run(c,cmd):
    return subprocess.run(["docker","exec",c,"vtysh","-c",cmd],
                          stdout=subprocess.PIPE,text=True).stdout

def test_ospf_area_1_nssa_behavior():
    r2=f"{LAB}-r2"

    for r in ["r1","r2"]:
        run(f"{LAB}-{r}","conf t\nrouter ospf\narea 1 nssa\nend")
        run(f"{LAB}-{r}","clear ip ospf process")
    logger.info("NSSA configured successfully")
    time.sleep(60)
    db=run(r2,"show ip ospf database")

    assert "NSSA-external Link States" in db
    assert "0.0.0.0" in db
    logger.info("NSSA verified successfully")
