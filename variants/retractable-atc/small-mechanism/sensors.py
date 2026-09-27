"""Dimensioned PM-U25-P bodies, actual-pin flag, and fabricated mounts."""
import cadquery as cq
from cad_helpers import box,cyl,plate,place,rect

def sensor_body():
    # Local X width13.4, Y thickness6, Z height16; slot open upward.
    s=box(13.4,6,16).cut(box(6,8,5.5).translate((3.7,-1,10.5)))
    for x in (2.7,10.7):s=s.cut(cyl(3.2,8).rotate((0,0,0),(1,0,0),90).translate((x,7,2.5)))
    return s

def add_pin_sensors(m,index,py,shift,xf):
    reverse=index==1
    def add(n,s,pn,purchased=False,flat=None,local=None):
        q=m.add(f'LOCK_{index}_{n}',xf(s),pn=pn,group='pin-sensing',purchased=purchased,color=(.1,.15,.18) if purchased else (.2,.55,.65),flat=flat)
        if local is not None:q.local=local
        else:
            b=s.BoundingBox();q.local=s.translate((-b.xmin,-b.ymin,-b.zmin))
        return q
    # Two sensor slots face opposite directions: a single2mm flag translates6mm.
    # The flag cannot strike a slot's closed floor during the complete movement.
    targetys=[py+(-55 if reverse else 55),py+(-35 if reverse else 35)]
    fymin=min([py]+targetys);fymax=max([py]+targetys)
    flag=box(1.6,fymax-fymin+4,2).translate((120.2,fymin-2,957+shift))
    flag=flag.fuse(cyl(4,2).translate((121,py,957+shift)))
    for sy in targetys:flag=flag.fuse(box(14,1.6,2).translate((120.2,sy-.8,957+shift)))
    flag=flag.cut(cyl(3.2,2).translate((121,py,957+shift))).clean()
    add('SENSOR_FLAG',flag,'SM_PIN_FLAG_'+str(index))
    washer=cyl(6,.5).cut(cyl(3.2,.5)).translate((121,py,956.5+shift));add('FLAG_WASHER',washer,'WASHER_3p2_6_p5',True)
    nut=cq.Workplane('XY').polygon(6,5.5/0.866025403784).extrude(2.4).val().cut(cyl(2.5,2.4)).translate((121,py,954.1+shift))
    add('FLAG_NUT',nut,'M3_HEX_NUT',True)
    m.permit(f'LOCK_{index}_FLAG_NUT',f'LOCK_{index}_PIN','M3 threaded lower stem in M3 tapped nut; nominal thread cylinders.')
    for j,sy in enumerate(targetys):
        invert=j==1; beam=964 if invert else 958;bottom=962 if invert else 944
        body=sensor_body()
        if invert:body=body.rotate((6.7,3,8),(7.7,3,8),180)
        # local width alongY, depth alongX; body occupies X130..136.
        shape=body.rotate((0,0,0),(0,0,1),-90).translate((130,sy+6.7,bottom))
        add(f'SENSOR_{j}',shape,'PM_U25_P',True,local=sensor_body())
        row=975.5 if invert else 946.5
        bz=972.5 if invert else 943.5;bh=(994.3 if reverse else 987.95)-bz
        holes=[(2.7,row-bz,3.2),(10.7,row-bz,3.2)]
        internal=[] if invert else [[(4.2,951-bz),(9.2,951-bz),(9.2,972-bz),(4.2,972-bz)]]
        local=plate(rect(13.4,bh),2.9,holes,internal=internal)
        bracket=place(local,(127.1,sy-6.7,bz),u=(0,1,0),v=(0,0,1))
        add(f'SENSOR_BRACKET_{j}',bracket,f'SM_SENSOR_BRACKET_{index}_{j}',flat={'outline':rect(13.4,bh),'thickness_mm':2.9,'holes':holes,'slots':[],'internal':internal},local=local)
        for k,y in enumerate((sy-4,sy+4)):
            bolt=cyl(3,14).fuse(cyl(5.5,3).translate((0,0,14))).rotate((0,0,0),(0,1,0),-90).translate((141.1,y,row))
            add(f'SENSOR_BOLT_{j}_{k}',bolt,'M3x14_CAP',True)
            n=cq.Workplane('XY').polygon(6,5.5/0.866025403784).extrude(2.4).val().cut(cyl(2.5,2.4)).rotate((0,0,0),(0,1,0),90).translate((136,y,row))
            add(f'SENSOR_NUT_{j}_{k}',n,'M3_HEX_NUT',True)
            m.permit(f'LOCK_{index}_SENSOR_BOLT_{j}_{k}',f'LOCK_{index}_SENSOR_NUT_{j}_{k}','M3 nominal threaded cylinder.')
    return {'sensor_quantity':2,'target_opaque_mm':[1.6,2],'beam_height_withdrawn':958,'beam_height_engaged':964}

