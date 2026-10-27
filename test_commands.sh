#!/usr/bin/env bash
# Run from ~/workspace/projectmanager
set -u
PM="python3 main.py"

# Pull the UUID out of the header line "=== <TYPE>: <name> - (<uuid>) ==="
get_id() { sed -n 's/^===.*(\([0-9a-f-]\{36\}\)) ===.*/\1/p' | head -n 1; }

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

echo "===== CREATE PROJECT AREAS ====="
$PM create projectarea "$P1" "$A1" "Kitchen is indoors"
$PM create projectarea "$P2" "$A2" "Beds go in the back yard"
$PM create projectarea "$P3" "$A3" "Workshop corner of the garage"
$PM create projectarea "$P3" "$A1" "Storage shelves inside"

echo "===== CREATE TOOLS ====="
T1=$(create tool "Drill"    "Cordless drill")
T2=$(create tool "Saw"      "Circular saw")
T3=$(create tool "Wrench"   "Adjustable pipe wrench")

echo "===== CREATE PROJECT STEP TOOLS ====="
$PM create steptool "Kitchen" "Demo"     "Saw"
$PM create steptool "Kitchen" "Plumbing" "Wrench"
$PM create steptool "$P1"     "$S3"       "$T1"
$PM create steptool "Garden"  "Lumber"   "Saw"
$PM create steptool "Garden"  "Assemble" "Drill"

echo "===== GET PROJECTS BY NAME ====="
$PM get project "Kitchen"
$PM get project "Garden"
$PM get project "Garage"

echo "===== GET BY ID ====="
$PM get project "$P1"
$PM get area "$A1"
$PM get tool "$T1"

echo "===== GET PROJECT AREAS BY PROJECT (name and id) ====="
$PM list projectarea "Kitchen"
$PM list projectarea "$P2"
$PM list projectarea "Garage"
$PM get projectarea "Kitchen" "Indoor"
$PM get projectarea "$P3" "$A3"

echo "===== GET PROJECT AREAS BY AREA ====="
$PM list projectarea "Indoor"
$PM list projectarea "$A2"
$PM list projectarea "Workshop"

echo "===== GET EACH PROJECT STEP ====="
$PM get step "Kitchen" "Demo"
$PM get step "Kitchen" "Plumbing"
$PM get step "Kitchen" "Install"
$PM get step "Garden"  "Lumber"
$PM get step "$P2"     "$S5"
$PM get step "Garage"  "Sort"

echo "===== LIST STEPS PER PROJECT ====="
$PM list step "Kitchen"
$PM list step "$P2"
$PM list step "Garage"

echo "===== GET / LIST PROJECT STEP TOOLS ====="
$PM get steptool "Kitchen" "Demo" "Saw"
$PM get steptool "$P2" "$S5" "$T1"
$PM list steptool "Kitchen"
$PM list steptool "Garden" "Lumber"

echo "===== DELETE (links and steps first, then projects) ====="
$PM delete steptool "Kitchen" "Demo"     "Saw"
$PM delete steptool "Kitchen" "Plumbing" "Wrench"
$PM delete steptool "$P1"     "$S3"       "$T1"
$PM delete steptool "Garden"  "Lumber"   "Saw"
$PM delete steptool "Garden"  "Assemble" "Drill"
$PM delete projectarea "$P1" "$A1"
$PM delete projectarea "$P2" "$A2"
$PM delete projectarea "$P3" "$A3"
$PM delete projectarea "$P3" "$A1"
for id in "$S1" "$S2" "$S3" "$S4" "$S5" "$S6"; do $PM delete step "$id"; done
for id in "$P1" "$P2" "$P3"; do $PM delete project "$id"; done
for id in "$A1" "$A2" "$A3"; do $PM delete area "$id"; done
for id in "$T1" "$T2" "$T3"; do $PM delete tool "$id"; done
