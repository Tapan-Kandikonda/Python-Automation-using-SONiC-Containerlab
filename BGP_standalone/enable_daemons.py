import subprocess

ROUTERS = ["r1", "r2", "r3"]
LAB = "clab-sonic-lab"
DAEMONS = ["zebra", "bgpd"]

def run(cmd):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=True)

for r in ROUTERS:
    c = f"{LAB}-{r}"
    for d in DAEMONS:
        run(["docker","exec",c,"sed","-i",f"s/^{d}=.*/{d}=yes/","/etc/frr/daemons"])
    run(["docker","exec",c,"service","frr","restart"])

print("✅ BGP daemons enabled")
