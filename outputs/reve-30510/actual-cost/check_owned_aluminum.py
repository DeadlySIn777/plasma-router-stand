import json
from pathlib import Path
from itertools import combinations

out=Path("plasma_router_stand/outputs/reve-30510/actual-cost")
stock_area=304.8**2
owned_half=[
 {"part":"Z_CARRIER","quantity":1,"x_mm":10,"y_mm":10,"width_mm":260,"height_mm":170.2,"finished_thickness_mm":12.7,"status":"Existing guarded part; final Z module holes remain unresolved"},
 {"part":"TOOL_INTERFACE_HOLD","quantity":1,"x_mm":10,"y_mm":186.2,"width_mm":110,"height_mm":70,"finished_thickness_mm":12.7,"status":"Existing guarded interface blank; final Z output pattern unresolved"},
 {"part":"HMS40_DRIVE_SHOE_6p35_A","quantity":1,"x_mm":126,"y_mm":186.2,"width_mm":65,"height_mm":48,"finished_thickness_mm":6.35,"status":"Mill down from nominal12.7 to6.35"},
 {"part":"HMS40_DRIVE_SHOE_6p35_B","quantity":1,"x_mm":197,"y_mm":186.2,"width_mm":65,"height_mm":48,"finished_thickness_mm":6.35,"status":"Mill down from nominal12.7 to6.35"}]
third_candidates=[
 {"part":"X_LINK_FLANGE redesign blank","x_mm":10,"y_mm":10,"width_mm":156,"height_mm":120.8,"finished_thickness_mm":6.35},
 {"part":"X_LINK_WEB redesign blank","x_mm":10,"y_mm":136.8,"width_mm":156,"height_mm":30,"finished_thickness_mm":8},
 {"part":"Y_LINK_FLANGE_L redesign blank","x_mm":172,"y_mm":10,"width_mm":103.1,"height_mm":32,"finished_thickness_mm":6.35},
 {"part":"Y_LINK_FLANGE_R redesign blank","x_mm":172,"y_mm":48,"width_mm":103.1,"height_mm":32,"finished_thickness_mm":6.35},
 {"part":"Y_LINK_WEB_L redesign blank","x_mm":172,"y_mm":86,"width_mm":32,"height_mm":40,"finished_thickness_mm":8},
 {"part":"Y_LINK_WEB_R redesign blank","x_mm":210,"y_mm":86,"width_mm":32,"height_mm":40,"finished_thickness_mm":8}]
def check(parts):
 for p in parts:
  assert p["x_mm"]>=10 and p["y_mm"]>=10
  assert p["x_mm"]+p["width_mm"]<=304.8-10+1e-6
  assert p["y_mm"]+p["height_mm"]<=304.8-10+1e-6
 for a,b in combinations(parts,2):
  assert a["x_mm"]+a["width_mm"]+6<=b["x_mm"]+1e-6 or b["x_mm"]+b["width_mm"]+6<=a["x_mm"]+1e-6 or a["y_mm"]+a["height_mm"]+6<=b["y_mm"]+1e-6 or b["y_mm"]+b["height_mm"]+6<=a["y_mm"]+1e-6
 area=sum(p["width_mm"]*p["height_mm"] for p in parts)
 return {"edge_clearance_mm":10,"minimum_rectangular_gap_mm":6,"rectangular_fit_checks_pass":True,"net_rectangle_area_mm2":round(area,4),"gross_sheet_area_mm2":stock_area,"net_area_fraction":area/stock_area,"scope":"2D bounding-rectangle nesting only; not machining-access, joint-strength or release validation"}
data={
 "date":"2026-09-24",
 "source":"User reports owned aluminum1/2 and3/8; subsequently reports12x12in size. One plate of each thickness is provisional, not confirmed quantity.",
 "quantity_assumption_requires_confirmation":True,
 "reported_size_inches":[12,12],
 "owned_plates":[
  {"thickness_inches":0.5,"nominal_thickness_mm":12.7,"width_mm":304.8,"height_mm":304.8,"quantity_assumed":1,"alloy":"unknown","temper":"unknown","usable_actual_thickness_and_flatness":"unverified","proposed_allocations":owned_half,"fit":check(owned_half)},
  {"thickness_inches":0.375,"nominal_thickness_mm":9.525,"width_mm":304.8,"height_mm":304.8,"quantity_assumed":1,"alloy":"unknown","temper":"unknown","usable_actual_thickness_and_flatness":"unverified","proposed_allocations":[],"optional_redesign_envelopes":third_candidates,"fit_of_optional_redesign_envelopes":check(third_candidates),"warning":"No current unchanged aluminum part is9.525mm thick. Separate-plate link supports require engineered joints, extra fasteners and clearance checks. This nest proves only stock fit; it does not replace integral bracket definitions."}],
 "conditional_avoidable_purchase":{
   "line_id":"MET08","item":"6061-T6511 1/2x8x12in raw blank forZ_CARRIER",
   "goods_credit_usd":58.74,
   "shipping_credit_usd":None,
   "status":"Conditional owned-material option; not applied to frozen baseline by this report",
   "conditions":["Confirm owned material suitable for the design load and threads; current target6061-T6/T651-type properties","Measure actual usable thickness and flatness; nominal12.7raw has no guaranteed datum cleanup allowance","Confirm one owned304.8x304.8plate is available","Do not release Z holes until actual module interface is verified"],
   "fallback":"Buy MET08 standalone raw blank if owned plate is unsuitable or unavailable; do not count both owned stock and purchased blank.",
   "other_allocations_credit_usd":0,
   "no_double_count_reason":"Tool interface and two6.35mm shoes are already nested intoMET07offcuts; moving them to owned plate does not eliminate the1200mm guide-face stock purchase."
 },
 "baseline_or_cad_edited":False,
 "orders_or_supplier_contacts":False
}
(out/"OWNED-ALUMINUM-INVENTORY.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"half_fit":check(owned_half),"three_eighth_candidate_fit":check(third_candidates)},indent=2))

