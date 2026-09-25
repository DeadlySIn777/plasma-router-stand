"""Adjustable removable float carriers; wet trip planes are commissioning values."""
import cadquery as cq
from cad_helpers import *
from frame_details import hexpart

# PAN_EMPTY uses a deliberately restricted carrier travel. Raising the old Z802
# carrier by 10 mm leaves >10 mm nominal clearance to the sloped pan floor.
# Commissioning may move this carrier UP, never down to recover an assumed trip.
PAN_EMPTY_MOUNT_MIN=812.0
PAN_EMPTY_MOUNT_MAX=832.0
PAN_EMPTY_MIN_AS_BUILT_GAP=8.0

def make_sensor_mounts(m):
    specs=[('PAN_MIN',1031.952,600,860,755,910,810),
           ('PAN_FILL',1031.952,660,870,755,910,820),
           ('PAN_HH',1031.952,720,877,755,910,827),
           ('PAN_EMPTY',1031.952,1197,PAN_EMPTY_MOUNT_MIN,755,910,None),
           ('TANK_LOW',1025,1000,283.048,210,325,233.048)]
    for label,wall,y,mount,low,high,trip in specs:
        pre='FLOAT_'+label+'_';back=wall-13.952;face=back-3.048;cx=wall-32.952
        # Two verticalslots permit independent sensor-height calibration; clampnuts
        # remain on the wet side, so no bolt penetrates a tank/pan wall.
        height=high-low
        slots=[(8,height/2,height-30,6.6,90),(42,height/2,height-30,6.6,90)]
        rail_pn='FLOAT_BACKRAIL_'+('TANK' if label=='TANK_LOW' else'PAN')
        rail_notes=['Slot height adjustment; weld two standoffs to wet face of wall. No new pan/tank wall penetrations.']
        if label=='PAN_EMPTY':
            # Arc centres correspond to M6 bolt-axis Z799.5..819.5. The 0.3 mm
            # diametral-radius difference of slot and screw permits at most
            # another 0.3 mm downward movement; include it in the gap check.
            slot_mid=(PAN_EMPTY_MOUNT_MIN+PAN_EMPTY_MOUNT_MAX)/2-12.5-low
            slot_len=PAN_EMPTY_MOUNT_MAX-PAN_EMPTY_MOUNT_MIN+6.6
            slots=[(8,slot_mid,slot_len,6.6,90),(42,slot_mid,slot_len,6.6,90)]
            rail_pn='FLOAT_BACKRAIL_PAN_EMPTY'
            rail_notes.append('Restricted PAN_EMPTY carrier mount Z812..832 nominal; do not extend slots downward. Lowest bolt-axis limit including 0.3 mm slot/shank radial play is mount Z811.7.')
        m.add_plate(pre+'BACKRAIL',50,height,6,slots=slots,origin=(back,y-25,low),u=(0,1,0),v=(0,0,1),pn=rail_pn,
                    group='float_mount',material='304stainless6mm',notes=rail_notes)
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
        guard_notes=[]
        if label=='PAN_EMPTY':
            guard_notes=['PAN_EMPTY installed guard underside Z750 at carrier mount Z812; floor footprint X978..1014, Y1177..1217. Nominal closest pan-floor clearance is 10.671 mm before fabrication tolerances.',
                         'Maintain at least 8 mm actual clear gap across the entire guard footprint after welding, with the carrier clamped at its lowest allowed setting. This allows 2.37 mm total pan/guard/datum variation after 0.3 mm bolt-slot play; rework the bracket if the gauge fails.',
                         'Removable for brushing/washout; the 8 mm clean gap is not permission to accumulate sludge. Wet-calibrate PAN_EMPTY and prove the remaining 60 s drain empties the usable pan before enabling a bed change. No dry-pan claim from this float alone.']
        m.add_plate(pre+'GUARD_FLOOR',36,40,1,holes=holes,origin=(cx-21,y-20,gz),pn='FLOAT_GUARD_FLOOR_PAN_EMPTY' if label=='PAN_EMPTY' else 'FLOAT_GUARD_FLOOR',group='float_guard',material='304stainless1mm',notes=guard_notes)
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
            'pan_empty_clearance':{'mount_nominal_range_z_mm':[PAN_EMPTY_MOUNT_MIN,PAN_EMPTY_MOUNT_MAX],'mount_lowest_with_slot_play_z_mm':PAN_EMPTY_MOUNT_MIN-0.3,'guard_underside_at_nominal_min_z_mm':PAN_EMPTY_MOUNT_MIN-62,'minimum_as_built_gap_mm':PAN_EMPTY_MIN_AS_BUILT_GAP,'pan_floor_check_footprint_xy_mm':[978,1177,1014,1217],'release':'WET CALIBRATION HOLD: prove actual trip and drained state; unknown supplier trip offset is not inferred from carrier height.'},
            'commissioning':'Wet-set actual reed trips with mount slots; independently prove normal stop, minimum, HH and tank low. PAN_EMPTY mount must remain Z812..832 nominal and its entire guard must retain >=8 mm actual floor clearance. Prove the actual low trip followed by 60 s drain before mode-swap release; do not lower the carrier to chase an assumed trip.',
            'guard_service':'Release2M6screwsandliftslider/sensor/guardasonepiece. Removebracketassembliesbeforelongsheetoverhangoutsidenominal800mmcuttingwidth.'}
