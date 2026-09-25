"""Adjustable removable float carriers; wet trip planes are commissioning values."""
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

def make_sensor_mounts(m):
    specs=[('PAN_MIN',1031.952,600,860,755,910,810),
           ('PAN_FILL',1031.952,660,870,755,910,820),
           ('PAN_HH',1031.952,720,877,755,910,827),
           ('PAN_EMPTY',1031.952,1197,802,755,910,None),
           ('TANK_LOW',1025,1000,283.048,210,325,233.048)]
    for label,wall,y,mount,low,high,trip in specs:
        pre='FLOAT_'+label+'_';back=wall-13.952;face=back-3.048;cx=wall-32.952
        # Two verticalslots permit independent sensor-height calibration; clampnuts
        # remain on the wet side, so no bolt penetrates a tank/pan wall.
        height=high-low
        slots=[(8,height/2,height-30,6.6,90),(42,height/2,height-30,6.6,90)]
        m.add_plate(pre+'BACKRAIL',50,height,6,slots=slots,origin=(back,y-25,low),u=(0,1,0),v=(0,0,1),pn='FLOAT_BACKRAIL_'+('TANK' if label=='TANK_LOW' else'PAN'),
                    group='float_mount',material='304stainless6mm',notes=['Slotheightadjustment;weldtwostandoffstowetfaceofwall. No newpan/tankwallpenetrations.'])
        for i,z in enumerate((low+20,low+55),1):
            m.add(pre+'STANDOFF_'+str(i),cyl(12,7.952),origin=(back+6,y,z),u=(0,1,0),v=(0,0,1),pn='FLOAT_STANDOFF',group='float_mount',material='304stainlessbar',length=7.952,
                  notes=['OD12×7.952solidstandoff,continuousfilletatbothends.'])
        # L-carrier is welded from two sheets, avoiding unspecified bend allowances.
        m.add_plate(pre+'SLIDER',44,25,3.048,holes=[(5,12.5,6.6),(39,12.5,6.6)],origin=(face,y-22,mount-25),u=(0,1,0),v=(0,0,1),pn='FLOAT_SLIDER',group='float_mount',material='304stainless0.120insheet')
        ledgex=cx-20;ledgew=face-ledgex
        m.add_plate(pre+'LEDGE',ledgew,44,3.048,holes=[(20,22,10.5)],origin=(ledgex,y-22,mount),pn='FLOAT_LEDGE',group='float_mount',material='304stainless0.120insheet',
                    notes=['M10sensorclearance10.5;weldrearledgetoslidertop. Floatthreadclampswithsuppliernut. Wetcalibrate;nominalmountZisnottripZ.'])
        for i,yy in enumerate((y-17,y+17),1):
            bolt=cyl(6,16).fuse(cyl(10,6).translate((0,0,16))).clean()
            m.add(pre+'BOLT_'+str(i),bolt,origin=(face+16,yy,mount-12.5),u=(0,1,0),v=(0,0,-1),pn='STD_M6x16_SOCKET',group='float_mount',material='M6x16stainlesssocket',purchased=True,color=HARDWARE)
            m.add(pre+'NUT_'+str(i),hexpart(10,5,6),origin=(back+6,yy,mount-12.5),u=(0,1,0),v=(0,0,1),pn='STD_M6_STAINLESS_NUT',group='float_mount',material='M6stainlessnut',purchased=True,color=HARDWARE)
        # ConservativeØ26×60under-ledgeenvelopeplusM10upperstem; actualfloatform
        # isnotpublished. Guardclearancesarecheckedagainstthislargerenvelope.
        sensor=cyl(26,60).fuse(cyl(10,8.048).translate((0,0,60))).clean()
        m.add(pre+'SENSOR_ENVELOPE',sensor,origin=(cx,y,mount-60),pn='BUY_FOCMKEAS_M10_65MM',group='float_sensor',material='Purchasedstainlessreedfloat',purchased=True,color=(.65,.65,.65),
              release='PURCHASED SERVICE ENVELOPE - WET CALIBRATE TRIP PLANE',notes=['Seller65mmoverall/M10/Ø26;conservative60mmunderledgebodyenvelope. Actualbodyshapeandtripoffsetnotpublished.',
                       'TargettripZ='+str(trip)+';PAN_EMPTYislowlevelplus60sdrain,notanabsolutedrydetector.'])
        m.add(pre+'SENSOR_NUT',hexpart(17,5,10),origin=(cx,y,mount+3.048),pn='BUY_FLOAT_M10_MOUNTNUT',group='float_sensor',material='SuppliedM10floatmountnut',purchased=True,color=HARDWARE,
              notes=['Nominal17AF×5mountnutenvelope;usesensorsuppliednutandsealingwasher,confirmactualthreadpitch.'])
        # Slotted guard is welded to the removablecarrier; no hiddenfixedtrap.
        gz=mount-62
        holes=[(x,yy,4) for x in(7,14,21,28) for yy in(8,16,24,32)]
        m.add_plate(pre+'GUARD_FLOOR',36,40,1,holes=holes,origin=(cx-21,y-20,gz),pn='FLOAT_GUARD_FLOOR',group='float_guard',material='304stainless1mm')
        for side,xx in enumerate((cx-21,cx+14),1):
            m.add_plate(pre+'GUARD_SIDE_'+str(side),40,61,1,slots=[(10,22,30,4,90),(20,22,30,4,90),(30,22,30,4,90)],origin=(xx,y-20,gz+1),u=(0,1,0),v=(0,0,1),pn='FLOAT_GUARD_SIDE',group='float_guard',material='304stainless1mm',
                        notes=['Slottedremovableguard;upperedgesweldtofloatledgeunderside. Brushcleanandtestfreefloattravel.'])
        for side,yy in enumerate((y-19,y+20),1):
            m.add_plate(pre+'GUARD_END_'+str(side),34,61,1,slots=[(8,22,30,4,90),(17,22,30,4,90),(26,22,30,4,90)],origin=(cx-20,yy,gz+1),u=(1,0,0),v=(0,0,1),pn='FLOAT_GUARD_END',group='float_guard',material='304stainless1mm')
        # Access openings expose both clamp screw heads without detaching the guard.
        for p in [p for p in m.parts if p.id.startswith(pre+'GUARD_')]:
            tools=[place(cyl(12,15),(face-8,yy,mount-12.5),u=(0,1,0),v=(0,0,1)) for yy in(y-17,y+17)]
            before=p.shape.Volume();p.shape=p.shape.cut(cq.Compound.makeCompound(tools)).clean()
            if abs(before-p.shape.Volume())>1e-4:
                # Unique guards need their exact hole/notch outline from the solid.
                p.part_number=p.id
                bb=bbox(p.shape);p.local=p.shape.translate(tuple(-v for v in bb[:3]));p.flat=None
                p.notes.append('Two 12 mm cylindrical access cuts along world X at the M6 clamp axes. Use the individual STEP for these guard cutouts; no through-cut DXF is issued for the intersecting notch.')
    return {'count':5,'mount_z_mm':{s[0]:s[3] for s in specs},'target_trip_z_mm':{s[0]:s[-1] for s in specs},
            'commissioning':'Wet-setactualreedtripwithmountslots;independentlyprovenormalstop,minimum,HH,andtanklow. SetPAN_EMPTYjustabovephysicalfloorwithfreemovement,then60sdrain.',
            'guard_service':'Release2M6screwsandliftslider/sensor/guardasonepiece. Removebracketassembliesbeforelongsheetoverhangoutsidenominal800mmcuttingwidth.'}
