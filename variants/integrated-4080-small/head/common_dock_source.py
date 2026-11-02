"""Defined common head-side dock. Supplier-facing Z attachment remains undrilled.

Coordinates: X across, +Y forward, +Z up. Custom geometry and nominal metric
fastener envelopes; no ownership, thread-strength or supplier-mount claim.
"""
from pathlib import Path
import math
import cadquery as cq

HERE = Path(__file__).resolve().parent

def box(w,d,h,p):
    return cq.Workplane('XY').box(w,d,h,centered=False).val().translate(p)

def cz(d,L,p):
    return cq.Workplane('XY').circle(d/2).extrude(L).val().translate(p)

def cy(d,L,p):
    return cq.Workplane('XY').circle(d/2).extrude(L).val().rotate((0,0,0),(1,0,0),-90).translate(p)

def washer_y(od,di,t,p):
    return cy(od,t,p).cut(cy(di,t+2,(p[0],p[1]-1,p[2]))).clean()

def socket_screw_y(d,L,tip,head_d=None,head_h=None):
    hd = head_d or {2:3.8,3:5.5,4:7.,5:8.5,6:10.}[d]
    hh = head_h or d
    x,y,z = tip
    shape = cy(d,L,tip).fuse(cy(hd,hh,(x,y+L,z)))
    af = {2:1.5,3:2.5,4:3,5:4,6:5}[d]
    radius = af/math.sqrt(3)
    wire = [(radius*math.cos(k*math.pi/3),radius*math.sin(k*math.pi/3)) for k in range(6)]
    key = cq.Workplane('XY').polyline(wire).close().extrude(hh*.65+.2).val().rotate((0,0,0),(1,0,0),-90).translate((x,y+L+hh*.35,z))
    return shape.cut(key).clean()

def part(ident,shape,group,material,notes,purchased=False,move='fixed'):
    shape=shape.clean()
    if not shape.isValid() or len(shape.Solids())!=1:
        raise ValueError('Invalid dock part '+ident)
    return {'id':ident,'shape':shape,'group':group,'material':material,'notes':notes,
            'commodity_candidate':purchased,'owner_purchase_confirmed':False,'move':move}

def head_blank(height=110.):
    """Return removable9.525mm plate with the exact common interface cut.

    Root router adapter may request height150 without changing common features.
    M3 cage holes and M6 release holes are included. Threads use major-diameter
    voids for overlap checks; manufacturing taps are separate notes.
    """
    if height<100: raise ValueError('Head blank too short for the shared locators')
    p=box(80,9.525,height,(-40,12.7,0))
    p=p.cut(box(30.6,11.525,13,(-15.3,11.7,57.0)))
    for xx in (-28,28):
        p=p.cut(cy(6.6,12,(xx,11.7,40)))
        for zz in (29,51):p=p.cut(cy(3,8,(xx,14.225,zz)))
    p=p.cut(cy(5.2,12,(-30,11.7,85)))
    slot=cy(5.2,12,(28.5,11.7,85)).fuse(cy(5.2,12,(31.5,11.7,85))).fuse(box(3,12,5.2,(28.5,11.7,82.4)))
    return p.cut(slot).clean()

def common_dock():
    """Return fixed receiver parts and common metadata. No supplier holes."""
    out=[];contacts=[]
    receiver=box(80,12.7,110,(-40,0,0))
    for xx in (-28,28): receiver=receiver.cut(cy(6,14.7,(xx,-1,40)))
    for xx in (-30,30): receiver=receiver.cut(cy(4,8,(xx,4.7,85)))
    for xx in (-8,8): receiver=receiver.cut(cy(4,10,(xx,2.7,63.65)))
    out.append(part('CD_RECEIVER',receiver,'common_receiver','6061-T6 candidate12.7mm blank',
                    '80x110x12.7 receiver. The two M6 head-retention holes are through-tapped for ordinary drill/tap runout; screw tips stop at Y2.225. Other M4 tool-side taps remain blind. No supplier Z mounting pattern is supplied; actual Z support and load qualification remain missing.'))
    ledge=box(30,9.525,12.7,(-15,12.7,57.3))
    for xx in (-8,8): ledge=ledge.cut(cy(4.5,12,(xx,11.7,63.65)))
    out.append(part('CD_GRAVITY_LEDGE',ledge,'common_receiver','6061-T6 candidate9.525mm blank',
                    'Positive seat topZ70. TwoM4x20/1mm washers clamp ledge to receiver; inspect/preload before loading.'))
    contacts.append(['CD_RECEIVER','CD_GRAVITY_LEDGE'])
    for xx in (-8,8):
        tag='L' if xx<0 else 'R'
        out.append(part('CD_LEDGE_WASHER_'+tag,washer_y(9,4.3,1,(xx,22.225,63.65)),'fastener','SteelM4washer',
                        'Nominal9OD/4.3ID/1thick washer; verify selected hardware.',True))
        out.append(part('CD_LEDGE_SCREW_'+tag,socket_screw_y(4,20,(xx,3.225,63.65)),'fastener','SteelM4x20',
                        '9.475mm nominal receiver engagement; head bears through1mm washer.',True))
        contacts += [['CD_GRAVITY_LEDGE','CD_LEDGE_WASHER_'+tag],['CD_LEDGE_WASHER_'+tag,'CD_LEDGE_SCREW_'+tag]]
    for xx in (-30,30):
        tag='L' if xx<0 else 'R'
        pin=cy(4,8,(xx,4.7,85)).fuse(cy(5,8,(xx,12.7,85)))
        key=box(1.2,2.1,3.2,(xx-.6,18.7,83.4))
        pin=pin.cut(key)
        out.append(part('CD_LOCATOR_'+tag,pin,'common_receiver','Custom steel shoulder locator',
                        'M4x8 threaded anchor,5mm diameter x8mm locating shoulder; end screwdriver slot. One round and one relieved head bore. Actual fit/repeatability unqualified.'))
        contacts.append(['CD_RECEIVER','CD_LOCATOR_'+tag])
    meta={'coordinates':'X across, +Y forward, Z up','receiver_rear_Y_mm':0,'head_rear_Y_mm':12.7,
          'head_front_Y_mm':22.225,'head_default_height_mm':110,'head_width_mm':80,
          'gravity_seat_Z_mm':70,'ledge_window_XZ_mm':[-15.3,15.3,57,70],
          'release_centers_XZ_mm':[[-28,40],[28,40]],'release_withdrawal_mm':11,
          'release_tip_reserve_mm':.525,'head_forward_clearance_translation_mm':18,
          'locator_centers_XZ_mm':[[-30,85],[30,85]],'locator_projection_mm':8,
          'head_cage_bounds_by_center':'Xcenter±6.35,Y22.225..41.225,Z26..54',
          'cage_blank_thickness_mm':12.7,'cage_sidewall_mm':1.1,'cage_retention_abuse_qualified':False,
          'supplier_Z_mounting_pattern_known':False,'supplier_attachment_holes_present':False,
          'tool_retention_M6_holes_through':True,
          'physical_qualification':False,'contacts':contacts}
    return out,meta

def removable_fasteners(withdrawal=0.):
    """Two real screw/cage sets plus cage fixing screws; plate supplied by caller."""
    if not 0<=withdrawal<=11: raise ValueError('Captive screw range0..11')
    out=[];contacts=[]
    for xx in (-28,28):
        tag='L' if xx<0 else 'R'
        cage=box(12.7,2,16,(xx-6.35,39.225,32)).cut(cy(6.6,4,(xx,38.225,40)))
        for dx in (-6.35,5.25):cage=cage.fuse(box(1.1,17,16,(xx+dx,22.225,32)))
        for zz in (26,48):
            cage=cage.fuse(box(12.7,3,6,(xx-6.35,22.225,zz)))
        for zz in (29,51):cage=cage.cut(cy(3.4,5,(xx,21.225,zz)))
        out.append(part('CD_CAPTIVE_CAGE_'+tag,cage,'head_fastener','Custom small aluminium cage',
                        '12.7mm-blank open cage fixed by two M3x10. A6.6mm front tool aperture retains10mm M6head;11mm maximum withdrawal. The1.1mm sidewalls retain only the released screw; they do not support the head load. Retention/handling abuse and stock blank availability require qualification.',move='head'))
        out.append(part('CD_RELEASE_SCREW_'+tag,socket_screw_y(6,20,(xx,2.225+withdrawal,40)),'head_fastener','SteelM6x20',
                        '10.475mm nominal thread engagement atseated; backs11mm toclear receiver0.525mm. Captive head stops inside cage.',True,'head'))
        for zz in (29,51):
            ident=f'CD_CAGE_FIX_{tag}_{zz}'
            out.append(part(ident,socket_screw_y(3,10,(xx,15.225,zz)),'head_fastener','SteelM3x10',
                            '3mm cage foot plus7mm head-plate engagement; M3 major bore envelope,2.5mm tap drill.',True,'head'))
            contacts.append(['CD_CAPTIVE_CAGE_'+tag,ident])
    return out,{'contacts':contacts,'withdrawal_mm':withdrawal,'cages_require_assembly_after_release_screws_inserted':True}
