"""Conservative rigid-part path bounds against actual fixed CAD solids, mm.

CLEAR means no tested bound intersects fixed material above the stated Boolean
volume tolerance. CANDIDATE_NOT_PROVEN is not a collision finding: an AABB can
include much empty space. Optional exact pose probes distinguish some true
interferences from unresolved conservative candidates. Touching surfaces, stock
tolerances and omitted parts are not certified by a positive-volume check.

All moving parts in a call share one rigid transform. Their mutual clearance is
unchanged and must have been checked in the initial configuration. Different
independently moving groups require separate trajectory coordination.
"""
import math
import cadquery as cq
from cad_helpers import bbox,box,intersection_volume


def _parts(parts):
    result=list(parts.items()) if isinstance(parts,dict) else [(p.id,p.shape) for p in parts]
    if len({name for name,_ in result})!=len(result):raise ValueError('Duplicate part IDs')
    for name,shape in result:
        if not shape.isValid() or not shape.Solids():raise ValueError('Invalid/non-solid input: '+name)
    return result


def _candidate(a,b):
    # Keep touching AABBs in the broadphase. The actual-solid Boolean decides
    # whether they overlap by positive volume.
    return all(min(a[k+3],b[k+3])>=max(a[k],b[k]) for k in range(3))


def _bound_shape(bounds):
    return box(*(bounds[k+3]-bounds[k] for k in range(3))).translate(tuple(bounds[:3]))


def _report(kind,moving,fixed,clearance,volume_tolerance):
    if not all(math.isfinite(x) and x>=0 for x in (clearance,volume_tolerance)):
        raise ValueError('Tolerances must be finite and nonnegative')
    return {'method':kind,'status':'CLEAR','moving_part_count':len(moving),
            'fixed_part_count':len(fixed),'clearance_mm':clearance,
            'boolean_volume_tolerance_mm3':volume_tolerance,'bound_tests':0,
            'candidates':[],'caller_exclusions':[],
            'scope':'Conservative nominal rigid geometry. CLEAR excludes positive-volume interference above the Boolean tolerance; surface contact, unmodeled parts and manufacturing uncertainty are outside this result.'}


def _finish(report):
    report['all_pairs_included']=not report['caller_exclusions']
    if report['status']=='CLEAR' and report['caller_exclusions']:
        report['status']='CLEAR_EXCEPT_CALLER_EXCLUSIONS'
    return report


def _test_bound(report,moving_id,bounds,fixed,poses,exclusions,context):
    previous=report.get('swept_enclosing_bounds_mm')
    report['swept_enclosing_bounds_mm']=list(bounds) if previous is None else (
        [min(previous[k],bounds[k]) for k in range(3)]+
        [max(previous[k+3],bounds[k+3]) for k in range(3)])
    region=None
    for fixed_id,fixed_shape,fixed_bounds in fixed:
        if not _candidate(bounds,fixed_bounds):continue
        pair=(moving_id,fixed_id)
        if pair in exclusions:
            reason=exclusions[pair]
            if not reason:raise ValueError('Every caller exclusion requires a reason')
            report['caller_exclusions'].append({'moving':moving_id,'fixed':fixed_id,'reason':reason,**context})
            continue
        if region is None:region=_bound_shape(bounds)
        report['bound_tests']+=1
        volume=intersection_volume(region,fixed_shape)
        if volume<=report['boolean_volume_tolerance_mm3']:continue
        exact=[]
        for label,shape in poses():
            pb=bbox(shape)
            if _candidate(pb,fixed_bounds):
                measured=intersection_volume(shape,fixed_shape)
                if measured>report['boolean_volume_tolerance_mm3']:
                    exact.append({'pose':label,'intersection_mm3':measured})
        report['candidates'].append({'moving':moving_id,'fixed':fixed_id,
            'bound_mm':bounds,'bound_intersection_mm3':volume,
            'exact_probe_interferences':exact,
            'interpretation':'Actual overlap confirmed at listed probe poses.' if exact else 'Conservative bound intersects; actual collision has not been proved.',**context})
        report['status']='CANDIDATE_NOT_PROVEN'


def translation_segment(moving_parts,fixed_parts,delta_xyz,*,clearance_mm=0,
                        volume_tolerance_mm3=1e-6,exclusions=None,probe_candidates=True):
    """Bound each part's complete translation from its current world placement.

    Endpoint-AABB union encloses the whole path (also for a diagonal straight
    translation). Fixed geometry is the actual solid, not its bounding box.
    Exclusions map ordered (moving_id,fixed_id) pairs to explicit reasons.
    """
    moving=_parts(moving_parts);fixed_raw=_parts(fixed_parts)
    fixed=[(name,shape,bbox(shape)) for name,shape in fixed_raw]
    delta=tuple(float(x) for x in delta_xyz)
    if len(delta)!=3 or not all(math.isfinite(x) for x in delta):raise ValueError('Finite xyz displacement required')
    report=_report('Full translation enclosed by endpoint-AABB union',moving,fixed,clearance_mm,volume_tolerance_mm3)
    report['delta_xyz_mm']=delta
    for name,shape in moving:
        bb=bbox(shape)
        bounds=[bb[k]+min(0,delta[k])-clearance_mm for k in range(3)]
        bounds += [bb[k+3]+max(0,delta[k])+clearance_mm for k in range(3)]
        def poses():
            if probe_candidates:
                for fraction in (0,.5,1):
                    yield {'fraction':fraction},shape.translate(tuple(x*fraction for x in delta))
        _test_bound(report,name,bounds,fixed,poses,exclusions or {},{})
    return _finish(report)


def rotation_segment(moving_parts,fixed_parts,axis_origin,axis,start_deg,end_deg,*,
                     max_step_deg=5,clearance_mm=0,volume_tolerance_mm3=1e-6,
                     exclusions=None,probe_candidates=True):
    """Conservative continuous rotation about world X, Y or Z.

    The supplied shapes are at zero angle. Each cell uses the AABB at its middle
    angle, expanded in the radial directions by r_max*half_step_radians. Every
    point moves by at most that distance within the cell, including between
    exact probe poses. r_max is bounded from all original-shape AABB corners.
    """
    axis=str(axis).upper()
    if axis not in ('X','Y','Z'):raise ValueError('Principal axis X, Y or Z required')
    if not math.isfinite(max_step_deg) or max_step_deg<=0:raise ValueError('Positive finite angular step required')
    if not all(math.isfinite(v) for v in (*axis_origin,start_deg,end_deg)):raise ValueError('Finite rotation data required')
    moving=_parts(moving_parts);fixed_raw=_parts(fixed_parts)
    fixed=[(name,shape,bbox(shape)) for name,shape in fixed_raw]
    axial=('X','Y','Z').index(axis);radial=[k for k in range(3) if k!=axial]
    origin=tuple(axis_origin);end_axis=tuple(origin[k]+(1 if k==axial else 0) for k in range(3))
    count=max(1,math.ceil(abs(end_deg-start_deg)/max_step_deg))
    step=(end_deg-start_deg)/count
    report=_report('Mid-angle AABB plus rigorous radial displacement bound',moving,fixed,clearance_mm,volume_tolerance_mm3)
    report.update({'axis':axis,'axis_origin_mm':origin,'start_deg':start_deg,'end_deg':end_deg,
                   'angular_cells':count,'actual_step_deg':abs(step),'part_radius_bounds_mm':{}})
    for name,shape in moving:
        bb=bbox(shape)
        radius=math.sqrt(sum(max(abs(bb[k]-origin[k]),abs(bb[k+3]-origin[k]))**2 for k in radial))
        report['part_radius_bounds_mm'][name]=radius
        expansion=radius*math.radians(abs(step)/2)
        cache={}
        def rotated(angle):
            if angle not in cache:cache[angle]=shape.rotate(origin,end_axis,angle)
            return cache[angle]
        for i in range(count):
            lo=start_deg+i*step;hi=start_deg+(i+1)*step;mid=(lo+hi)/2
            bb_mid=bbox(rotated(mid))
            margins=[clearance_mm+(0 if k==axial else expansion) for k in range(3)]
            bounds=[bb_mid[k]-margins[k] for k in range(3)]+[bb_mid[k+3]+margins[k] for k in range(3)]
            def poses():
                if probe_candidates:
                    for angle in (lo,mid,hi):yield {'angle_deg':angle},rotated(angle)
            _test_bound(report,name,bounds,fixed,poses,exclusions or {},
                        {'angular_cell_deg':[lo,hi],'radial_expansion_mm':expansion})
    return _finish(report)
