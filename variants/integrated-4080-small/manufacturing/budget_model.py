"""Dated selected-source costs; unquoted charges stay unknown."""
from pathlib import Path
from decimal import Decimal
import json

HERE=Path(__file__).resolve().parent

def current_budget():
    cart=json.loads((HERE/'selected-cart-evidence.json').read_text())
    tracks=[r for r in cart['rows']if r.get('category')=='20100_PROFILE']
    track_total=sum(Decimal(r['extended_USD'])for r in tracks)
    hardware=sum(Decimal(r['extended_USD'])for r in cart['rows']if r not in tracks)
    assert track_total==Decimal('342.97') and hardware==Decimal('112.08')
    rows=[
        dict(id='20100_BED',quantity=1,unit='mixed raw-stock set supplying10 finished1220mmtracks',unit_USD=str(track_total),
            extended_USD=str(track_total),url='https://www.amazon.com/dp/B0DY7JYQCJ',
            shipping='Observed freePrime to30510',selected_case='required',pack_breakdown=tracks,
            scope='Eight1500mmtracks fromtwo4packs@129.99 plusone1220mmtwopack@82.99. Saw8to1220; fit/straightness/nut acceptance held. Cart1500deliveryDec9–24,1220Nov9; no universal shipping guarantee.'),
        dict(id='HDPE_RAW',quantity=1,unit='48x48x1/2in recycled black sheet SKU42707',unit_USD='191.86',extended_USD='191.86',
            url='https://www.usplastic.com/catalog/item.aspx?itemid=127310',shipping='UNKNOWN_NOT_ZERO',selected_case='required_candidate',
            scope='One1000x1200x12.7nominal finishedlayer. Suppliercut±6.35mm andthickness±10%; actualthickness/cleanup/flatness inspection required. Freight andtax unknown. Replacesoldtwo-layer48x96purchase.'),
        dict(id='RAPIDCHANGE_BASIC4',quantity=1,unit='4pocket ER11 Basic',unit_USD='400.00',extended_USD='400.00',
            url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',shipping='UNKNOWN_NOT_ZERO',selected_case='minimum_basic',
            scope='PrimarypageBasic400; requiresreverse-capablespindleandtoolsetter. Basiclacksdetection/cover. CustompassivecoverisintheCAD; actualsocket/nut/sensing/controlinterfaceheld.'),
        dict(id='STAGED_NEW_HARDWARE',quantity=1,unit='dated13AliExpress+1Amazonhardwarevariants',unit_USD=str(hardware),extended_USD=str(hardware),
            url='https://www.amazon.com/dp/B0F99JRW8G',shipping='Amazon freePrime30510; Ali cart free butexactAltoaddressunconfirmed',selected_case='required_partial',
            scope='Ali13variants78.32 plus80Amazon100mmM5screws33.76, finished99.3±.1. Otherhardwarestillunselected. IncludedBNUOKnuts/washersareunallocatedextras; no doublecredit.'),
        dict(id='RAPIDCHANGE_TOOLSETTER',quantity=1,unit='opticaltoolsetter candidate',unit_USD='50.00',extended_USD='50.00',
            url='https://rapidchangeatc.com/shop/automatic-tool-changer/linear-magazines/',shipping='UNKNOWN_NOT_ZERO',selected_case='required_unless_existing_qualified_probe',
            scope='Manufacturerrequirestoolsetter; exactintegrationandfullstate-sensinghardwarestillheld. No unverifiedownedprobecredit.'),
        dict(id='USS_MSV00009_DRAIN_VALVE',quantity=1,unit='1inNPT9–24VmotorizedNCvalve',unit_USD='50.42',extended_USD='50.42',
            url='https://ussolid.com/products/u-s-solid-motorized-ball-valve-1-stainless-steel-electrical-ball-valve-with-full-port-9-24-v-ac-dc-2-wire-auto-return-html',
            shipping='UNKNOWN_NOT_ZERO',selected_case='required_drain_candidate',scope='Existingofficialsourceprice; actualunions/fittings/supports/valvefitheld.'),
    ]
    core=track_total+Decimal('191.86')+Decimal('400')
    subset=core+hardware
    known=subset+Decimal('50')
    assert core==Decimal('934.83') and subset==Decimal('1046.91') and known==Decimal('1096.91')
    return dict(observed_date='2026-11-05',last_reconciled_date='2026-11-05',currency='USD',delivery_price_region='30510',
        basis='Dated primary source/cart observations. Selected source case only; not a universal market floor. Actual owned equipment and exclusive sheets excluded; missing costs are not zero.',
        rows=rows,three_core_goods_basis_USD=str(core),core_goods_saving_vs_baseline_USD='90.87',
        core_remaining_to_cap_before_other_goods_USD='65.17',
        known_core_plus_staged_hardware_goods_subset_USD=str(subset),
        known_basic_goods_subset_USD=str(known),known_basic_with_drain_valve_goods_subset_USD=str(known+Decimal('50.42')),
        known_preferred_ProIR_goods_subset_USD=None,
        detection_upgrade_price_conflict=dict(linear_product_page_addition_USD='100.00',new_shop_page_Pro_total_USD='550.00',
            qualified_selected_upgrade_USD=None,rule='Resolve actual checkoutconfiguration; neitherconflictingpriceis silentlytreatedasafinalquote.'),
        gas_spring_requirement=dict(force_N_each=667,nominal_lb_each=150,quantity=2,compressed_eye_length_max_mm=445,extended_eye_length_min_mm=700,
            selected_verified_offer=None,goods_USD=None,old_200lb_offer_selected=False),
        budget_cap_USD='1000.00',budget_gate='FAIL',minimum_three_item_goods_over_cap_USD='0.00',
        known_core_and_staged_hardware_over_cap_USD=str(subset-Decimal('1000')),
        complete_delivered_total_USD=None,shipping_tax_total_USD=None,
        all_required_parts_in_cart=False,
        missing_costs=['All4080stock/cutallowance/packrounding/freight, includingtwo1760mmcontinuousheaders',
            'Pan/slats/reservoir/drainfittings/hose/thermalguards and associatedsteel/consumables',
            'New1202x114x6.35minimumgantryfaceblank,Zcarrier/supportbillet,gantry/hinge/ATCcustomstocknotcoveredbyexclusiveownednests',
            'Matched150lbgaspair,mounts,pins/retainers,remainingfasteners/slotnuts/feet/workholding',
            'ATCnut/collet/toolcontents,state-sensing/cabling/chain/glands/bondingnotverifiedowned',
            'Allunquotedshipping/freight/tax/cutting/finishing and physicalfitselectioncosts'],
        pricing_scope='Core934.83; coreplusalready-stagedhardware1046.91beforeany4080frame/pan/freight. Full1000deliveredrequirementisnotachieved. No purchase, physical qualification or operating release implied.')
