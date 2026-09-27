"""Guide length arithmetic, not a load, accuracy or installed-fit qualification."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BLOCK_LENGTH = 45.4
MAX_BLOCK_LENGTH = 45.8
PITCH = 80.0
END_ALLOWANCE = 10.0
TARGET_STROKE = 200.0
SOURCE = 'https://www.hiwin.de/en/Products/Linear-guideways/Blocks/Miniature-guides/MGN-HIRES-series/MGN12HZ1CM/p/MGN12HZ1CM'

def main():
    examples = []
    for count in (1, 2):
        group_length = MAX_BLOCK_LENGTH + (count-1)*PITCH
        for rail in (200.0, 300.0, 350.0):
            travel = rail-group_length-2*END_ALLOWANCE
            examples.append(dict(blocks_per_rail=count, rail_length_mm=rail,
                                 occupied_block_span_mm=group_length,
                                 available_travel_mm=round(travel, 3),
                                 accommodates_200mm_travel=travel >= TARGET_STROKE))
    required = TARGET_STROKE+MAX_BLOCK_LENGTH+PITCH+2*END_ALLOWANCE
    result = {
        'scope': 'Guide/block packaging arithmetic using the catalog maximum block length. Stops, fittings, actuator and installation tolerances can increase length.',
        'manufacturer_block_length_mm': BLOCK_LENGTH,
        'manufacturer_maximum_block_length_mm': MAX_BLOCK_LENGTH,
        'manufacturer_source': SOURCE,
        'maximum_envelope_source': 'https://www.hiwin.com/wp-content/uploads/HIWIN-Linear-Guideway-Catalog.pdf#page=91',
        'maximum_envelope_reference': 'Printed page88, section2-4-19, revisionG99TE24-2410; note3 includes screws and end-seal lips.',
        'source_checked': '2026-09-26',
        'design_assumptions': {'two_block_center_pitch_mm': PITCH,
                               'end_allowance_each_mm': END_ALLOWANCE,
                               'target_useful_stroke_mm': TARGET_STROKE},
        'two_block_minimum_nominal_rail_length_mm': round(TARGET_STROKE+BLOCK_LENGTH+PITCH+2*END_ALLOWANCE, 3),
        'two_block_minimum_rail_using_maximum_block_length_mm': round(required, 3),
        'illustrative_rail_length_mm': 350,
        'examples': examples,
        'guide_selected_for_purchase': False,
        'load_capacity_qualified': False,
        'mechanical_design_released': False,
        'source_sha256': {'variants/retractable-atc/check_guide_stroke.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'passed': abs(required-345.8) < 1e-9 and len(examples) == 6,
    }
    (HERE/'guide-stroke-check.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'minimum_rail_mm': required, 'examples': examples, 'passed': result['passed']}))
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
