#!/usr/bin/env bash
# Run from ~/workspace/projectmanager
set -u
PM="python3 main.py"

# Pull the UUID out of "Created <type> '<name>' with id <uuid>"
get_id() { sed -n 's/.* with id \([0-9a-f-]\{36\}\).*/\1/p'; }

create() {  # usage: create <type> args...  -> echoes id
  local out; out=$($PM create "$@")
  echo "$out" >&2
  echo "$out" | get_id
}

echo "===== CREATE PROJECTS ====="
P1=$(create project "Kitchen" "Remodel the kitchen")
P2=$(create project "Garden"  "Build raised garden beds")
P3=$(create project "Garage"  "Organize the garage")

echo "===== CREATE PROJECT STEPS ====="
S1=$(create step "$P1" "Demo"     "Tear out old cabinets")
S2=$(create step "$P1" "Plumbing" "Reroute sink lines")
S3=$(create step "$P1" "Install"  "Install new cabinets")
S4=$(create step "$P2" "Lumber"   "Buy cedar boards")
S5=$(create step "$P2" "Assemble" "Build the beds")
S6=$(create step "$P3" "Sort"     "Sort items into keep/donate")

echo "===== CREATE AREAS ====="
A1=$(create area "Indoor"   "Inside the house")
A2=$(create area "Outdoor"  "Yard and exterior")
A3=$(create area "Workshop" "Garage workshop space")

echo "===== CREATE TOOLS ====="
T1=$(create tool "Drill"    "Cordless drill")
T2=$(create tool "Saw"      "Circular saw")
T3=$(create tool "Wrench"   "Adjustable pipe wrench")

echo "===== GET PROJECTS BY NAME ====="
$PM get project --name "Kitchen"
$PM get project --name "Garden"
$PM get project --name "Garage"

echo "===== GET EACH PROJECT STEP ====="
$PM get step --project-name "Kitchen" --name "Demo"
$PM get step --project-name "Kitchen" --name "Plumbing"
$PM get step --project-name "Kitchen" --name "Install"
$PM get step --project-name "Garden"  --name "Lumber"
$PM get step --project-name "Garden"  --name "Assemble"
$PM get step --project-name "Garage"  --name "Sort"

echo "===== LIST STEPS PER PROJECT ====="
$PM list step --project-name "Kitchen"
$PM list step --project-name "Garden"
$PM list step --project-name "Garage"

echo "===== DELETE (steps first, then projects) ====="
for id in "$S1" "$S2" "$S3" "$S4" "$S5" "$S6"; do $PM delete step "$id"; done
for id in "$P1" "$P2" "$P3"; do $PM delete project "$id"; done
for id in "$A1" "$A2" "$A3"; do $PM delete area "$id"; done
for id in "$T1" "$T2" "$T3"; do $PM delete tool "$id"; done
