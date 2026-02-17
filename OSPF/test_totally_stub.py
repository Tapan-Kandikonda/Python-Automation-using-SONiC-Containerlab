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

print("\n================ BEFORE TOTALLY STUB CONFIG ================")

r5_container = f"{LAB_PREFIX}-r5"

ospf_db_before = run(r5_container, "show ip ospf database")
ospf_route_before = run(r5_container, "show ip ospf route")

print("\n🔍 R5 OSPF DATABASE (BEFORE)")
print(ospf_db_before)

print("\n🔍 R5 OSPF ROUTES (BEFORE)")
print(ospf_route_before)


# ------------------ APPLY TOTALLY STUB ------------------

print("\n================ APPLY TOTALLY STUB CONFIG ================")

# ABR → totally stub
abr_container = f"{LAB_PREFIX}-r4"
print("  → Configuring ABR (r4) as totally stub")
run(abr_container, "conf t\nrouter ospf\narea 2 stub no-summary\nend")
print("  → Clearing OSPF process on r4")
run(abr_container, "clear ip ospf process")

# Internal router → stub
internal_container = f"{LAB_PREFIX}-r5"
print("  → Configuring internal router (r5) as stub")
run(internal_container, "conf t\nrouter ospf\narea 2 stub\nend")
print("  → Clearing OSPF process on r5")
run(internal_container, "clear ip ospf process")

time.sleep(60)


# ------------------ AFTER STATE ------------------

print("\n================ AFTER TOTALLY STUB CONFIG ================")

ospf_db_after = run(r5_container, "show ip ospf database")
ospf_route_after = run(r5_container, "show ip ospf route")

print("\n🔍 R5 OSPF DATABASE (AFTER)")
print(ospf_db_after)

print("\n🔍 R5 OSPF ROUTES (AFTER)")
print(ospf_route_after)


# ------------------ VALIDATION ------------------

print("\n================ VALIDATION (TOTALLY STUB) ================")

failed = False

# Default route MUST exist
if "0.0.0.0/0" in ospf_route_after:
    print("  ✅ Default route present (expected)")
else:
    print("  ❌ Default route missing")
    failed = True

# Only default inter-area route is allowed
for line in ospf_route_after.splitlines():
    if line.startswith("N IA") and "0.0.0.0/0" not in line:
        print(f"  ❌ Non-default inter-area route found: {line}")
        failed = True
        break
else:
    print("  ✅ Only default inter-area route present (expected)")


# External routes MUST NOT exist
if "N E" not in ospf_route_after:
    print("  ✅ No external routes (expected)")
else:
    print("  ❌ External routes found")
    failed = True

# Default summary LSA MUST exist
if "0.0.0.0" in ospf_db_after:
    print("  ✅ Default summary LSA present (expected)")
else:
    print("  ❌ Default summary LSA missing")
    failed = True

# No AS External LSAs
if "AS External Link States" not in ospf_db_after:
    print("  ✅ No Type-5 LSAs (expected)")
else:
    print("  ❌ Type-5 LSAs present")
    failed = True

# No non-default summary LSAs
if "Summary Net Link States" in ospf_db_after and "0.0.0.0" not in ospf_db_after:
    print("  ❌ Non-default summary LSAs found")
    failed = True
else:
    print("  ✅ No non-default summary LSAs (expected)")


# ------------------ RESULT ------------------

print("\n================ VALIDATION RESULT ================")

if failed:
    print("🚨 TOTALLY STUB AREA VALIDATION FAILED")
else:
    print("🎉 TOTALLY STUB AREA CONFIGURATION VERIFIED SUCCESSFULLY")


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

print("\n================ FINAL RESULT ================")

if failed:
    sys.exit(1)
else:
    sys.exit(0)
