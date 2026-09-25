"""Rev C tube takeoff and exact bin-packing check; millimetres, 3 mm saw kerf."""
from functools import lru_cache
import json
from pathlib import Path

def pack(length_counts, stock, trim=10, kerf=3):
    lengths=sorted([round(length*10) for length,count in length_counts for _ in range(count)],reverse=True)
    pieces=[x+kerf*10 for x in lengths]
    capacity=round((stock-trim)*10)
    for count in range((sum(pieces)+capacity-1)//capacity,len(pieces)+1):
        bins=[[] for _ in range(count)]
        used=[0]*count
        failed=set()
        def place(index):
            if index==len(pieces): return True
            state=(index,tuple(sorted(used)))
            if state in failed: return False
            seen=set()
            for i in sorted(range(count), key=lambda q:used[q],reverse=True):
                if used[i] in seen or used[i]+pieces[index]>capacity: continue
                seen.add(used[i]);used[i]+=pieces[index];bins[i].append(lengths[index]/10)
                if place(index+1): return True
                bins[i].pop();used[i]-=pieces[index]
            failed.add(state)
            return False
        if place(0):
            return {'stock_length_mm':stock,'stock_qty':count,'trim_mm_per_bar':trim,
                    'kerf_mm_per_piece':kerf,'net_parts_mm':sum(lengths)/10,
                    'purchased_mm':count*stock,'net_utilization_pct':round(sum(lengths)/10/(count*stock)*100,2),
                    'bars':[{'cuts_mm':b,'net_mm':round(sum(b),3),
                             'offcut_after_trim_kerf_mm':round(stock-trim-sum(b)-len(b)*kerf,3)} for b in bins]}

main=[(1450,4),(1048.4,4),(1032.4,3),(1032,8),(949.2,6),(648.8,4)]
panel=[(497,12),(347,18)]
data={'main_20ft':pack(main,6096), 'main_12ft':pack(main,3657.6),
      'panel_20ft':pack(panel,6096),'panel_5ft':pack(panel,1524),
      'panel_metric6m':pack(panel,6000),'panel_24ft':pack(panel,7315.2)}
target=Path(__file__).with_name('cut_stock_check.json')
target.write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
