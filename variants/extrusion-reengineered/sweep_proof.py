"""Conservative continuous translation proof by recursively covering an obstacle.

No trajectory sampling or ignored collision pairs. Every retained obstacle
cell is expanded by the negative translation box and checked against the
reference moving solid. A failure to prove separation remains unresolved.
"""
import cadquery as cq

def box(b):
    return cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))

def translation_cover_proof(moving,obstacle,tmin,tmax,max_depth=13,gap=.01):
    bb=obstacle.BoundingBox()
    initial=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]
    pending=[(initial,0)];examined=0;empty=0;clear=0;unresolved=[];minimum_gap=None
    while pending:
        b,depth=pending.pop();examined+=1
        # Cells partition the original bounding box. Only cells proven to
        # contain no obstacle material may be discarded.
        cell=box(b)
        if obstacle.intersect(cell).Volume()<1e-7:
            empty+=1;continue
        expanded=[b[k]-tmax[k] for k in range(3)]+[b[k+3]-tmin[k] for k in range(3)]
        swept_obstacle=box(expanded)
        distance=moving.distance(swept_obstacle)
        if distance>gap:
            clear+=1
            minimum_gap=distance if minimum_gap is None else min(minimum_gap,distance)
            continue
        lengths=[b[k+3]-b[k] for k in range(3)]
        axis=max(range(3),key=lambda k:lengths[k])
        if depth>=max_depth or lengths[axis]<.05:
            unresolved.append({'cell_bounds_mm':b,'depth':depth,'distance_mm':distance,
                'reference_intersection_mm3':moving.intersect(swept_obstacle).Volume()})
            # Stop after the first unresolved leaf. This is a failed proof,
            # not a sampled assertion that a collision occurs in operation.
            break
        middle=(b[axis]+b[axis+3])/2
        lower=b.copy();upper=b.copy();lower[axis+3]=middle;upper[axis]=middle
        pending.extend(((lower,depth+1),(upper,depth+1)))
    return {'passed':not unresolved and not pending,'cells_examined':examined,
        'empty_cells':empty,'separated_material_cells':clear,
        'unresolved_cells':unresolved,'minimum_expanded_cell_gap_mm':minimum_gap,
        'translation_min_mm':list(tmin),'translation_max_mm':list(tmax),
        'method':'Recursive covering of the complete fixed solid, expanded by the negative independent translation box; exact reference-solid distance. No path sampling. Empty-volume numerical threshold1e-7mm3; required proven separation0.01mm.'}
