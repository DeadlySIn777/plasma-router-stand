"""Calculate the specified normally-off low-voltage run isolator limits.

This verifies a schematic, not a PCB, EMC, every transient or a safety function.
Semiconductor catalogue values are subject to their published test conditions.
"""
from pathlib import Path
import hashlib,json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    # TI's 2.3 V guaranteed high at VCC=3 V, IOH=24 mA is conservative.
    # Bound maximum LED current with zero forward drop: no invented Vf minimum.
    r=154.;tol=.01;shunt=22000.
    minimum_a=(2.3-1.5)/(r*(1+tol))-1.5/(shunt*(1-tol))
    maximum_a=3.6/(r*(1-tol))
    r_max_w=3.6**2/(r*(1-tol))
    led_max_w=1.5*maximum_a
    input_leak_v=5e-6*10000*1.01
    power_off_led_v=10e-6*shunt*1.01
    # One 24 V Finder40.52 coil. The 40 mA design cap is above catalogue
    # nominal27mA, not a guaranteed cold-coil current over all environments.
    coil_cap=.040;ron=.7;leak=1e-6
    checks={
        'LED minimum reaches recommended5mA':minimum_a>=.005,
        'Buffer output current stays below24mA guarantee':maximum_a<.024,
        'LED maximum stays below recommended30mA':maximum_a<.030,
        'Series resistor below half0.25W':r_max_w<.125,
        'LED dissipation below75mW':led_max_w<.075,
        'Input pull-down holds below specified3V lower threshold0.89V':input_leak_v<.89,
        'Unpowered buffer leakage shunted below LED forward region':power_off_led_v<.3,
        'Field steady voltage below48V recommended':26.4<48,
        'Specified one-coil cap below0.1A design limit':coil_cap<.1,
        'Catalogue reference-condition DC pickup17.5V has voltage margin':21.6-coil_cap*ron>17.5,
        'Off leakage cannot operate a nominal900ohm coil':leak*900<.1,
    }
    connections=[
        ['J_LOGIC:1','3V3'],['J_LOGIC:2','PG2'],['J_LOGIC:3','LOGIC_0'],
        ['3V3','U1:5'],['U1:3','LOGIC_0'],['3V3','C1:1'],['C1:2','LOGIC_0'],
        ['PG2','R1:1'],['R1:2','U1:2'],['U1:2','R2:1'],['R2:2','LOGIC_0'],
        ['U1:4','R3:1'],['R3:2','U2:1'],['U2:2','LOGIC_0'],
        ['U2:1','R4:1'],['R4:2','LOGIC_0'],
        ['J_FIELD:13','U2:4'],['U2:3','J_FIELD:14'],
        ['J_FIELD:13','C'],['J_FIELD:14','K_REQUEST:A1'],['K_REQUEST:A2','FIELD_0'],
        ['D1:K','K_REQUEST:A1'],['D1:A','FIELD_0'],
    ]
    parts={
        'U1':'Texas Instruments SN74LVC1G17DBVR; pin1 NC',
        'U2':'Panasonic AQY212GS; pins1/2 LED; pins3/4 NO output',
        'R1':'1kohm1%0.25W series at GPIO',
        'R2':'10kohm1%0.25W buffer-input pull-down',
        'R3':'154ohm1%0.25W LED series resistor',
        'R4':'22kohm1%0.25W across LED',
        'C1':'100nF X7R 16V atU1 supply pins',
        'D1':'1N4007 at request-relay coil; cathode towardA1',
        'K_REQUEST':'Finder40.52.9.024.0000 with95.05 socket, included in control inventory',
    }
    sources={
        'U1':'https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',
        'U2':'https://industry.panasonic.com/ac/cdn/e/control/relay/photomos/catalog/semi_eng_gu1a_aqy21_gs.pdf',
        'K_REQUEST':'https://cdn.findernet.com/app/uploads/S40EN.pdf',
    }
    report={'status':'SCHEMATIC_SCREEN_PASS' if all(checks.values()) else 'FAIL',
        'scope':__doc__,'checks':checks,'connections':connections,'parts':parts,'sources':sources,
        'calculated':{'LED_min_mA':minimum_a*1000,'LED_max_mA_zero_Vf_bound':maximum_a*1000,
            'series_resistor_max_W':r_max_w,'LED_power_bound_W':led_max_w,
            'input_open_voltage_bound_V':input_leak_v,'unpowered_LED_voltage_bound_V':power_off_led_v,
            'specified_coil_current_limit_mA':coil_cap*1000,'output_drop_at_limit_V':coil_cap*ron},
        'limits':['No copper layout, creepage/clearance qualification, EMC or PCB fabrication release.',
            '5ms turn-on and0.5ms turn-off are catalogue25C test values; verify actual board, supply, load and temperature.',
            'No floating-ground connection; field and controller returns remain separate.',
            'An output short can hold K_REQUEST on. Hardware permission removal still gates tool relay coils; this is not redundant safety logic.',
            'GPIO high glitches may be valid run requests after arming. Verify boot/reset/shutdown waveforms with actual firmware and hardware.',
            'Intended only for24V command coil, never raw plasma voltage, mains, motor power or5kHz speed PWM.'],
        'source_sha256':{Path(__file__).name:hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'artifact_sha256':{(OUT/'RUN-INTERFACE.md').relative_to(ROOT).as_posix():
                           hashlib.sha256((OUT/'RUN-INTERFACE.md').read_bytes()).hexdigest()}}
    (OUT/'run-interface.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert all(checks.values()),checks
    print(report['status'],len(checks),'checks',json.dumps(report['calculated']),flush=True)


if __name__=='__main__':main()
