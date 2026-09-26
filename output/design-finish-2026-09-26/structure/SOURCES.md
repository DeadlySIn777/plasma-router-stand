# Primary references and calculation assumptions

Checked 26 September 2026. These sources support material constants and equation
bases; none certifies the owner's scrap, purchased hardware, extrusion profile,
welds or complete machine.

- [AISC 360-16 specification and commentary](https://www.aisc.org/globalassets/aisc/publications/standards/a360-16-spec-and-commentary_june-2019_linked.pdf): steel elastic modulus 200,000 MPa. The report uses elastic member equations in consistent N/mm units, not an assertion of building-code compliance.
- [Steel Tube Institute: ASTM A500](https://steeltubeinstitute.org/resources/astm-a500/): A500 wall tolerance and the 0.93 nominal-to-design-wall factor. The actual scrap grade is unknown, so no Grade C strength is credited; the 245 MPa steel yield screen is a conditional design assumption below nominal A36 minimum.
- [Steel Tube Institute: HSS geometry / section-property convention](https://steeltubeinstitute.org/wp-content/uploads/2024/06/STI-Filling-the-Void-Concrete-Filled-HSS-Columns-061924.pdf): the cited property convention uses corner radius 2× design thickness. The calculator explicitly builds a rounded tube with outer radius2t and inner radius1t; measured unusual corners require recalculation.
- [Hydro EN AW-6063 technical datasheet](https://www.hydro.com/Document/Index?id=7823&name=Hydro+EN+AW+6063.PDF): elastic modulus 69 GPa. The profile's section properties are computed from the existing reconstructed CAD, not taken from a certified extrusion table.
- [Hydro North America 6063 mechanical limits](https://www.hydro.com/globalassets/01-products--services/extruded-profiles/americas/ena-resources/alloy-data-sheets/hydro_2019_data_sheet_6063.pdf): 6063-T5 strength varies with product thickness/condition. The report uses a conditional 110 MPa slot-lip yield screen and requires testing the actual profile; the source does not establish the Amazon product's alloy/temper.
- [Bossard screw material/property-class tables](https://www.bossard.com/-/media/bossard-group/website/documents/technical-resources_old/screws-property-class-46-to-129.pdf): metric tensile stress areas and class 8.8 proof properties. M6 and M8 use 20.1 and 36.6 mm²; the screen uses 580 MPa proof stress for the relevant diameters.
- [Bossard arrangement, design and assembly guidance](https://media.bossard.com/hr-en/-/media/bossard-group/website/documents/technical-resources/en/f-047-en.pdf): bolt preload/torque depends on friction and assembly conditions. The chosen low-force targets are design inputs, not values quoted from a standard torque table.
- [AISC Weld Reliability Analysis](https://www.aisc.org/globalassets/aisc/research-library/210005_dowswell-weld-reliability-study/aisc-frr-2024-02_dowswell-weld-reliability-analysis.pdf): identifies the fillet-weld nominal stress basis0.60FEXX and ASD divisor2.00. The calculator uses these for a nominal weld-metal screen, with equal-leg geometric throat a/√2 and no directional strength increase.

The required rod yield of at least 300 MPa is an explicit procurement
acceptance requirement, not a claimed property of an unidentified rod. The
100 N routing load, 0.20 mm static target, 500 N local/external proof scenarios,
650 kg maximum support case, 25 kg stock limit, friction0.15 and 15% mass
sensitivity are engineering assumptions selected for this study. They must be
revisited when the actual hardware, stock, support surface and use are known.

The slot-lip model is an independently derived infinite beam on an elastic
foundation: EI w'''' + k w = Pδ(x); β=(k/4EI)^(1/4), peak combined lip reaction
q(0)=Pβ/2. Each of two lips receives half that reaction. Its local cantilever
stress is therefore 1.5Pβa/t². This idealized contact model does not resolve the
supplier's unmeasured fillets, local end effects, preload contact state or MDF
compression. The coupon test in JOINTS.md is required before assigning an
assembly setting.
