"""Two owned 12-inch blanks, actual rectangular nesting with 4 mm cut gaps.

No price credit or assertion of alloy/flatness. Parts faced thinner keep their
original blank thickness in this nesting. Remaining custom parts are not owned.
"""
from pathlib import Path
import json,hashlib
import params as P

HERE=Path(__file__).resolve().parent
SIZE=304.8

def run():
    half=[dict(id='PLASMA_DROP',x=2,y=2,w=110,h=185+911-P.SLAT_TOP,finish_t=12.7)]
    half += [dict(id=f'ACTUATOR_PAD_{i+1}',x=x,y=y,w=70,h=60,finish_t=12.7)
             for i,(x,y) in enumerate([(116,2),(190,2),(116,66),(190,66),(116,130),(190,130)])]
    half += [dict(id=f'LINK_SUPPORT_WEB_{i+1}',x=x,y=194,w=48,h=40,finish_t=12.7) for i,x in enumerate((116,168))]
    half += [dict(id=f'LINK_SUPPORT_FLANGE_{i+1}',x=x,y=y,w=99.8,h=48,finish_t=6.35) for i,(x,y) in enumerate(((2,224),(106,238)))]
    three=[dict(id=f'ACTUATOR_SIDE_{i+1}',x=x,y=y,w=60,h=80,finish_t=9.525)
           for i,(x,y) in enumerate((x,y) for y in (2,86) for x in (2,66,130))]
    footpositions=[(194,y) for y in (2,46,90,134,178,222)]+[(2,170),(86,170)]
    three += [dict(id=f'FOOT_PLATE_{i+1}',x=x,y=y,w=80,h=40,finish_t=9.525) for i,(x,y) in enumerate(footpositions)]
    three += [dict(id=f'TOP_FISHPLATE_{i+1}',x=x,y=214,w=80,h=80,finish_t=6) for i,x in enumerate((2,86))]
    sheets=[dict(id='OWNED_HALF',stock_t=12.7,parts=half),dict(id='OWNED_THREE_EIGHTHS',stock_t=9.525,parts=three)]
    def fits(p,placed):
        if p['x']+p['w']>SIZE-2 or p['y']+p['h']>SIZE-2:return False
        return all(p['x']+p['w']+4<=a['x'] or a['x']+a['w']+4<=p['x'] or p['y']+p['h']+4<=a['y'] or a['y']+a['h']+4<=p['y'] for a in placed)
    small=[(f'TRACK_BACKING_BLOCK_{i+1}',20.,20.,9.525) for i in range(32)]+[(f'DOCK_PAD_{i+1}',16.,25.,3.175) for i in range(16)]
    for name,w,h,t in small:
        found=False
        for sheet in reversed(sheets):
            placed=sheet['parts'];xs=sorted({2.,*[a['x']+a['w']+4 for a in placed]});ys=sorted({2.,*[a['y']+a['h']+4 for a in placed]})
            for ww,hh in ((w,h),(h,w)):
                for yy in ys:
                    for xx in xs:
                        p=dict(id=name,x=xx,y=yy,w=ww,h=hh,finish_t=t)
                        if fits(p,placed):placed.append(p);found=True;break
                    if found:break
                if found:break
            if found:break
        assert found,('Owned-stock offcut nest cannot fit',name)
    for sheet in sheets:
        for p in sheet['parts']:
            assert min(p['x'],p['y'])>=2
            assert p['x']+p['w']<=SIZE-2 and p['y']+p['h']<=SIZE-2,p
            assert p['finish_t']<=sheet['stock_t']
        for i,a in enumerate(sheet['parts']):
            for b in sheet['parts'][i+1:]:
                separated=(a['x']+a['w']+4<=b['x'] or b['x']+b['w']+4<=a['x']
                         or a['y']+a['h']+4<=b['y'] or b['y']+b['h']+4<=a['y'])
                assert separated,(a,b)
        sheet['used_blank_area_mm2']=sum(p['w']*p['h'] for p in sheet['parts'])
    r={'stock_size_mm':[SIZE,SIZE],'cut_gap_mm':4,'edge_allowance_mm':2,'sheets':sheets,
       'passed':True,'scope':'Nominal cut nesting only. Confirm true stock dimensions, alloy, temper, damage, machining allowance and the final component drawing before cutting.',
       'not_covered':'All parts not explicitly listed, including the two deep gantry billets and six clevis billets, remain new material unless physically confirmed owned.',
       'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),HERE/'params.py')}}
    (HERE/'review').mkdir(exist_ok=True)
    (HERE/'review'/'owned-stock-check.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({s['id']:dict(parts=len(s['parts']),blank_area=s['used_blank_area_mm2']) for s in sheets},indent=2))
    return r

if __name__=='__main__':run()
