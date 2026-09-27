"""Inset side keepers, fixed front stops and removable axial service caps."""
def retain(e,prefix,front,y,z,material):
    add=e['add'];plate=e['plate'];bolt=e['bolt'];box=e['box'];cyl=e['cyl'];pose=e['pose'];parts=e['parts'];steel=e['STEEL']
    plate(prefix+'BODY_END_FRONT',28.956,28.9936,4,(front-4,y-14.478,z-14.4968),[(14.478,14.4968,11.5)],normal=(1,0,0),xdir=(0,1,0),material=material,note='Fixed positive axial front stop; weld to front saddle tie. Plunger passes through the 11.5 mm bore.')
    # Rear cap has a centered upper ear. Two actual M3x10 screws pass through
    # its 4 mm plate into 8 mm blind taps in the extended rear saddle roof.
    outline=[(0,0),(28.956,0),(28.956,28.9936),(25.478,28.9936),(25.478,34.9936),(3.478,34.9936),(3.478,28.9936),(0,28.9936)]
    plate(prefix+'BODY_END_REAR',28.956,34.9936,4,(front+49.9872,y-14.478,z-14.4968),[(8.478,30.9936,3.4),(20.478,30.9936,3.4)],normal=(1,0,0),xdir=(0,1,0),material=material,outline=outline,note='Removable 4 mm axial service cap. Two M3x10 screws give 6 mm engagement in 8 mm blind taps, 2 mm bottom margin. Disconnect leads and remove this cap, then withdraw the coil axially toward this end; guided plunger remains linked. Delivered internal retention and terminals require inspection.')
    add(prefix+'END_TIE_F',box(4,28.956,2).translate((front,y-14.478,z-14.4968)),'fixed',material,steel,'Weld tie between fixed front endplate and saddle base.')
    rear=next(p for p in parts if p.id==prefix+'BODY_STRAP_1')
    rear.shape=rear.shape.fuse(box(10,22,8).translate((front+39.9872,y-11,z+12.4968))).clean()
    rear.note+=' Integral or welded rear roof boss, 10 x 22 x 8 mm, with two M3 blind taps 8 mm deep from the rear axial face. Nominal major-diameter thread representation; drill/tap per material and inspect depth.'
    for j,yy in enumerate((y-6,y+6)):
        rear.shape=rear.shape.cut(pose(cyl(1.5,8.001),(front+49.9882,yy,z+16.4968),(-1,0,0),(0,1,0)))
        bolt(prefix+'END_CAP_BOLT_'+str(j),3,10,(front+53.9872,yy,z+16.4968),(-1,0,0),(0,1,0))
    plate(prefix+'BODY_SIDE_KEEPER',42,4,24.9936,(front+4,y-18.478,z-12.4968),[(3,2,3.,10.,'top'),(39,2,3.,10.,'top')],material=material,note='Inset removable side keeper; two vertical M3x10 captive-head screws into 10 mm blind taps. Coil is retained geometrically; no friction-clamp force assumed. Leave keeper installed during axial coil service.')
    for j,x in enumerate((front+7,front+43)):
        through=cyl(1.7,5,x,y-16.478,z+12)
        cb=cyl(3,4,x,y-16.478,z+13.4968)
        for p in parts:
            if p.id.startswith(prefix+'BODY_STRAP_'):p.shape=p.shape.cut(through).cut(cb)
        bolt(prefix+'KEEPER_BOLT_'+str(j),3,10,(x,y-16.478,z+13.4968),(0,0,-1))
    if prefix=='CATCH_':
        for p in parts:
            if p.id.startswith(prefix+'BODY_STRAP_'):p.shape=p.shape.cut(box(100,60,10).translate((front-10,y-30,z-24.4968)))
