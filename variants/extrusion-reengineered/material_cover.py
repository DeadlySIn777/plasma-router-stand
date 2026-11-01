"""Continuous translation separation using material-tight obstacle covers.

Each clipped material bounding box contains the complete material in its
partition cell. Cropping away air improves convergence without discarding any
obstacle material or exempting any collision pair.
"""
import cadquery as cq

def box(b):
    return cq.Solid.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],cq.Vector(*b[:3]))

def bounds(s):
    b=s.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def translation_cover_proof(moving,obstacle,tmin,tmax,max_depth=24,gap=.01):
    pending=[(bounds(obstacle),0)]
    examined=empty=clear=0;unresolved=[];minimum_gap=None
    while pending:
        cell,depth=pending.pop();examined+=1
        material=obstacle.intersect(box(cell))
        if material.Volume()<1e-7:
            empty+=1;continue
        b=bounds(material)
        expanded=[b[k]-tmax[k] for k in range(3)]+[b[k+3]-tmin[k] for k in range(3)]
        cover=box(expanded)
        distance=moving.distance(cover)
        if distance>gap:
            clear+=1
            minimum_gap=distance if minimum_gap is None else min(minimum_gap,distance)
            continue
        lengths=[b[k+3]-b[k] for k in range(3)]
        axis=max(range(3),key=lambda k:lengths[k])
        if depth>=max_depth or lengths[axis]<.025:
            unresolved.append(dict(cell_bounds_mm=cell,material_bounds_mm=b,
                depth=depth,distance_mm=distance,
                reference_intersection_mm3=moving.intersect(cover).Volume()))
            break
        middle=(b[axis]+b[axis+3])/2
        lower=b.copy();upper=b.copy();lower[axis+3]=middle;upper[axis]=middle
        pending.extend(((lower,depth+1),(upper,depth+1)))
    return dict(passed=not unresolved and not pending,cells_examined=examined,
        empty_cells=empty,separated_material_cells=clear,
        unresolved_cells=unresolved,minimum_expanded_cell_gap_mm=minimum_gap,
        translation_min_mm=list(tmin),translation_max_mm=list(tmax),
        method='Complete obstacle partition; bbox of actual obstacle material in each cell expanded by the negative independent translation box. No path sampling or pair exemptions. Empty-volume threshold1e-7mm3; required separation0.01mm.')
