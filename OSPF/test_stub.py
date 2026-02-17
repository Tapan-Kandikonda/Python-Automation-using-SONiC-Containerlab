import subprocess
import sys
import time

LAB_PREFIX = "clab-sonic-lab"


def run(container, cmd):
    return subprocess.run(
        ["docker", "exec", container, "vtysh", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    ).stdout

#
# print("🔧 Applying OSPF stub configuration")
#
# for r in ["r4", "r5"]:
#     container = f"{LAB_PREFIX}-{r}"
#     print(f"  → Configuring stub area on {r}")
#     run(container, "conf t\nrouter ospf\narea 2 stub\nend")

# ------------------ BEFORE STATE ------------------
print("\n================ BEFORE STUB CONFIG ================")

r5_container = f"{LAB_PREFIX}-r5"

ospf_db_before = run(r5_container, "show ip ospf database")
ospf_route_before = run(r5_container, "show ip ospf route")

print("\n🔍 R5 OSPF Neighbors (BEFORE)")
print(ospf_db_before)

print("\n🔍 R5 OSPF Routes (BEFORE)")
print(ospf_route_before)


# ------------------ APPLY STUB ------------------
print("\n================ APPLY STUB CONFIG ================")

for r in ["r4", "r5"]:
    container = f"{LAB_PREFIX}-{r}"
    print(f"  → Configuring stub area on {r}")
    run(container, "conf t\nrouter ospf\narea 2 stub\nend")
    print(f"  → Clearing OSPF process on {r}")
    run(container, "clear ip ospf process")
time.sleep(60)

# ------------------ AFTER STATE ------------------
print("\n================ AFTER STUB CONFIG ================")

ospf_db_after = run(r5_container, "show ip ospf database")
ospf_route_after = run(r5_container, "show ip ospf route")

print("\n🔍 R5 OSPF Neighbors (AFTER)")
print(ospf_db_after)

print("\n🔍 R5 OSPF Routes (AFTER)")
print(ospf_route_after)




# print("\n🔍 Validating OSPF stub behavior on r5")
# output = run(f"{LAB_PREFIX}-r5", "show ip ospf route")
#
# failed = False
#
# if "0.0.0.0/0" in output:
#     print("  ✅ Default route (0.0.0.0/32) present (expected)")
# else:
#     print("  ❌ Default route missing")
#     failed = True
#
# if "O IA" not in output:
#     print("  ✅ No inter-area routes (expected)")
# else:
#     print("  ❌ Inter-area routes found")
#     failed = True
#
# if "O E" not in output:
#     print("  ✅ No external routes (expected)")
# else:
#     print("  ❌ External routes found")
#     failed = True

# ------------------ VALIDATION ------------------
print("\n================ VALIDATION ================")

failed = False

# Default route must exist
if "0.0.0.0/0" in ospf_route_after:
    print("  ✅ Default route present (expected)")
else:
    print("  ❌ Default route missing")
    failed = True

# Inter-area routes ARE allowed in stub
if "N IA" in ospf_route_after:
    print("  ✅ Inter-area routes present (expected)")
else:
    print("  ❌ Inter-area routes missing")
    failed = True

# External routes must NOT be installed
if "N E" not in ospf_route_after:
    print("  ✅ No external routes installed (expected)")
else:
    print("  ❌ External routes installed")
    failed = True


# Default summary LSA should exist
if "0.0.0.0" in ospf_db_after:
    print("  ✅ Default summary LSA present (expected)")
else:
    print("  ❌ Default summary LSA missing")
    failed = True

# AS External LSAs must NOT exist in stub
if "AS External Link States" not in ospf_db_after:
    print("  ✅ No Type-5 LSAs (expected)")
else:
    print("  ❌ Type-5 LSAs present")
    failed = True

# Inter-area summaries (non-default) should not exist
if "Summary Net Link States" not in ospf_db_after:
    print("  ✅ No inter-area summary LSAs (expected)")
else:
    print("  ❌ Inter-area summary LSAs found")
    failed = True



print("\n================ VALIDATION RESULT ================")

test_failed = failed

if test_failed:
    print("🚨 STUB AREA VALIDATION FAILED")
else:
    print("🎉 STUB AREA CONFIGURATION VERIFIED SUCCESSFULLY")




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
#
#
print("\n================ FINAL RESULT ================")

if test_failed:
    sys.exit(1)
else:
    sys.exit(0)
