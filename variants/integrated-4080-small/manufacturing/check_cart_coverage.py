"""Bind actual saved cart variants to consolidated purchase requirements.

This does not operate a browser or infer absent supplier prices. A nominal
size match is never a quality certificate or a delivered full-build quote.
"""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    evidence=HERE/'selected-cart-evidence.json'
    requirements=HERE/'procurement-requirements.csv'
    cart=json.loads(evidence.read_text())
    with requirements.open(newline='',encoding='utf-8-sig')as f:rows=list(csv.DictReader(f))
    results=[];used=set()
    for row in rows:
        matches=[]
        if row['category']=='SCREW' and row['head']=='socket head' and row['length_mm']:
            matches=[(i,c)for i,c in enumerate(cart['rows'])if c.get('head')=='socket'
                and c.get('thread')==row['thread']and float(c['length_mm'])==float(row['length_mm'])]
        elif row['category']=='WASHER' and row['specification']=='Flat washer OD18 ID6.4 t1.6':
            matches=[(i,c)for i,c in enumerate(cart['rows'])if c.get('category')=='WASHER'
                and c.get('required_dimensions_mm')==dict(OD=18,ID=6.4,thickness=1.6)]
        elif row['category']=='20100_PROFILE':
            matches=[(i,c)for i,c in enumerate(cart['rows'])if c.get('category')=='20100_PROFILE'
                and c.get('finished_length_mm')==1220 and c.get('raw_length_mm',0)>=1220]
        quantity=sum(c['pieces']for i,c in matches)
        required=float(row['new_required_quantity'])if row['new_required_quantity']else None
        if matches:
            assert not used.intersection(i for i,c in matches),'One cart package allocated twice'
            used.update(i for i,c in matches)
        status=('UNSTAGED'if not matches else'QUANTITY_HOLD'if required is None
                else'NOMINAL_CANDIDATE_QUANTITY_COVERED'if quantity>=required else'SHORT')
        results.append(dict(procurement_id=row['procurement_id'],category=row['category'],specification=row['specification'],
            required_quantity=required,cart_pieces=quantity,status=status,operations=row['operations'],
            cart_variants=[c['variant']for i,c in matches],
            qualification='Supplier size/quality and receipt fit acceptance remain. Washer dimensions are candidate requirements, not independently verified catalogue dimensions.'if matches else''))
    subtotal=sum(Decimal(r['extended_USD'])for r in cart['rows'])
    assert subtotal==Decimal(cart['selected_project_goods_USD'])
    result=dict(source_sha256={p.name:sha(p)for p in(evidence,requirements,Path(__file__))},
        selected_project_lines=len(cart['rows']),selected_project_packs=sum(r['pack_count']for r in cart['rows']),
        selected_goods_USD=str(subtotal),cart_shipping_display=cart['shipping_evidence'],sales_tax_USD=cart['sales_tax_USD'],
        exact_destination_shipping_confirmed=False,all_required_parts_in_cart=False,complete_delivered_build_total_USD=None,
        source_and_cart_arithmetic_passed=True,rows=results,
        unmapped_cart_variants=[c['variant']for i,c in enumerate(cart['rows'])if i not in used],
        meaning='Actual cart evidence versus source quantities only. Unstaged rows/quantity holds remain purchases to resolve; no full-cart, quality, budget or fabrication release.')
    (HERE/'cart-coverage-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(lines=len(cart['rows']),goods=str(subtotal),covered=sum(r['status']=='NOMINAL_CANDIDATE_QUANTITY_COVERED'for r in results),unstaged=sum(r['status']=='UNSTAGED'for r in results),unmapped_cart_variants=result['unmapped_cart_variants'])))

if __name__=='__main__':run()
