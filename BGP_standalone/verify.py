import subprocess, time

LAB = "clab-sonic-lab"
time.sleep(30)

def run(cmd):
    print("➡️", " ".join(cmd))
    subprocess.run(cmd, check=False)

# --- BGP state ---
for r in ["r1","r2","r3"]:
    print(f"\n{r}")
    run(["docker","exec",f"{LAB}-{r}","vtysh","-c","show bgp summary"])

# --- vtysh ping (like OSPF) ---
print("\n📡 vtysh ping R3 → R1")
run([
    "docker","exec",f"{LAB}-r3",
    "timeout","5",
    "vtysh","-c","ping 1.1.1.1"
])
