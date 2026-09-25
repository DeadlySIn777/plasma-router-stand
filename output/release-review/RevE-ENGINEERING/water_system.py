"""Welded, permanently vented water-pan and reservoir fabrication geometry."""
import math
import cadquery as cq
from cad_helpers import *

T=3.048
PIPE_SOURCE='https://www.wheatland.com/wp-content/uploads/2017/12/Schedule-40-Submittal-Sheet.pdf'

def make_water(m):
    shift=30.0  # Approved front extraction well; reservoir and support stations stay fixed.
    # Normal-thickness floor, fabricated as a flat cut rectangle and installed at 1%.
    a=math.atan(.01);cs=math.cos(a);sn=math.sin(a)
    flen=1200/cs
    floor_holes=[(900-115,(1240-75)/cs,48.5),(180-115,(1240-75)/cs,48.5)]
    m.add_plate('WP_FLOOR',920,flen,T,holes=floor_holes,origin=(115,75+shift,747),v=(0,cs,-sn),
        group='water_pan',material='A36 steel 0.120in sheet',color=WATER,
        notes=['Install at 1% downward slope toward rear. Continuous watertight seam welds.',
               'Two48.5mmweldneckclearanceholes:drainand1.5instandpipe. No bend allowance required.',
               'Drain center is0.35mm above absolute rear floor edge; residual film requires cleaning.'])
    def top(y):return 735+.01*(1275+shift-y)+T/cs
    outline=[(0,top(75+shift)-735),(1200,top(1275+shift)-735),(1200,100),(0,100)]
    for i,x in enumerate((115,1035-T),1):
        m.add_plate('WP_SIDE_'+str(i),1200,100,T,outline=outline,origin=(x,75+shift,735),u=(0,1,0),v=(0,0,1),
                    pn='WP_SIDE',group='water_pan',color=WATER,notes=['Miter/fit lower seam to tilted floor; nominal corner weld gap<=0.1mm from 1% floor projection.'])
    for label,y in [('FRONT',75+shift+T),('REAR',1275+shift)]:
        bottom=top(y-T)
        m.add_plate('WP_END_'+label,920-2*T,835-bottom,T,origin=(115+T,y,bottom),u=(1,0,0),v=(0,0,1),
                    group='water_pan',color=WATER,notes=['Welded end plate; dress local 0.031mm slope mismatch before welding.'])
    # Standard nominal pipe geometry; threads are drawing callouts, not helical meshes.
    m.add('WP_DRAIN_NECK',pipe(45),origin=(900,1240+shift,top(1240+shift)-45),group='water_pan',material='NPS1.5 schedule40 steel pipe',color=WATER,
          length=45,notes=['OD48.3 ID40.9 per Wheatland schedule40 table. Flush upper end to floor; continuous weld.',
                           'Lower end:1.5 NPT male standard thread; match reducer/union to selected1in drain valve before plumbing assembly.',PIPE_SOURCE])
    m.add('WP_OVERFLOW_STANDPIPE',pipe(375,48.3,40.9),origin=(180,1240+shift,450),group='water_pan',material='NPS1.5 schedule40 steel pipe',color=WATER,
          length=375,notes=['Top edgeZ825 establishes pan overflow. Lower outletZ450 air-gaps above reservoir inlet.',PIPE_SOURCE])

    # Three independently mounted steel saddles. Their top profiles follow the floor.
    # Pan restraining lugs are separate from bed-support structure.
    for i,y in enumerate((175,675,1150),1):
        # Two transverse vertical webs provide line contact under the sloped floor.
        for j,yy in enumerate((y,y+44.8),1):
            h=735+.01*(1275+shift-(yy+6))-730
            m.add_plate(f'WP_CRADLE_WEB_{i}_{j}',900,h,6,origin=(125,yy+6,730),u=(1,0,0),v=(0,0,1),
                        group='pan_support',notes=['Weld web to bearer. Grind upper edge to measured floor slope; do not force-distort pan.'])
        # Four removable hold tabs per pan, outside working and bridge paths.
    for i,(x,bolt_x,y) in enumerate(((89,108,200.4),(1035,1042,200.4),(89,108,1175.4),(1035,1042,1175.4)),1):
        z=top(y-15)
        m.add_plate(f'WP_HOLD_TAB_{i}',26,30,6,holes=[(bolt_x-x,15,6.6)],origin=(x,y-15,z),
                    group='pan_support',notes=['Continuous6mm-side-edge weld to pan side. M6x40 restraint, not part of routing load path.'])
        spacer=pipe(z-730,12,6.6)
        m.add(f'WP_HOLD_SPACER_{i}',spacer,origin=(bolt_x,y,730),group='pan_support',length=z-730,
              notes=['Machined spacer between bearer top and pan tab. Seats without pulling pan out of shape.'])
        head=cyl(6,40).fuse(cyl(10,6).translate((0,0,40))).clean()
        m.add(f'WP_HOLD_BOLT_{i}',head,origin=(bolt_x,y,z+6-40),pn='STD_M6x40_SOCKET',group='fasteners',material='M6x40class8.8',purchased=True,color=HARDWARE)

    # Two combs receive all19 slats; comb feet are cut to the real sloping floor.
    # Each comb is a separate laser-cut plate, with slots down to theZ775 seating line.
    for i,x in enumerate((195,955),1):
        pts=[(0,top(100+shift)-735),(1120,top(1220+shift)-735),(1120,60)]
        for yy in reversed(list(range(120,1240,60))):
            c=yy+T/2-100;w=3.6
            pts.extend([(c+w/2,60),(c+w/2,40),(c-w/2,40),(c-w/2,60)])
        pts.extend([(0,60)])
        m.add_plate(f'WP_COMB_{i}',1120,60,6,outline=pts,origin=(x,100+shift,735),u=(0,1,0),v=(0,0,1),
                    pn='WP_COMB',group='slat_support',notes=['Continuous lower edge follows floor. Stitch weld to floor, alternating sides; slots3.6wide toZ775 seat.'])
    for i,y in enumerate(range(120,1240,60),1):
        m.add_plate(f'WP_SLAT_{i:02}',880,75,T,origin=(135,y+T+shift,775),u=(1,0,0),v=(0,0,1),
                    pn='WP_SLAT',group='slats',notes=['Replaceable loose slat;75height yields topZ850. No welding to comb.'])

    # Actual vented reservoir:900x600x250 INTERNAL dimensions, floor and walls3.048.
    x0,y0,z0=125,715,178.048
    ox,oy=121.952,711.952;ow,od=906.096,606.096
    walltop=z0+250;flange_z=walltop-6;gasket_z=walltop;lid_z=walltop+2;lidtop=lid_z+T
    m.add_plate('WT_FLOOR',ow,od,T,holes=[(900-ox,1260-oy,48.5),(500-ox,1270-oy,48.5)],origin=(ox,oy,175),
                group='reservoir',color=WATER,notes=['Weld continuously to all walls. Floor drain allows washout; permanently vented, never pressure/vacuum-rated.'])
    for name,x in [('LEFT',ox),('RIGHT',x0+900)]:
        m.add_plate('WT_SIDE_'+name,od,250,T,origin=(x,oy,z0),u=(0,1,0),v=(0,0,1),pn='WT_SIDE',group='reservoir',color=WATER)
    m.add_plate('WT_FRONT',900,250,T,origin=(x0,y0,z0),u=(1,0,0),v=(0,0,1),group='reservoir',color=WATER)
    rearholes=[(180-x0,25,21.5)]
    m.add_plate('WT_REAR',900,250,T,holes=rearholes,origin=(x0,y0+600+T,z0),u=(1,0,0),v=(0,0,1),group='reservoir',color=WATER,
                notes=['Rear port is the clarified pickup. The emergency overflow uses the separate internal standpipe through the floor.'])
    m.add_plate('WT_SETTLING_WEIR',900,50,T,holes=[(180-x0,25,21.5)],origin=(x0,1175+T,z0),u=(1,0,0),v=(0,0,1),
                group='reservoir',color=WATER,notes=['Weld bottom and sides;topZ228.048. Retainssettledmaterialwithouttrappingexcesswater.'])
    # Clarified pickup runs through sealed hole in settling weir to front compartment.
    m.add('WT_PICKUP_PIPE',pipe(608.048,21.3,15.8),origin=(180,750,z0+25),u=(1,0,0),v=(0,0,-1),
          group='reservoir',color=WATER,material='NPS0.5 schedule40 steel pipe',length=608.048,
          notes=['Axis+Y;open intake is25mm above internalfloor,inclarifiedfrontbay. Sealbafflepenetration.',
                 'Rearexternalend1/2NPTmale. Pumptripat55mmaboveinternalfloor.',PIPE_SOURCE])
    m.add('WT_EMERGENCY_OVERFLOW',pipe(292),origin=(500,1270,128.048),group='reservoir',color=WATER,material='NPS1.5 schedule40 steel pipe',length=292,
          notes=['Internal standpipe crest Z420.048,242mm above reservoir floor. Open outlet below tank atZ128.048 must route to a visible drain; never cap.',PIPE_SOURCE])
    m.add('WT_CLEANOUT_NECK',pipe(50),origin=(900,1260,128.048),group='reservoir',color=WATER,
          material='NPS1.5 schedule40 steel pipe',length=50,
          notes=['Flush upper end with inner floor; external lower end1.5NPT male for manual washout valve/cap. Keep accessible from rear.',PIPE_SOURCE])

    # External flat-bar rim, sealed gasket and bolt-on removable cover.
    lx,ly=ox-30,oy-30;lw,ld=ow+60,od+60
    global_bolts=[(x,y) for x in (120,350,575,800,1030) for y in (oy-15,oy+od+15)]
    global_bolts += [(x,y) for x in (ox-15,ox+ow+15) for y in (900,1065,1230)]
    for label,bx,by,w,h in [('FRONT',lx,ly,lw,30),('REAR',lx,oy+od,lw,30),('LEFT',lx,oy,30,od),('RIGHT',ox+ow,oy,30,od)]:
        holes=[(x-bx,y-by,6.6) for x,y in global_bolts if bx<x<bx+w and by<y<by+h]
        m.add_plate('WT_RIM_'+label,w,h,6,holes=holes,origin=(bx,by,flange_z),group='reservoir',color=WATER,
                    notes=['Continuous external wall weld. M6 weld nuts below each bolt hole; remove lid for tank washout.'])
    lidholes=[(x-lx,y-ly,6.6) for x,y in global_bolts]+[(180-lx,1240+shift-ly,55),(150-lx,850-ly,33.6)]
    hatch=[(817-lx,1177-ly),(983-lx,1177-ly),(983-lx,1303-ly),(817-lx,1303-ly)]
    m.add_plate('WT_GASKET',lw,ld,2,holes=lidholes[:-2],internal=[[(30,30),(30+ow,30),(30+ow,30+od),(30,30+od)]],
                origin=(lx,ly,gasket_z),group='reservoir',material='2mm EPDM gasket, compatible media required',color=(.12,.12,.12),
                notes=['Knife-cut; do not use metal laser program. Permanently vented cover, not a pressure seal.'])
    m.add_plate('WT_LID',lw,ld,T,holes=lidholes,internal=[hatch],origin=(lx,ly,lid_z),group='reservoir',color=WATER,
                notes=['Catch-basket hatch166x126. Separate55mm overflow entry and33.6mm vent pipe penetration.'])
    for i,(x,y) in enumerate(global_bolts,1):
        af=10;rr=af/math.sqrt(3)
        hexpts=[(rr*math.cos(k*math.pi/3),rr*math.sin(k*math.pi/3)) for k in range(6)]
        nut=plate(hexpts,5,[(0,0,6)])
        m.add(f'WT_WELDNUT_{i}',nut,origin=(x,y,flange_z-5),pn='STD_M6_WELDNUT',group='fasteners',material='M6 weld nut',purchased=True,color=HARDWARE)
        bolt=cyl(6,20).fuse(cyl(10,6).translate((0,0,20))).clean()
        m.add(f'WT_LID_BOLT_{i}',bolt,origin=(x,y,lidtop-20),pn='STD_M6x20_SOCKET',group='fasteners',material='M6x20 class8.8',purchased=True,color=HARDWARE)
    m.add('WT_VENT_NECK',pipe(60,33.4,26.6),origin=(150,850,lidtop),group='reservoir',material='NPS1 schedule40 steel pipe',color=WATER,length=60,
          notes=['Permanently open vent. Fit coarse removable stainless insect/debris mesh; inspect for blockage. No compressed-air connection.'])

    # Lift-out catch basket: actual perforated bottom, welded sheet sides and rim.
    bz=lidtop-100
    holes=[(x,y,6) for x in range(10,151,15) for y in range(10,111,15)]
    m.add_plate('WT_BASKET_BASE',160,120,1.5,holes=holes,origin=(820,1180,bz),group='catch_basket',material='304 stainless1.5mm',color=ALU,
                notes=['Ø6 coarse perforations; abrasive fines pass to settling tank. Removable for cleaning.'])
    for label,x in [('LEFT',820),('RIGHT',978.5)]:
        m.add_plate('WT_BASKET_'+label,120,98.5,1.5,origin=(x,1180,bz+1.5),u=(0,1,0),v=(0,0,1),pn='WT_BASKET_SIDE',group='catch_basket',material='304 stainless1.5mm',color=ALU)
    for label,y in [('FRONT',1181.5),('REAR',1300)]:
        m.add_plate('WT_BASKET_'+label,157,98.5,1.5,origin=(821.5,y,bz+1.5),u=(1,0,0),v=(0,0,1),pn='WT_BASKET_END',group='catch_basket',material='304 stainless1.5mm',color=ALU)
    m.add_plate('WT_BASKET_RIM',180,140,2,internal=[[(10,10),(170,10),(170,130),(10,130)]],origin=(810,1170,lidtop),group='catch_basket',material='304 stainless2mm',color=ALU,
                notes=['Rim seats on lid with7mm minimum overlap around hatch; entire basket lifts vertically100mm before rearward removal.'])
    m.add_plate('WT_BASKET_SPLASH_COVER',180,140,1.5,holes=[(90,100,58)],origin=(810,1170,lidtop+2),group='catch_basket',material='304 stainless1.5mm',color=ALU,
                notes=['Loose removable splash cover;58mm open inlet remains vented. Drain outlet is above inlet with air gap.'])
    return {'reservoir_internal_mm':[900,600,250],'gross_litres':135.0,'weir_top_z_mm':228.048,
            'reservoir_cover_top_z_mm':lidtop,'overflow_start_approx_z_mm':420.048,
            'water_charge_limit_litres':115,'minimum_return_capacity_litres':125,
            'pan_normal_level_z_mm':820,'pan_minimum_level_z_mm':810,'pan_high_high_z_mm':827,'pan_overflow_crest_z_mm':825,
            'reservoir_pump_low_trip_z_mm':233.048,
            'pipe_dimensional_source':PIPE_SOURCE,'pan_drain_xyz_mm':[900,1240+shift,top(1240+shift)],
            'unmodeled_purchased_connections':['Selected motorized valve, reducers/unions and refill pump connections require selected manufacturer dimensions.',
                                               'External emergency-overflow destination must be defined before commissioning.']}
