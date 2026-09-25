"""Serviceable pump mounting and permanent vent screen hardware.

Pump is explicitly a clearance envelope. Port datums and the exact mounting-foot
thickness await receipt inspection; flexible hoses prevent false rigid fit claims.
"""
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

def make_water_accessories(m):
    lidtop=433.096;ztray=446.952
    fixing=[(752,842),(978,842),(752,944),(978,944)]
    pumpfix=[(x,y) for x in(866,924) for y in(850.5,935.5)]
    trayholes=[(x-740,y-830,6.6) for x,y in fixing]+[(x-740,y-830,5) for x,y in pumpfix]
    m.add_plate('PUMP_TRAY',250,126,3.048,holes=trayholes,origin=(740,830,ztray),group='pump_mount',
                notes=['FourØ5pumpmounts:58longitudinal×85transverse,210mmfamilydrawing. Receipt-checkselected31seriesbracketbeforefinaldrill.',
                       'Pumpfootthicknessandportaxisnotpublished;M4mountboltlengthisreceipt-selected. Flexiblehoseconnectionsrequired.'])
    lid=m.find('WT_LID')
    tools=[cyl(6.6,5).translate((x,y,lidtop-4)) for x,y in fixing]
    lid.shape=lid.shape.cut(cq.Compound.makeCompound(tools)).clean()
    bb=bbox(lid.shape);lid.local=lid.shape.translate(tuple(-v for v in bb[:3]))
    lid.flat['holes'].extend([(x-bb[0],y-bb[1],6.6) for x,y in fixing])
    for i,(x,y) in enumerate(fixing,1):
        m.add(f'PUMP_SPACER_{i}',pipe(13.856,12,6.6),origin=(x,y,lidtop),pn='PUMP_SPACER',group='pump_mount',length=13.856,
              notes=['OD12ID6.6steelspacer;lidandtrayremaindemountableforwashout.'])
        m.add(f'PUMP_WELDNUT_{i}',hexpart(10,5,6),origin=(x,y,lidtop-3.048-5),pn='STD_M6_WELDNUT',group='fasteners',material='M6weldnut',purchased=True,color=HARDWARE)
        bolt=cyl(6,35).fuse(cyl(10,6).translate((0,0,35))).clean()
        m.add(f'PUMP_TRAY_BOLT_{i}',bolt,origin=(x,y,ztray+3.048-35),pn='STD_M6x35_SOCKET',group='fasteners',material='M6x35class8.8',purchased=True,color=HARDWARE)
    # Bounding envelope only, including four clearance bores so the vendor mounting
    # datum remains visible. This is deliberately not a fabricated pump body.
    env=box(210,86,114.5).cut(cq.Compound.makeCompound([cyl(5,116).translate((x,y,-.5)) for x in(106,164) for y in(.5,85.5)])).clean()
    m.add('BUY_SEAFLO31_ENVELOPE',env,origin=(760,850,ztray+3.048),pn='BUY_SFDP2_018_120_31',group='pump',material='Purchased24V7Lminpump',purchased=True,color=(.18,.2,.23),
          release='PURCHASED CLEARANCE ENVELOPE - RECEIPT VERIFY BRACKET AND PORTS',
          notes=['210×86×114.5manufacturerfamilyenvelope;notinternalpumpgeometry.3/8NPTportsviaflexible1/2inhoseadapters.',
                 'Exactmountfootthicknessnotpublished;selectM4boltsafterreceipt.'])

    # Open vent is protected by a removable perforated cap; no closed pressure cap.
    # Two M4 set-screw holes retain sleeve to neck without a solid fastener over the bore.
    ventz=493.096
    sleeve=pipe(12,39.4,33.8)
    sleeve=sleeve.cut(place(cyl(4,6),(-20,0,5),u=(0,1,0),v=(0,0,1))).clean()
    sleeve=sleeve.cut(place(cyl(4,6),(14,0,5),u=(0,1,0),v=(0,0,1))).clean()
    m.add('VENT_SCREEN_SLEEVE',sleeve,origin=(150,850,ventz-8),group='vent',material='304stainlessmachinedsleeve',
          notes=['ID33.8OD39.4length12;2×M4radialtap,opposed. Perforatedcapweldedtosleeve;removeforscreenwashing.'])
    disk=cyl(39.4,1.5)
    holes=[(x,y,3) for x in(-9,-3,3,9) for y in(-9,-3,3,9) if x*x+y*y<150]
    disk=disk.cut(cq.Compound.makeCompound([cyl(3,2).translate((x,y,-.25)) for x,y,d in holes])).clean()
    m.add('VENT_PERFORATED_CAP',disk,origin=(150,850,ventz+4),group='vent',material='304stainless1.5mm',
          notes=['Ø39.4×1.5disc,12Ø3 holes on the ±3/±9 grid with four corners omitted;84.82mm² nominal open area,neverpaintorplug. Coarsedebrisguard,notfiltermedia.'])
    for i,x in enumerate((130.3,166.7),1):
        m.add(f'VENT_M4_SETSCREW_{i}',cyl(4,3),origin=(x,850,ventz-3),u=(0,1,0),v=(0,0,1),pn='STD_M4x3_GRUB',group='vent',material='M4x3grubscrew',purchased=True,color=HARDWARE)
    # Visible emergency catch vessel is below the permanently open tank standpipe.
    # It handles a brief fault discharge; it is not a115L secondary containment tank.
    m.add_plate('OVERFLOW_CATCH_FLOOR',600,250,1.5,origin=(250,1190,15),group='overflow_catch',material='304 stainless1.5mm',
                notes=['Welded open catch vessel,8.85L internal capacity. Keep visible and empty; investigate any water in it before restarting.'])
    for side,x in [('L',250),('R',848.5)]:
        m.add_plate('OVERFLOW_CATCH_SIDE_'+side,250,60,1.5,origin=(x,1190,16.5),u=(0,1,0),v=(0,0,1),pn='OVERFLOW_CATCH_SIDE',group='overflow_catch',material='304 stainless1.5mm')
    for side,y in [('F',1191.5),('R',1440)]:
        m.add_plate('OVERFLOW_CATCH_END_'+side,597,60,1.5,origin=(251.5,y,16.5),u=(1,0,0),v=(0,0,1),pn='OVERFLOW_CATCH_END',group='overflow_catch',material='304 stainless1.5mm')
    for i,(x,y) in enumerate([(x,y) for x in(275,825) for y in(1215,1415)],1):
        m.add('OVERFLOW_CATCH_PAD_'+str(i),cyl(30,15),origin=(x,y,0),pn='OVERFLOW_CATCH_PAD',group='overflow_catch',material='NBR rubber30mm rod,cut15mm',length=15,
              notes=['Bond pads beneath the removable catch vessel; inspect condition during washout.'])
    return {'pump_mount_plate_mm':[250,126,3.048],'pump_foot_hole_pattern_mm':[58,85],
            'purchased_pump_envelope_mm':[210,86,114.5],
            'pump_unknowns':['Exactfootthickness:M4boltlengthselectedafterreceipt','Portaxis:centeredrigidpipesnotreleased'],
            'vent_cap_open_area_mm2':len(holes)*3.141592653589793*1.5**2,
            'float_brackets_status':'Verticalfloattrip-planeandthreadengagementdimensionsareunpublished;wet-calibratedadjustablemountsremainunreleased.'}
