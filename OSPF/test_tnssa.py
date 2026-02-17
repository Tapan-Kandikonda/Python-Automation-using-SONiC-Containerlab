import subprocess
import sys
import time

LAB_PREFIX = "clab-sonic-lab"

# ------------------ HELPERS ------------------

def run(container, cmd):
    return subprocess.run(
        ["docker", "exec", container, "vtysh", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    ).stdout


# ------------------ BEFORE STATE ------------------
print("\n================ BEFORE TNSSA CONFIG ================")

r2_container = f"{LAB_PREFIX}-r2"

ospf_db_before = run(r2_container, "show ip ospf database")

print("\n🔍 R2 OSPF Neighbors (BEFORE)")
print(ospf_db_before)


print("\n================ APPLY TNSSA CONFIG ================")

# ABR → totally stub
abr_container = f"{LAB_PREFIX}-r1"
print("  → Configuring ABR (r1) as tnssa")
run(abr_container, "conf t\nrouter ospf\narea 1 nssa no-summary\nend")
print("  → Clearing OSPF process on r1")
run(abr_container, "clear ip ospf process")

# Internal router → stub
internal_container = f"{LAB_PREFIX}-r2"
print("  → Configuring internal router (r2) as nssa")
run(internal_container, "conf t\nrouter ospf\narea 1 nssa\nend")
print("  → Clearing OSPF process on r2")
run(internal_container, "clear ip ospf process")

time.sleep(60)

# ------------------ AFTER STATE ------------------
print("\n================ AFTER NSSA CONFIG ================")

ospf_db_after = run(internal_container, "show ip ospf database")

print("\n🔍 R2 OSPF Neighbors (AFTER)")
print(ospf_db_after)

import re

failed = False

ospf_db = ospf_db_after   # reuse already-fetched output

# ---------- SUMMARY LSA CHECK ----------
summary_block = re.search(
    r"Summary Link States.*?(?=\n\s+\S+ Link States|\Z)",
    ospf_db,
    re.S
)

if not summary_block:
    print("  ❌ Summary Link States section not found")
    failed = True
else:
    link_ids = re.findall(
        r"^\s*(\d+\.\d+\.\d+\.\d+)\s+",
        summary_block.group(0),
        re.M
    )

    if link_ids == ["0.0.0.0"]:
        print("  ✅ Only default summary LSA (0.0.0.0) present (expected)")
    else:
        print("  ❌ Unexpected summary LSAs found:")
        for ip in link_ids:
            print(f"     {ip}")
        failed = True

# ---------- NSSA TYPE-7 CHECK ----------
print("\n================ VALIDATION ================")

if "NSSA-external Link States" in ospf_db:
    print("  ✅ Type-7 LSAs present (expected)")
else:
    print("  ❌ Type-7 LSAs missing")
    failed = True

# ---------- FINAL RESULT ----------
if failed:
    print("\n❌ TNSSA VALIDATION FAILED")
else:
    print("\n✅ TNSSA VALIDATION PASSED")

print("\n================ CONFIG REMOVAL ================")
LAB_PREFIX = "clab-sonic-lab"
ROUTERS = ["r1", "r2", "r3", "r4", "r5"]

def run(cmd):
    subprocess.run(cmd, check=False)

for r in ROUTERS:
    cmds = [
        "conf t",
        "router ospf",
        "no area 1 stub",
        "no area 1 stub no-summary",
        "no area 2 nssa",
        "no area 2 nssa no-summary",
        "do clear ip ospf process",
        "end",
    ]

    run([
        "docker", "exec", f"{LAB_PREFIX}-{r}",
        "vtysh",
        *sum([["-c", c] for c in cmds], [])
    ])
time.sleep(45)
print("🧹 OSPF special-area configuration cleaned")

if failed:
    sys.exit(1)
else:
    sys.exit(0)
