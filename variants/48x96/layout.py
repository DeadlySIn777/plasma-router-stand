"""Independent full-sheet hybrid layout. All dimensions are millimeters.

This is a parametric packaging model, not a released fabrication assembly.
Purchased axes, drives, dock hardware and ATC are explicit allocations without
manufacturer mounting holes. Frozen Rev I sources are neither imported nor edited.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json, math, os, sys
import cadquery as cq

OUT=Path(__file__).resolve().parent
STEEL=(.19,.27,.29); ALU=(.69,.74,.76); HDPE=(.88,.88,.84)
WET=(.24,.44,.56); RESERVE=(.91,.53,.15); MAGAZINE=(.55,.37,.70)

@dataclass(frozen=True)
class Parameters:
    frame_x:float=1950.
    frame_y:float=2950.
    tube_side:float=50.8
    tube_wall:float=3.048
    sheet_x:float=1219.2
    sheet_y:float=2438.4
    sheet_origin_x:float=180.
    sheet_origin_y:float=230.
    deck_x:float=1320.
    deck_y:float=2550.
    deck_origin_x:float=130.
    deck_origin_y:float=175.
    columns:int=3
    rows:int=6
    panel_gap:float=2.
    wear_thickness:float=12.7
    backing_thickness:float=6.35
    carrier_height:float=38.1
    carrier_width:float=25.4
    carrier_wall:float=3.175
    dock_height:float=26.
    grid_height:float=101.6
    wear_top_z:float=912.7
    surfacing_radius:float=12.7
    pan_inner_x:float=1360.
    pan_inner_y:float=2590.
    pan_origin_x:float=110.
    pan_origin_y:float=155.
    pan_floor_bottom_z:float=650.
    pan_sheet:float=2.
    pan_wall_top_z:float=720.
    water_depth:float=50.
    slat_top_z:float=710.
    gantry_tool_y_offset:float=100.
    gantry_y:float=2100.
    tool_x:float=780.
    tank_x:float=450.
    tank_y:float=1500.
    tank_height:float=400.
    tank_working_litres:float=230.

@dataclass
class Part:
    name:str
    shape:object
    group:str
    material:str
    color:tuple
    status:str='LAYOUT ONLY: joints, tolerances and strength not released'
    note:str=''

def box(x,y,z):return cq.Workplane('XY').box(x,y,z,centered=False).val()
def bounds(shape):
    b=shape.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def tube(length,width,height,wall):
    return box(length,width,height).cut(box(length+2,width-2*wall,height-2*wall).translate((-1,wall,wall))).clean()
def along(shape,origin,direction,width_axis):
    u=cq.Vector(*direction).normalized();v=cq.Vector(*width_axis).normalized()
    return shape.moved(cq.Plane(origin=origin,xDir=u,normal=u.cross(v)).location)

def dimensions(p):
    pw=(p.deck_x-(p.columns-1)*p.panel_gap)/p.columns
    pl=(p.deck_y-(p.rows-1)*p.panel_gap)/p.rows
    carrier_under=p.wear_top_z-p.wear_thickness-p.backing_thickness-p.carrier_height
    return dict(panel_x=pw,panel_y=pl,carrier_under_z=carrier_under,
                grid_top_z=carrier_under-p.dock_height,wear_bottom_z=p.wear_top_z-p.wear_thickness,
                tool_centers_x=[p.deck_origin_x-p.surfacing_radius,1800.],
                tool_centers_y=[p.deck_origin_y-p.surfacing_radius,p.deck_origin_y+p.deck_y+p.surfacing_radius],
                sheet_bounds=[p.sheet_origin_x,p.sheet_origin_y,p.sheet_origin_x+p.sheet_x,p.sheet_origin_y+p.sheet_y],
                deck_bounds=[p.deck_origin_x,p.deck_origin_y,p.deck_origin_x+p.deck_x,p.deck_origin_y+p.deck_y])

def build(p=Parameters(),state='router',allocations=True):
    assert state in ('router','plasma_layout')
    d=dimensions(p);parts=[];s=p.tube_side;w=p.tube_wall
    def add(name,shape,group,material,color,note='',status=None):
        parts.append(Part(name,shape,group,material,color,status or 'LAYOUT ONLY: joints, tolerances and strength not released',note))
    def block(name,xyz,origin,group='frame',material='steel',color=STEEL,**kw):
        add(name,box(*xyz).translate(origin),group,material,color,**kw)
    def member(name,length,origin,axis=(1,0,0),width_axis=(0,1,0),group='frame',material='steel',color=STEEL):
        if axis==(0,1,0) and width_axis==(1,0,0):
            origin=(origin[0]+s,origin[1],origin[2]);width_axis=(-1,0,0)
        add(name,along(tube(length,s,s,w),origin,axis,width_axis),group,material,color,
            'Nominal sharp-corner 50.8 mm tube. Actual salvage wall, grade, straightness and corrosion must be measured.')
    stations=(100.,1000.,1900.,2850.)
    # Four supports per long side; open front portal above the low crossmember.
    for side,xc in (('L',75.),('R',p.frame_x-75.)):
        for i,y in enumerate(stations,1):
            member(f'LEG_{side}_{i}',829.2,(xc-s/2,y-s/2,20),(0,0,1),(1,0,0))
            block(f'FOOT_{side}_{i}',(100,100,12.7),(xc-50,y-50,7.3),group='feet',note='Plain fabricated base allocation; anchors/levelers not selected.')
        member(f'SIDE_{side}_UPPER',2900.,(xc-s/2,25.,849.2),(0,1,0),(1,0,0))
        for i,(ya,yb) in enumerate(zip(stations,stations[1:]),1):
            member(f'SIDE_{side}_LOWER_{i}',yb-ya-s,(xc-s/2,ya+s/2,549.2),(0,1,0),(1,0,0))
        # Alternating diagonals are trimmed to the two chord faces, with no
        # made-up weld or bolt detail. Posts remain separate fabricated tubes.
        for i,(ya,yb) in enumerate(zip(stations,stations[1:]),1):
            rising=i%2==1;za,zb=(575.,875.) if rising else (875.,575.)
            delta=cq.Vector(0,yb-ya,zb-za);length=delta.Length
            raw=along(tube(length,s,s,w).translate((0,-s/2,-s/2)),(xc,ya,za),delta.toTuple(),(1,0,0))
            clip=box(s,yb-ya-s,249.2).translate((xc-s/2,ya+s/2,600.))
            add(f'SIDE_{side}_DIAGONAL_{i}',raw.intersect(clip).clean(),'frame','steel',STEEL,'Chord-face trimmed layout. Weld design and residual distortion unqualified.')
    pan_stations=(130.,555.,980.,1405.,1830.,2255.,2680.)
    for side,lx in (('L',100.4),('R',1798.8)):
        member(f'PAN_BEARER_{side}',2750.,(lx,100.,p.pan_floor_bottom_z-s),(0,1,0),(1,0,0))
        for i,y in enumerate(stations):
            blockx=100.4 if side=='L' else 1798.8
            member(f'PAN_BEARER_SEAT_{side}_{i}',s,(blockx,y-25.4,p.pan_floor_bottom_z-2*s))
    for i,y in enumerate(pan_stations,1):
        member(f'PAN_CROSS_{i}',1647.6,(151.2,y-25.4,p.pan_floor_bottom_z-s))
    for i,y in enumerate((100.,1000.,1900.,2850.),1):
        member(f'LOW_CROSS_{i}',1749.2,(100.4,y-25.4,99.2))
    # A vented catch pan; a pressure vessel is deliberately not implied.
    x,y=p.pan_origin_x,p.pan_origin_y;t=p.pan_sheet;px,py=p.pan_inner_x,p.pan_inner_y
    floor=p.pan_floor_bottom_z;top=floor+t;h=p.pan_wall_top_z-top
    block('PAN_FLOOR',(px+2*t,py+2*t,t),(x-t,y-t,floor),'wet_pan','steel',WET)
    block('PAN_LEFT',(t,py+2*t,h),(x-t,y-t,top),'wet_pan','steel',WET)
    block('PAN_RIGHT',(t,py+2*t,h),(x+px,y-t,top),'wet_pan','steel',WET)
    block('PAN_FRONT',(px,t,h),(x,y-t,top),'wet_pan','steel',WET)
    block('PAN_REAR',(px,t,h),(x,y+py,top),'wet_pan','steel',WET)
    # Slats are always below the removable grid. No unmodeled hydraulic lift.
    for i in range(25):
        sy=190.+i*104.
        block(f'SLAT_{i+1:02}',(1240.,3.,50.),(170.,sy,p.slat_top_z-50.),'plasma_slats','steel',STEEL,
              note='Replaceable plain slat layout; actual slat rack/notches and consumable maintenance remain to detail.')
    # Removable paired beams; full supplier docking details live in the common
    # dock module, not in invented hole patterns in this allocation assembly.
    gridz=d['grid_top_z'];beam_y=[p.deck_origin_y+i*(d['panel_y']+p.panel_gap) for i in range(p.rows+1)]
    beam_y[-1]=p.deck_origin_y+p.deck_y
    for i,cy in enumerate(beam_y):
        shape=tube(p.deck_x,s,p.grid_height,w)
        if state=='router':shape=shape.translate((p.deck_origin_x,cy-s/2,gridz-p.grid_height))
        else:
            # Four-by-two rectangular beams store in individual horizontal
            # slots, their long dimension along Y. No composite weld credit.
            shape=along(shape,(1510.+(i%3)*110.,400.,180.+(i//3)*65.),(0,1,0),(0,0,1))
        add(f'GRID_BEAM_{i+1}',shape,'removable_grid','steel',STEEL,
            '101.6x50.8x3.048 RHS on edge; optional new stock distinct from2x2 chassis. End captures and panel dock lugs are not integrated.')
    for side,lx in (('L',115.),('R',1414.2)):
        ledger_bottom=gridz-p.grid_height-s
        member(f'GRID_LEDGER_{side}',2580.,(lx,160.,ledger_bottom),(0,1,0),(1,0,0),'grid_support')
        for i,yy in enumerate(pan_stations[1:]):
            px=110. if side=='L' else 1370.
            block(f'GRID_LOAD_PAD_{side}_{i}',(100.,100.,6.35),(px,yy-50.,top),'grid_support',note='Load-spreading pad over actual pan cross/bearer lines; weld and local plate qualification remains.')
            height=ledger_bottom-(top+6.35)
            member(f'GRID_POST_{side}_{i}',height,(lx,yy-25.4,top+6.35),(0,0,1),(1,0,0),'grid_support')
    # Carrier frame: 38.1 x25.4 x3.175 aluminum rectangular tube,6.35 backing.
    pw,pl=d['panel_x'],d['panel_y'];tw=p.carrier_width;th=p.carrier_height;aw=p.carrier_wall
    for row in range(p.rows):
        for col in range(p.columns):
            n=row*p.columns+col+1;ox=p.deck_origin_x+col*(pw+p.panel_gap);oy=p.deck_origin_y+row*(pl+p.panel_gap)
            local=[]
            def local_member(label,length,ori,axis=(1,0,0),width_axis=(0,1,0)):
                if axis==(0,1,0) and width_axis==(1,0,0):
                    ori=(ori[0]+tw,ori[1],ori[2]);width_axis=(-1,0,0)
                local.append((label,along(tube(length,tw,th,aw),ori,axis,width_axis)))
            local_member('FRONT',pw,(0,0,0));local_member('REAR',pw,(0,pl-tw,0))
            for label,lx in (('LEFT',0),('RIGHT',pw-tw)):
                local_member(label,pl-2*tw,(lx,tw,0),(0,1,0),(1,0,0))
            for k in (1,2):local_member(f'RIB{k}',pw-2*tw,(tw,k*(pl-tw)/3,0))
            local.append(('BACKING',box(pw,pl,p.backing_thickness).translate((0,0,th))))
            for label,shape in local:
                if state=='router':world=shape.translate((ox,oy,d['carrier_under_z']))
                else:
                    # Slot poses are packaging only; no checked insertion route
                    # or retention latch is inferred from these final poses.
                    world=along(shape,(170.,280.+(n-1)*60.,160.),(1,0,0),(0,0,1))
                add(f'PANEL_{n:02}_{label}',world,'aluminum_carriers','aluminum',ALU,'Dock hardware, clamps and fastening remain supplied by common interface study.')
            wear=box(pw,pl,p.wear_thickness)
            if state=='router':wear=wear.translate((ox,oy,d['wear_bottom_z']))
            else:wear=along(wear,(660.,280.+(n-1)*17.,160.),(1,0,0),(0,0,1))
            add(f'HDPE_{n:02}',wear,'wear_panels','HDPE',HDPE,'Floating expansion attachments and cut-through screw avoidance are unresolved until common dock integration.')
    # Vented reservoir: theoretical internal gross volume270L,230L working.
    rx,ry,rz=1000.,1000.,170.+t;tx,ty,th=p.tank_x,p.tank_y,p.tank_height
    block('RESERVOIR_FLOOR',(tx+2*t,ty+2*t,t),(rx-t,ry-t,rz-t),'reservoir','steel',WET)
    for label,sz,ori in [('LEFT',(t,ty+2*t,th),(rx-t,ry-t,rz)),('RIGHT',(t,ty+2*t,th),(rx+tx,ry-t,rz)),
                         ('FRONT',(tx,t,th),(rx,ry-t,rz)),('REAR',(tx,t,th),(rx,ry+ty,rz))]:
        block('RESERVOIR_'+label,sz,ori,'reservoir','steel',WET,note='Open/vented storage only. Support, drain/refill, cleanout and level details not yet engineered.')
    def small_member(name,length,origin,axis=(1,0,0),width_axis=(0,1,0)):
        if axis==(0,1,0) and width_axis==(1,0,0):
            origin=(origin[0]+20.,origin[1],origin[2]);width_axis=(-1,0,0)
        add(name,along(tube(length,20.,20.,2.),origin,axis,width_axis),'reservoir_stiffeners','steel',STEEL,
            '20x20x2mm tube layout;225mm maximum wall cell pitch. Weld/buckling/corrosion qualification still required.')
    ys=(1000.,1225.,1450.,1675.,1900.,2125.,2350.,2500.)
    for i,xx in enumerate((990.,1215.,1440.)):
        small_member(f'TANK_BOTTOM_LONG_{i}',1540.,(xx,980.,150.),(0,1,0),(1,0,0))
    for i,yy in enumerate(ys):
        for j,xx in enumerate((1010.,1235.)):
            small_member(f'TANK_BOTTOM_CROSS_{i}_{j}',205.,(xx,yy-10.,150.))
    for side,xx in (('L',978.),('R',1452.)):
        for i,yy in enumerate(ys):
            small_member(f'TANK_WALL_POST_{side}_{i}',th,(xx,yy-10.,rz),(0,0,1),(1,0,0))
        for i,(ya,yb) in enumerate(zip(ys,ys[1:])):
            small_member(f'TANK_WALL_MID_{side}_{i}',yb-ya-20.,(xx,ya+10.,rz+225.),(0,1,0),(1,0,0))
    for end,yy in (('FRONT',978.),('REAR',2502.)):
        for i,xx in enumerate((1000.,1215.,1430.)):
            small_member(f'TANK_END_POST_{end}_{i}',th,(xx,yy,rz),(0,0,1),(1,0,0))
        for i,xx in enumerate((1020.,1235.)):
            small_member(f'TANK_END_MID_{end}_{i}',195.,(xx,yy,rz+225.))
    # Actual side truss carries a rail preparation strip, with purchased
    # allocations kept visually and computationally distinct from fabrication.
    for side,xc in (('L',75.),('R',p.frame_x-75.)):
        block(f'RAIL_PREP_{side}',(80.,2890.,8.),(xc-40,40.,900.),'rail_preparation','steel',STEEL,
              note='Plain weld/machine allowance. Rail model and hole pattern unselected.')
    gy=p.gantry_y
    for z,zname in ((1150.,'LOW'),(1350.,'HIGH')):
        for yy,yname in ((gy-50.8,'FRONT'),(gy,'REAR')):
            member(f'GANTRY_{zname}_{yname}',1800.,(75.,yy,z),group='gantry')
    for k,xc in enumerate((100.,650.,1200.,1824.2)):
        for j,yy in enumerate((gy-50.8,gy)):
            member(f'GANTRY_POST_{k}_{j}',149.2,(xc,yy,1200.8),(0,0,1),(1,0,0),'gantry')
    for side,lx in (('L',49.6),('R',1849.6)):
        member(f'GANTRY_TOWER_{side}',175.,(lx,gy-25.4,975.),(0,0,1),(1,0,0),'gantry')
    if allocations:
        def reserve(name,sz,ori,group='motion_allocations',color=RESERVE,note=''):
            block(name,sz,ori,group,'allocation only',color,note=note,status='UNSELECTED INTERFACE / NOT A PURCHASED-PART MODEL')
        for side,xc in (('L',75.),('R',p.frame_x-75.)):
            reserve(f'Y_RAIL_{side}',(25.,2890.,25.),(xc-12.5,40.,908.),note='25mm-class profiled rail allocation; supplier and loads not selected.')
            reserve(f'Y_CARRIAGE_{side}',(75.,180.,42.),(xc-37.5,gy-90.,933.),note='Dual block/adapter allocation, not a sourced bolt interface.')
            reserve(f'RACK_{side}',(20.,2830.,20.),((24. if side=='L' else 1906.),100.,870.),note='Segmented rack drive allocation. Pitch, reducer, preload and mesh are unselected.')
        reserve('X_AXIS',(1800.,30.,180.),(75.,gy-80.,1170.),note='Separated rail/drive space on deep fabricated beam; assumes80mm bearing-carriage width. Actual axis and section capacity not qualified.')
        reserve('Z_TOOL_PACKAGE',(100.,90.,410.),(p.tool_x-50.,gy-145.,930.),note='Unselected spindle/Z/holder package; no spindle-to-torch interchange proof.')
        reserve('ATC_MAGAZINE',(200.,600.,140.),(1600.,400.,800.),'atc_allocation',MAGAZINE,
                'RapidChange600x200 bay; exact product body, cover swing, pitch, mounting and tool lengths unconfirmed.')
    return parts,d

def calculations(p,d,parts):
    density={'steel':7.85e-6,'aluminum':2.7e-6,'HDPE':.95e-6}
    masses={}
    for a in parts:
        if a.material in density:masses[a.group]=masses.get(a.group,0)+a.shape.Volume()*density[a.material]
    tube_i=(p.tube_side**4-(p.tube_side-2*p.tube_wall)**4)/12
    rhs_i=(p.tube_side*p.grid_height**3-(p.tube_side-2*p.tube_wall)*(p.grid_height-2*p.tube_wall)**3)/12
    paired_area=2*(p.tube_side**2-(p.tube_side-2*p.tube_wall)**2)
    rhs_area=p.tube_side*p.grid_height-(p.tube_side-2*p.tube_wall)*(p.grid_height-2*p.tube_wall)
    screen=[]
    for minor in (16.,20.,25.,32.):
        for name,factor in [('supported-supported',9.7),('fixed-supported',15.1),('fixed-fixed',21.9)]:
            rpm=factor*minor/2900.**2*1e7
            screen.append(dict(minor_diameter_mm=minor,bearing_span_mm=2900.,mounting=name,permissible_rpm=rpm,
                               linear_m_min_at_10mm_lead=rpm*.01))
    water=p.pan_inner_x*p.pan_inner_y*p.water_depth/1e6
    return dict(nominal_group_mass_kg=masses,nominal_total_modeled_mass_kg=sum(masses.values()),
      mass_scope='Nominal fabricated solids only; no screws, motors, reduction drives, rack mechanisms, cables, welds, coolant/sludge, stock or ATC tools.',
      nominal_pan_water_litres=water,water_level_to_slat_top_mm=p.slat_top_z-(p.pan_floor_bottom_z+p.pan_sheet+p.water_depth),
      reservoir_gross_litres=p.tank_x*p.tank_y*p.tank_height/1e6,reservoir_working_litres=p.tank_working_litres,
      working_capacity_minus_pan_litres=p.tank_working_litres-water,
      flow_capacity_limit='Allocate remaining53.88L between wet-line inventory, heel/sludge and operational reserve; no hydraulic/overflow qualification.',
      tube_second_moment_mm4=tube_i,
      beam_screen={'load_N':500.,'simple_span_mm':1320.,'previous_two_parallel_tubes_deflection_mm':500*1320**3/(48*200000*tube_i*2),
                   'current_4x2_RHS_deflection_mm':500*1320**3/(48*200000*rhs_i),
                   'stiffness_ratio':rhs_i/(tube_i*2),'seven_beam_mass_previous_kg':paired_area*1320*7*7.85e-6,'seven_beam_mass_current_kg':rhs_area*1320*7*7.85e-6,
                   'scope':'Illustrative central load, ideal supports, nominal3.048mm wall; no joint, local wall, frame or whole-machine qualification. Not a completed tool-to-work stiffness budget.'},
      wet_sheet_screen={'thickness_mm':p.pan_sheet,'pan_water_head_mm':p.water_depth,'pan_support_pitch_mm':425.,
          'pan_one_way_strip_deflection_mm':5*(p.water_depth*9.81e-6)*425**4/(384*200000*(p.pan_sheet**3/12)),
          'pan_one_way_strip_bending_stress_MPa':(p.water_depth*9.81e-6)*425**2/(8*(p.pan_sheet**2/6)),
          'tank_wall_height_mm':p.tank_height,'tank_full_head_pressure_MPa':p.tank_height*9.81e-6,
          'tank_required_stiffener_pitch_mm':225.,
          'tank_strip_deflection_at_required_pitch_mm':5*(p.tank_height*9.81e-6)*225**4/(384*200000*(p.pan_sheet**3/12)),
          'scope':'One-way simply supported elastic strips, steelE200GPa, static water. Tank225mm stiffener grid is modeled; its welds and global frame stiffness remain unqualified. Corrosion allowance, weld distortion and leakage still require fabrication review.'},
      rotating_screw_screen=screen,
      screw_formula='THK N1=lambda2*d_minor/L^2*10^7 rpm; includes0.8 critical-speed safety factor. Root diameter is NOT nominal screw diameter. DN and bearing limits still apply.',
      racking_screen={'rail_center_spacing_mm':1800.,'one_side_error_mm':1.,'yaw_rad_small_angle':1/1800.,
                      'Y_error_difference_across_full_sheet_width_mm':p.sheet_x/1800.,
                      'scope':'Small-angle yaw from1mm side-to-side drive mismatch. The induced Y error varies across X, not with travel down the sheet. Not permissible skew; dual home switches do not detect every cutting stall.'},
      rack_illustration={'module_mm':2.,'pinion_teeth':20,'motor_to_pinion_ratio':3.,'travel_mm_per_motor_rev':math.pi*2*20/3,
                         'at600_motor_rpm_m_min':math.pi*2*20/3*600/1000,
                         'scope':'Arithmetic example only; not a selected rack, gear rating, motor torque or attainable feed.'})

def verify(p,d,parts):
    ids=[a.name for a in parts]
    x_axis=bounds(next(a.shape for a in parts if a.name=='X_AXIS'))
    checks={'unique_ids':len(ids)==len(set(ids)),
        'positive_valid_single_solids':all(a.shape.isValid() and len(a.shape.Solids())==1 and a.shape.Volume()>0 for a in parts),
        'all_static_bodies_inside_plan':all(bounds(a.shape)[0]>=-1e-5 and bounds(a.shape)[1]>=-1e-5 and bounds(a.shape)[3]<=p.frame_x+1e-5 and bounds(a.shape)[4]<=p.frame_y+1e-5 for a in parts),
        'deck_covers_sheet':d['deck_bounds'][0]<=d['sheet_bounds'][0] and d['deck_bounds'][1]<=d['sheet_bounds'][1] and d['deck_bounds'][2]>=d['sheet_bounds'][2] and d['deck_bounds'][3]>=d['sheet_bounds'][3],
        'carrier_width_sum':abs(d['panel_x']*p.columns+p.panel_gap*(p.columns-1)-p.deck_x)<1e-7,
        'carrier_length_sum':abs(d['panel_y']*p.rows+p.panel_gap*(p.rows-1)-p.deck_y)<1e-7,
        'nominal_grid_above_slats':d['grid_top_z']-p.grid_height>p.slat_top_z,
        'gantry_Y_extreme_allocation_inside':d['tool_centers_y'][1]+p.gantry_tool_y_offset+90.<p.frame_y and d['tool_centers_y'][0]+p.gantry_tool_y_offset-90.>0,
        'X_bearing_allocation_supports_stated_travel':d['tool_centers_x'][0]-40.>=x_axis[0] and d['tool_centers_x'][1]+40.<=x_axis[3],
        'ATC_tool_center_reachable':d['tool_centers_x'][0]<1700.<d['tool_centers_x'][1]}
    return dict(passed=all(checks.values()),checks=checks,
        scope='Solid validity, plan containment, coverage and named reach arithmetic only. NOT an all-pairs interference or in-motion conversion proof.',
        conversion_paths_verified=False,whole_machine_strength_qualified=False,supplier_interfaces_verified=False)

def main():
    p=Parameters();before=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();records={}
    for state in ('router','plasma_layout'):
        parts,d=build(p,state);verification=verify(p,d,parts)
        if not verification['passed']:raise AssertionError(verification)
        assy=cq.Assembly(name='FULL_SHEET_'+state.upper())
        for a in parts:assy.add(a.shape,name=a.name,color=cq.Color(*a.color))
        target=OUT/(state+'.step');assy.save(str(target),exportType='STEP',mode='default')
        reread=cq.importers.importStep(str(target)).val();expected=sum(a.shape.Volume() for a in parts)
        delta=abs(reread.Volume()-expected)
        assert reread.isValid() and len(reread.Solids())==len(parts) and delta<max(.2,expected*1e-7)
        records[state]=dict(verification=verification,part_count=len(parts),step_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            step_solid_count=len(reread.Solids()),step_volume_delta_mm3=delta,
            parts=[dict(name=a.name,group=a.group,material=a.material,status=a.status,note=a.note,bounds_mm=bounds(a.shape)) for a in parts])
        if state=='router':calc=calculations(p,d,parts)
        print(state,len(parts),'valid solids; STEP readback PASS',flush=True)
    after=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report=dict(status='PARAMETRIC LAYOUT ONLY',assumptions=['48x96in means usable full sheet; awaiting confirmation.','Aluminum framed carriers with independent HDPE wear panels; material choices provisional.',
        'In-footprint manual conversion is a requirement. Final storage poses are allocated; actual handling, restraint and service routes are not yet proved.',
        'Dock interval26mm includes lower support and12mm upperreceiver; pin projection above this plane requires a carrier pocket, not yet integrated.',
        '100mm-class originalZ is not silently scaled; large-machine spindle/ATC Z stroke and lengths remain to select.'],
        parameters=asdict(p),dimensions=d,calculations=calc,states=records,source_sha256={'layout.py':after},sources_unchanged=before==after,
        sources={'THK_critical_speed':'https://www.thk.com/us/en/products/ball_screw/selection/0007/',
                 'THK_formula_pdf':'https://tech.thk.com/en/products/pdf_download.php?file=E_15_BallScrew.pdf',
                 'Atlanta_racks':'https://atlantadrives.com/racks.htm',
                 'Atlanta_preload':'https://atlantadrives.com/systems1.htm'})
    (OUT/'layout-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('LAYOUT complete; physical release FALSE',flush=True)

if __name__=='__main__':
    try:main();code=0
    except Exception:
        import traceback;traceback.print_exc();code=1
    sys.stdout.flush();sys.stderr.flush();os._exit(code)
