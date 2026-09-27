"""Guided spring pin with equal-arm slotted bellcrank. Candidate, not commissioned."""
from pathlib import Path
import math,sys
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'output/release-review/RevE-ENGINEERING'))
from cad_helpers import box,cyl,plate,rect,place

def headed(shaft,hi,lo):
    return shaft.fuse(cyl(5,1).rotate((0,0,0),(1,0,0),-90).translate(hi)).fuse(cyl(5,.5).rotate((0,0,0),(1,0,0),90).translate(lo)).clean()

def add_locks(m,unlocked=False):
    shift=0 if unlocked else 6;angle=math.degrees(math.atan2(shift,20))
    steel=(.3,.37,.4);blue=(.12,.48,.65);gold=(.8,.6,.25)
    for i,py in enumerate((1055.,1430.)):
        mirror=i==1;cy=py+(-6 if mirror else 6)
        def xf(s):return s.mirror('YZ',(121,0,0)) if mirror else s
        def add(n,s,pn,**kw):
            q=m.add(f'LOCK_{i}_{n}',xf(s),pn=pn,group='lock',**kw)
            b=s.BoundingBox();q.local=s.translate((-b.xmin,-b.ymin,-b.zmin))
            return q
        def flat(n,outline,t,holes=(),slots=(),origin=(0,0,0),u=(1,0,0),v=(0,1,0)):
            local=plate(outline,t,holes,slots);q=add(n,place(local,origin,u,v),'SM_'+n,color=steel)
            q.local=local;q.flat={'outline':outline,'thickness_mm':t,'holes':list(holes),'slots':list(slots),'internal':[]};return q
        q=flat('LOCK_HOUSING',rect(28,10),13,[(13,5,6.05),(4,5,4.5),(23,5,4.5)],origin=(108,py-5,1007))
        for xx in (4,23):q.local=q.local.cut(cyl(7.5,5).translate((xx,5,8)))
        q.shape=xf(q.local.translate((108,py-5,1007)))
        q.flat['operations']=[{'type':'circle','x':xx,'y':5,'diameter':7.5,'layer':'COUNTERBORE7p5_DEPTH5'} for xx in (4,23)]
        for k,(xx,yy) in enumerate(((112,py),(131,py))):
            base=m.find('BASE_0');hole=cyl(3.3,12.8).translate((xx,yy,994.2));base.shape=base.shape.cut(xf(hole));base.local=base.shape.translate((-104.5,-1030,-994.3));base.flat['holes'].append(((242-xx if mirror else xx)-104.5,yy-1030,3.3))
            bolt=cyl(4,18).fuse(cyl(7,4).translate((0,0,18))).translate((xx,yy,997))
            add(f'MOUNT_BOLT_{k}',bolt,'CAP_M4x18',color=steel,purchased=True)
            m.permit(f'LOCK_{i}_MOUNT_BOLT_{k}','BASE_0','M4 screw in tapped3.3minor bore; cut20mm stock screw to18mm.')
        pin=cyl(6,33).translate((121,py,985+shift)).fuse(cyl(8,6).translate((121,py,979+shift))).fuse(cyl(3,25.5).translate((121,py,953.5+shift)))
        follower=cyl(3.2,16).rotate((0,0,0),(1,0,0),90).translate((121,py+8,982+shift))
        add('PIN',pin.cut(follower),'SM_GROUND_LOCK_PIN',color=gold,notes=['Diameter6h6 shaft; housing6.05+.02;4mm engagement/2mm release clearance. M3 lower stem for flag nut.'])
        add('FOLLOWER',headed(follower,(121,py+8,982+shift),(121,py-8,982+shift)),'SM_FOLLOWER_3p2_L16_RIVET',color=gold,notes=['Head5x1; upset tail5x0.5 after assembly; verify free articulation. Replace after removal.'])
        outline=[(-4,-26),(4,-26),(4,-4),(26,-4),(26,4),(-4,4)];slots=[(0,-20.5,6.5,3.4,90),(20.5,0,6.5,3.4,0)]
        q=flat('BELLCRANK',outline,3.175,[(0,0,3.3)],slots,origin=(101,cy+1.5875,982),u=(1,0,0),v=(0,0,1))
        q.shape=xf(place(q.local,(101,cy+1.5875,982),u=(1,0,0),v=(0,0,1)).rotate((101,cy,982),(101,cy+1,982),-angle));q.color=blue
        yy=cy+1.7375
        flat('PIVOT_EAR',rect(14,20.3),3.175,[(4,8,3.2)],origin=(97,yy+3.175,974),u=(1,0,0),v=(0,0,1))
        pin=cyl(3.2,7).rotate((0,0,0),(1,0,0),90).translate((101,yy+3.175,982))
        add('PIVOT_PIN',headed(pin,(101,yy+3.175,982),(101,yy+3.175-7,982)),'SM_PIVOT_PIN_3p2_L7_RIVET',color=gold)
        gap=2.7+shift;force=(14-gap)*.0602
        add('SPRING_ENVELOPE',cyl(5,gap).cut(cyl(4.5,gap)).translate((121,py,976.3)),'SPRING_SPEC_OD5_FREE14_RATE0p0602',color=gold,purchased=True,notes=[f'Force specification {force:.3f}N at length {gap}mm. Catalog spring and actual friction remain unqualified.'])
        flat('SPRING_SEAT',rect(12,12),3,[(6,6,3.5)],origin=(115,py-6,973.3))
        for xx in (112,127):add(f'SPRING_POST_{xx}',box(3,5,21).translate((xx,py if mirror else py-5,973.3)),'SM_SPRING_POST',color=steel)
        front=87.4364;mounty=cy+(14.478 if not mirror else -14.478)
        body=box(49.9872,28.956,24.9936).translate((front-49.9872,cy-14.478,949.5032))
        for xx in (front-7.112,front-22.987):body=body.cut(cyl(3.5,3).rotate((0,0,0),(1,0,0),90 if not mirror else -90).translate((xx,mounty,962)))
        add('SOLENOID',body,'DELTA_DSOL_1151_24C_BODY',color=gold,purchased=True,notes=['Selected same-height8-32 face; thread depth unpublished. Check delivered revision.'])
        plunger=cyl(10.9982,17.526+shift).rotate((0,0,0),(0,1,0),90).translate((front,cy,962)).cut(box(15,4.826,12).translate((front+2.526+shift,cy-2.413,956)))
        clevis=cyl(3.2,11).rotate((0,0,0),(1,0,0),90).translate((101+shift,cy+5.5,962))
        add('PLUNGER',plunger.cut(clevis),'DELTA_PLUNGER_ENVELOPE',color=gold,purchased=True,notes=['Fork width4.826 sourced; useful fork depth14.5mm is an integration requirement pending delivered part.'])
        add('CLEVIS_PIN',headed(clevis,(101+shift,cy+5.5,962),(101+shift,cy-5.5,962)),'SM_CLEVIS_PIN_3p2_L11_RIVET',color=gold)
        add('TERMINALS',box(12,19.3,12.7).translate((front-49.9872,cy-9.65,936.8032)),'DELTA_TERMINAL_ENVELOPE',color=gold,purchased=True)
        q=flat('SOLENOID_MOUNT',rect(100.0508,44.7968),3.175,[(49.9872-7.112,12.4968,4.5),(49.9872-22.987,12.4968,4.5)],origin=(front-49.9872,mounty+3.175 if not mirror else mounty,949.5032),u=(1,0,0),v=(0,0,1));q.part_number += '_REAR' if mirror else '_FRONT'
        if not mirror:
            q.local=q.local.cut(cyl(10,3.175).translate((115-(front-49.9872),967.25-949.5032,0)));q.flat['holes'].append((115-(front-49.9872),967.25-949.5032,10));q.shape=place(q.local,(front-49.9872,mounty+3.175,949.5032),u=(1,0,0),v=(0,0,1))
        window=[(119-(front-49.9872),956-949.5032),(123-(front-49.9872),956-949.5032),(123-(front-49.9872),966-949.5032),(119-(front-49.9872),966-949.5032)]
        q.local=q.local.cut(plate(window,3.175));q.flat['internal'].append(window)
        q.shape=xf(place(q.local,(front-49.9872,mounty+3.175 if not mirror else mounty,949.5032),u=(1,0,0),v=(0,0,1)))
        for k,xx in enumerate((front-7.112,front-22.987)):
            sign=1 if not mirror else -1;surf=mounty+sign*3.175
            sh=cyl(4.166,6.35).fuse(cyl(7.5,2.5).translate((0,0,6.35))).rotate((0,0,0),(1,0,0),-90*sign).translate((xx,surf-sign*5.85,962))
            add(f'SOLENOID_SCREW_{k}',sh,'8_32_UNC_QUARTER_PAN',color=steel,purchased=True,notes=['Delivered tapped depth must be at least3.175mm; nominal engagement2.675mm plus0.5mm bottom reserve.'])
            add(f'SOLENOID_WASH_{k}',cyl(8,.5).cut(cyl(4.5,.5)).rotate((0,0,0),(1,0,0),-90*sign).translate((xx,surf,962)),'WASHER_4p5_8_p5',color=steel,purchased=True)
            m.permit(f'LOCK_{i}_SOLENOID_SCREW_{k}',f'LOCK_{i}_SOLENOID','Nominal8-32 major cylinder in3.5minor bore; conditional delivered depth.')
        from sensors import add_pin_sensors
        add_pin_sensors(m,i,py,shift,xf)
    return {'pin_diameter_mm':6,'withdrawal_mm':6,'engagement_mm':4,'clearance_unlocked_mm':2,'lock_axes_xy':[[121,1055],[121,1430]],'automatic_unlock_coils':2,'solenoid_model':'Delta DSOL-1151-24C','max_spring_target_N':.68026,'bellcrank_equal_arms_mm':20,'slot_radial_slide_mm':math.hypot(20,6)-20,'release':'Unload screw reaction; verify both pins withdrawn; move; verify endpoint pin engaged before M6/cutting.','sensors':'Four PM-U25-P; separate actual-pin endpoint flags; isolated PNP input interfaces.','retention':'Headed and upset-tail custom pivots; verify free rotation after peening.'}

