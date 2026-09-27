"""Sourced mounting interfaces; conservative simplified bodies, no race/thread CAD.

Motor face: local Z=0, screw along +Z. Nut flange: local Z=0..3.81,
barrel to Z=11. Rail: local X travel, centered Y, foot Z=0. Block center
is X=0; its top is Z=13 above the rail mounting plane.
"""
import math
import cadquery as cq

def box(x,y,z):return cq.Workplane('XY').box(x,y,z,centered=False).val()
def cyl(r,h,x=0,y=0,z=0):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))

def slide_motor():
    body=box(42.3,42.3,48).translate((-21.15,-21.15,-48))
    body=body.fuse(cyl(11,2)).fuse(cyl(4,298,z=2))
    for x in (-15.5,15.5):
        for y in (-15.5,15.5):body=body.cut(cyl(1.5,4.5,x,y,-4.5))
    return body.clean()

def slide_nut():
    part=cyl(12.7,3.81).fuse(cyl(6.35,7.19,z=3.81)).cut(cyl(4.1,13,z=-1))
    for angle in (0,120,240):
        a=math.radians(angle);part=part.cut(cyl(1.78,5,9.525*math.cos(a),9.525*math.sin(a),-.5))
    return part.clean()

def rail_350():
    rail=box(350,12,8).translate((0,-6,0))
    for x in [10+25*i for i in range(14)]:
        rail=rail.cut(cyl(1.75,10,x,0,-1)).cut(cyl(3,4.5,x,0,3.5))
    return rail.clean()

def mgn12h_block():
    block=box(45.8,27,10).translate((-22.9,-13.5,3))
    block=block.cut(box(48,12.4,5.2).translate((-24,-6.2,3)))
    for x in (-10,10):
        for y in (-10,10):block=block.cut(cyl(1.5,3.5,x,y,9.5))
    return block.clean()

def delta_housing():
    """DSOL-1151 body front Z0, plunger+Z; mounted by fabricated body saddle.

    The supplied UNC hole depth is unspecified, so this API does not invent
    tapped-hole depth or claim its solid rectangular housing is internal CAD.
    """
    body=box(28.956,24.9936,49.9872).translate((-14.478,-12.4968,-49.9872))
    return body.cut(cyl(5.65,35.1,z=-35)).clean()

def delta_plunger(released=False):
    """released=True means coil energized,6mm closer to housing than spring state."""
    tip=17.526+(0 if released else 6.)
    rod=cyl(5.4991,tip+15,z=-15)
    rod=rod.cut(box(4.826,12,8).translate((-2.413,-6,tip-7)))
    pin=cq.Solid.makeCylinder(3.2512/2,13,cq.Vector(-6.5,0,tip-3.9624),cq.Vector(1,0,0))
    return rod.cut(pin).clean()

def pose(shape,origin,direction=(0,0,1),xdir=(1,0,0)):
    return shape.moved(cq.Plane(origin=origin,xDir=xdir,normal=direction).location)
