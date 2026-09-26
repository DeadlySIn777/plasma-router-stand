"""Draw why the Y guide rail is longer than the 1,000 mm stroke, from GM1 Rev H model positions.

Positions come from motion_details.make_motion at gantry_y = 275 (front stop) and
1275 (back stop); see rail-length-positions.json. Horizontal is to scale; the
vertical is a schematic side view, stretched so the parts are visible.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

HERE = Path(__file__).resolve().parent
POS = json.loads((HERE / 'rail-length-positions.json').read_text(encoding='utf-8'))
FRONT, BACK = POS['275.0'], POS['1275.0']
Y = lambda part, state, k: state[part][1 if k == 0 else 4]

RAIL, BLOCK, GHOST, BODY, MOTOR, CARR, INK = '#6b7780', '#d98c1f', '#d98c1f', '#c3c9ce', '#3a3f44', '#2f6fb3', '#1f2a30'


def box(ax, y0, y1, z0, z1, color, **kw):
    ax.add_patch(Rectangle((y0, z0), y1 - y0, z1 - z0, facecolor=color, edgecolor=kw.pop('edge', INK), lw=kw.pop('lw', 1.2), **kw))


def dim(ax, y0, y1, z, text, above=True, color=INK, size=13, weight='normal'):
    ax.add_patch(FancyArrowPatch((y0, z), (y1, z), arrowstyle='<|-|>', mutation_scale=14, lw=1.4, color=color))
    ax.text((y0 + y1) / 2, z + (3 if above else -3), text, ha='center', va='bottom' if above else 'top', fontsize=size, color=color, weight=weight)


def machine(ax, state, title):
    # Guide rail with its two bearing blocks.
    box(ax, *[Y('Y_RAIL_L', state, k) for k in (0, 1)], 0, 8, RAIL)
    for b in ('Y_BLOCK_L_1', 'Y_BLOCK_L_2'):
        box(ax, Y(b, state, 0), Y(b, state, 1), -4, 12, BLOCK)
    # HMS40 drive module above: motor, bracket, body, carriage.
    box(ax, Y('HMS_Y_L_MOTOR', state, 0), Y('HMS_Y_L_MOTOR', state, 1), 30, 43, MOTOR)
    box(ax, Y('HMS_Y_L_MOTOR_BRACKET', state, 0), Y('HMS_Y_L_MOTOR_BRACKET', state, 1), 30, 46, '#8a939a')
    box(ax, Y('HMS_Y_L_BODY', state, 0), Y('HMS_Y_L_BODY', state, 1), 30, 44, BODY)
    box(ax, Y('HMS_Y_L_CARRIAGE_TOP', state, 0), Y('HMS_Y_L_CARRIAGE_TOP', state, 1), 44, 52, CARR)
    ax.set_title(title, loc='left', fontsize=16, weight='bold', color=INK)
    ax.set_xlim(-10, 1470); ax.set_ylim(-44, 68)
    ax.set_yticks([]); ax.spines[['left', 'right', 'top']].set_visible(False)


fig, (a, b) = plt.subplots(2, 1, figsize=(15, 9.6), dpi=120, sharex=True)
fig.suptitle('Why the guide rail is longer than the 1,000 mm stroke (GM1, Y axis, left side)', fontsize=19, weight='bold', color=INK, y=0.985)

# --- Front stop.
machine(a, FRONT, 'Gantry at the FRONT stop')
r0, r1 = Y('Y_RAIL_L', FRONT, 0), Y('Y_RAIL_L', FRONT, 1)
f0, f1 = Y('Y_BLOCK_L_1', FRONT, 0), Y('Y_BLOCK_L_2', FRONT, 1)
dim(a, r0, r1, -33, f'guide rail: {r1 - r0:,.0f} mm (a 1,500 mm rail cut down)', above=False, size=14, weight='bold')
dim(a, f0, f1, -15, f'2 blocks span {f1 - f0:.1f} mm', above=False, color='#9a5b06')
dim(a, r0, f0, -15, f'{f0 - r0:.0f} mm spare\n(front stop)', above=False, size=11)
a.text(f1 + 14, 21, 'gantry bearing blocks (HGH20CA) ride on the HGR20 guide rail', fontsize=12, color='#9a5b06', va='center')
a.text(700, 37, 'HMS40 1000 mm module: only pushes the gantry', fontsize=12, color=INK, ha='center', va='center')
a.text(Y('HMS_Y_L_CARRIAGE_TOP', FRONT, 1) + 10, 49, 'carriage', fontsize=11, color=CARR, va='center')
a.text(47, 49, 'motor', fontsize=11, color=MOTOR, ha='center')
m0, m1 = Y('HMS_Y_L_MOTOR_BRACKET', FRONT, 0), Y('HMS_Y_L_BODY', FRONT, 1)
dim(a, m0, m1, 57, f'module body {m1 - m0:,.0f} mm long for a 1,000 mm stroke (L = S + 145), plus the motor', size=12)

# --- Back stop, with the front positions ghosted.
machine(b, BACK, 'Gantry at the BACK stop')
for blk in ('Y_BLOCK_L_1', 'Y_BLOCK_L_2'):
    box(b, Y(blk, FRONT, 0), Y(blk, FRONT, 1), -4, 12, 'none', edge=GHOST, lw=1.4, linestyle='--')
bf0, bb0, bb1 = Y('Y_BLOCK_L_1', FRONT, 0), Y('Y_BLOCK_L_1', BACK, 0), Y('Y_BLOCK_L_2', BACK, 1)
dim(b, bf0, bb0, 19, f'blocks travel {bb0 - bf0:,.0f} mm = the stroke', size=14, weight='bold', color='#9a5b06')
dim(b, bb1, r1, -15, f'{r1 - bb1:.0f} mm\nspare', above=False, size=11)
c0, c1 = Y('HMS_Y_L_CARRIAGE_TOP', FRONT, 0), Y('HMS_Y_L_CARRIAGE_TOP', BACK, 0)
box(b, Y('HMS_Y_L_CARRIAGE_TOP', FRONT, 0), Y('HMS_Y_L_CARRIAGE_TOP', FRONT, 1), 44, 52, 'none', edge=CARR, lw=1.4, linestyle='--')
dim(b, c0, c1, 57, f'HMS40 carriage travels {c1 - c0:,.0f} mm', size=12, color=CARR)
b.text(700, -30, 'Rail needed = 1,000 travel + 257.5 block span = 1,257.5 mm minimum. A 1,000 mm rail would let the blocks run off the end.\n'
       'X works the same way: 800 travel + 237.5 block span = 1,037.5 mm minimum; the X rails are 1,200 mm (the full gantry beam).',
       fontsize=12.5, color=INK, ha='center', va='center',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='#f3f6f8', edgecolor='#aab4bb'))
b.set_xlabel('position along the machine, mm  (front of machine at 0, back at 1,450; horizontal to scale, heights not to scale)', fontsize=12)
b.set_xticks(range(0, 1451, 250))
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(HERE / 'rail-length-explained.png', facecolor='white')
print('wrote', HERE / 'rail-length-explained.png')
