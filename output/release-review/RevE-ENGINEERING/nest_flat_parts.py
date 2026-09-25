"""Conservative rectangular nesting of the actual individual DXF part schedule.

This lays out nominal contours, without CAM kerf compensation. Part marks and
stock borders are non-cut layers. It does not infer missing manufactured parts.
"""
from pathlib import Path
from collections import defaultdict
import json, math, re, random
import ezdxf
from ezdxf import bbox as dxf_bbox
from ezdxf.math import Matrix44

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'nesting'
STOCK = (1219.2, 2438.4)
EDGE = 10.0
GAP = 6.0

def material_group(row):
    text = row['material'].lower()
    if 'epdm' in text or 'gasket' in text:
        return 'EPDM_knife_cut'
    if 'alum' in text or '6061' in text or '5052' in text:
        return 'aluminum_confirm_alloy'
    if 'stainless' in text:
        return 'stainless_confirm_grade'
    if 'steel' in text or 'a36' in text:
        return 'carbon_steel'
    return re.sub('[^a-zA-Z0-9]+', '_', row['material']).strip('_')

def overlap(a, b):
    return (min(a[0]+a[2], b[0]+b[2]) > max(a[0], b[0])+1e-8 and
            min(a[1]+a[3], b[1]+b[3]) > max(a[1], b[1])+1e-8)

def subtract_rects(free, used):
    result = []
    ux, uy, uw, uh = used
    for f in free:
        x, y, w, h = f
        if not overlap(f, used):
            result.append(f)
            continue
        if ux > x: result.append((x, y, ux-x, h))
        if ux+uw < x+w: result.append((ux+uw, y, x+w-ux-uw, h))
        if uy > y: result.append((x, y, w, uy-y))
        if uy+uh < y+h: result.append((x, uy+uh, w, y+h-uy-uh))
    # MaxRects free regions may overlap each other; remove wholly contained ones.
    clean = []
    for i, f in enumerate(result):
        x, y, w, h = f
        if w <= 1e-8 or h <= 1e-8: continue
        contained = any(i != j and x >= g[0]-1e-8 and y >= g[1]-1e-8 and
            x+w <= g[0]+g[2]+1e-8 and y+h <= g[1]+g[3]+1e-8 and
            (f != g or j < i) for j, g in enumerate(result))
        if not contained: clean.append(f)
    return clean

def pack(items, mode, seed=None):
    key = {'area': lambda p:p['w']*p['h'],
           'long':lambda p:max(p['w'],p['h']),
           'perimeter':lambda p:p['w']+p['h']}[mode]
    rng=random.Random(seed)
    ordered=sorted(items, key=lambda p:key(p)*(rng.uniform(0.70,1.30) if seed is not None else 1), reverse=True)
    sheets = []
    for part in ordered:
        candidates=[]
        for si,s in enumerate(sheets):
            for f in s['free']:
                for rot in (False,True):
                    pw,ph=(part['h'],part['w']) if rot else (part['w'],part['h'])
                    if pw+GAP <= f[2]+1e-7 and ph+GAP <= f[3]+1e-7:
                        score=(min(f[2]-pw-GAP,f[3]-ph-GAP),f[2]*f[3]-(pw+GAP)*(ph+GAP),si)
                        candidates.append((score,si,f,rot,pw,ph))
        if not candidates:
            s={'free':[(EDGE,EDGE,STOCK[0]-2*EDGE+GAP,STOCK[1]-2*EDGE+GAP)],'parts':[]}
            sheets.append(s)
            f=s['free'][0]
            for rot in (False,True):
                pw,ph=(part['h'],part['w']) if rot else (part['w'],part['h'])
                if pw+GAP <= f[2]+1e-7 and ph+GAP <= f[3]+1e-7:
                    candidates.append(((min(f[2]-pw-GAP,f[3]-ph-GAP),0,len(sheets)-1),len(sheets)-1,f,rot,pw,ph))
            if not candidates: raise ValueError('Part exceeds 4x8 sheet: '+part['part_number'])
        _,si,f,rot,pw,ph=min(candidates,key=lambda x:x[0])
        position={**part,'x':f[0],'y':f[1],'rotated_90':rot,'placed_w':pw,'placed_h':ph}
        sheets[si]['parts'].append(position)
        sheets[si]['free']=subtract_rects(sheets[si]['free'],(f[0],f[1],pw+GAP,ph+GAP))
    return sheets

def main():
    OUT.mkdir(exist_ok=True)
    groups=defaultdict(list)
    excluded=[]
    rows=json.loads((ROOT/'cutlist.json').read_text(encoding='utf-8-sig'))
    for row in rows:
        pn=row['part_number']; source=ROOT/'dxf'/(pn+'.dxf')
        if row.get('individual_export_guarded') or not source.exists():
            excluded.append({'part_number':pn,'reason':'Purchased, guarded, or no 2D flat export'})
            continue
        thickness=row.get('thickness_mm')
        if not thickness: raise ValueError('Missing thickness for '+pn)
        doc=ezdxf.readfile(source)
        assert doc.units==4 and not doc.audit().has_errors,pn
        outline_entities=[e for e in doc.modelspace() if e.dxf.layer == 'CUT_OUTER']
        assert outline_entities, 'Missing CUT_OUTER stock boundary: '+pn
        bounds=dxf_bbox.extents(outline_entities)
        w=bounds.extmax.x-bounds.extmin.x;h=bounds.extmax.y-bounds.extmin.y
        assert w>0 and h>0,pn
        for n in range(row['quantity']):
            groups[(material_group(row),thickness)].append({'part_number':pn,'copy':n+1,'w':w,'h':h,
                'source':str(source),'source_xmin':bounds.extmin.x,'source_ymin':bounds.extmin.y})
    report={'stock_mm':STOCK,'edge_margin_mm':EDGE,'part_spacing_mm':GAP,
            'scope':'Nominal manufacturing geometry and labeled machining references. Only CUT layers are through-cut paths; tap/pocket/mark layers require their named operations. CAM lead-ins, kerf offsets, tabs and cut order require the fabrication shop.',
            'procurement_note':'Sheet counts are geometric layouts, not a requirement to buy a full sheet for every small material group. Buy flat bars or quoted cut blanks where cheaper. Thickness is the finished CAD thickness; procured stock and finish machining follow cutlist.json.',
            'groups':[],'excluded_nonflat_or_purchased':excluded}
    for (material,t),items in sorted(groups.items()):
        trials=[pack(items,mode) for mode in ('area','long','perimeter')]
        sheets=min(trials,key=lambda s:len(s))
        # Deterministic alternative orders improve utilization without changing
        # part geometry or reducing the specified edge/part clearances.
        lower_bound=math.ceil(sum(p['w']*p['h'] for p in items)/((STOCK[0]-2*EDGE)*(STOCK[1]-2*EDGE)))
        for seed in range(180):
            if len(sheets)<=lower_bound: break
            candidate=pack(items,('area','long','perimeter')[seed%3],seed)
            if len(candidate)<len(sheets): sheets=candidate
        record={'material':material,'thickness_mm':t,'sheets':len(sheets),'part_count':len(items),
                'rectangular_blank_area_m2':sum(p['w']*p['h'] for p in items)/1e6,'layouts':[]}
        for si,s in enumerate(sheets,1):
            doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace()
            for layer in ('CUT_OUTER','CUT_HOLES','CUT_INNER','PART_MARK_NO_CUT','STOCK_NO_CUT'):
                doc.layers.new(layer)
            ms.add_lwpolyline([(0,0),(STOCK[0],0),STOCK,(0,STOCK[1])],close=True,dxfattribs={'layer':'STOCK_NO_CUT'})
            for i,p in enumerate(s['parts']):
                assert p['x']>=EDGE-1e-7 and p['y']>=EDGE-1e-7
                assert p['x']+p['placed_w']<=STOCK[0]-EDGE+1e-7
                assert p['y']+p['placed_h']<=STOCK[1]-EDGE+1e-7
                for other in s['parts'][i+1:]:
                    assert not overlap((p['x'],p['y'],p['placed_w']+GAP-1e-7,p['placed_h']+GAP-1e-7),
                                       (other['x'],other['y'],other['placed_w']+GAP-1e-7,other['placed_h']+GAP-1e-7)),(p,other)
                source=ezdxf.readfile(p['source'])
                mats=[Matrix44.translate(-p['source_xmin'],-p['source_ymin'],0)]
                if p['rotated_90']:
                    mats.extend([Matrix44.z_rotate(math.pi/2),Matrix44.translate(p['h'],0,0)])
                mats.append(Matrix44.translate(p['x'],p['y'],0))
                transform=Matrix44.chain(*mats)
                for entity in source.modelspace():
                    if entity.dxf.layer not in doc.layers:
                        doc.layers.new(entity.dxf.layer)
                    copied=entity.copy();copied.transform(transform);ms.add_entity(copied)
                ms.add_text(f"{p['part_number']} #{p['copy']}",dxfattribs={'height':3,'layer':'PART_MARK_NO_CUT','insert':(p['x']+2,p['y']+2)})
            name=f'{material}_{t:g}mm_sheet_{si:02}.dxf'
            doc.saveas(OUT/name)
            read=ezdxf.readfile(OUT/name);assert not read.audit().has_errors
            record['layouts'].append({'file':name,'parts':s['parts']})
        report['groups'].append(record)
    report['verification']={'all_parts_counted_once':sum(g['part_count'] for g in report['groups'])==sum(len(v) for v in groups.values()),
                            'stock_edge_clearance_and_rectangle_nonoverlap':True,'DXF_units_mm_and_audit':True}
    (OUT/'sheet-nesting.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in g.items() if k!='layouts'} for g in report['groups']],indent=2))

if __name__=='__main__': main()
