# Rev I low-voltage terminal connections

Generated from circuit.py. Wires are point-to-point; contact rows specify the device terminals between them. These circuits use only isolated 24 V control power. Tool-output pairs remain floating. Read the controls README before fabrication.

Factory contact form and logical closed condition are separate columns. For SETUP_RUN, the physical NC contact closes when setup=true, while the physical NO contact closes when setup=false. XW/XH rows with unspecified device form describe field-loop continuity only. MODE_R/MODE_P and BED_R/BED_P identify separate blocks on one head; each block uses the manufacturer-listed 13/14 terminals, not an invented 23/24 stamping. Verify positions by continuity before fitting labels.

| Tag | Type | From | To | Physical contact form | Closed condition | Device |
|---|---|---|---|---|---|---|
| W001 | wire | 24V | XW:1 | - | - | - |
| W002 | wire | XW:1 | F_CONTROL:1 | - | - | - |
| W003 | wire | F_CONTROL:2 | XW:3 | - | - | - |
| W004 | wire | XW:3 | C | - | - | - |
| W005 | wire | XW:1 | F_VALVE:1 | - | - | - |
| W006 | wire | F_VALVE:2 | XW:4 | - | - | - |
| W007 | wire | XW:4 | V | - | - | - |
| W008 | wire | C | MODE_R:13 | - | - | - |
| W009 | wire | MODE_R:14 | MR | - | - | - |
| W010 | wire | C | MODE_P:13 | - | - | - |
| W011 | wire | MODE_P:14 | MP | - | - | - |
| W012 | wire | MR | KM_P:41 | - | - | - |
| W013 | wire | KM_P:42 | KMR_COIL | - | - | - |
| W014 | wire | KMR_COIL | KM_R:A1 | - | - | - |
| W015 | wire | KM_R:A2 | XW:2 | - | - | - |
| W016 | wire | MP | KM_R:41 | - | - | - |
| W017 | wire | KM_R:42 | KMP_COIL | - | - | - |
| W018 | wire | KMP_COIL | KM_P:A1 | - | - | - |
| W019 | wire | KM_P:A2 | XW:2 | - | - | - |
| W020 | wire | C | XW:11 | - | - | - |
| W021 | wire | XW:12 | EMPTY_COIL | - | - | - |
| W022 | wire | EMPTY_COIL | K_EMPTY:A1 | - | - | - |
| W023 | wire | K_EMPTY:A2 | XW:2 | - | - | - |
| W024 | wire | C | XW:13 | - | - | - |
| W025 | wire | XW:14 | MIN_COIL | - | - | - |
| W026 | wire | MIN_COIL | K_MIN:A1 | - | - | - |
| W027 | wire | K_MIN:A2 | XW:2 | - | - | - |
| W028 | wire | C | XW:21 | - | - | - |
| W029 | wire | XW:22 | STOP_HEALTHY | - | - | - |
| W030 | wire | STOP_HEALTHY | XW:17 | - | - | - |
| W031 | wire | XW:18 | H | - | - | - |
| W032 | wire | C | KM_R:11 | - | - | - |
| W033 | wire | KM_R:14 | DR_REQ | - | - | - |
| W034 | wire | C | AUTO_DRAIN:13 | - | - | - |
| W035 | wire | AUTO_DRAIN:14 | DO_REQ | - | - | - |
| W036 | wire | DRAIN_COIL | K_DRAIN:A1 | - | - | - |
| W037 | wire | K_DRAIN:A2 | XW:2 | - | - | - |
| W038 | wire | V | K_DRAIN:11 | - | - | - |
| W039 | wire | K_DRAIN:14 | DV | - | - | - |
| W040 | wire | DV | XW:7 | - | - | - |
| W041 | wire | XW:8 | XW:2 | - | - | - |
| W042 | wire | C | KM_P:11 | - | - | - |
| W043 | wire | KM_P:14 | PCLOSE | - | - | - |
| W044 | wire | PCLOSE | K_DRAIN:21 | - | - | - |
| W045 | wire | K_DRAIN:22 | TC_POWER | - | - | - |
| W046 | wire | TC_POWER | T_CLOSE:A1 | - | - | - |
| W047 | wire | T_CLOSE:A2 | XW:2 | - | - | - |
| W048 | wire | H | KM_P:21 | - | - | - |
| W049 | wire | KM_P:24 | P_HEALTHY | - | - | - |
| W050 | wire | P_HEALTHY | XW:23 | - | - | - |
| W051 | wire | XW:23 | BED_P:13 | - | - | - |
| W052 | wire | BED_P:14 | XW:24 | - | - | - |
| W053 | wire | XW:24 | P_CLEAR | - | - | - |
| W054 | wire | P_CLEAR | T_CLOSE:15 | - | - | - |
| W055 | wire | T_CLOSE:18 | PC | - | - | - |
| W056 | wire | PC | R_TC:1 | - | - | - |
| W057 | wire | R_TC:2 | XW:2 | - | - | - |
| W058 | wire | PC | SETUP_RUN:21 | - | - | - |
| W059 | wire | SETUP_RUN:22 | SETUP_PC | - | - | - |
| W060 | wire | SETUP_PC | XW:19 | - | - | - |
| W061 | wire | XW:20 | L | - | - | - |
| W062 | wire | L | P_LIMIT:A1 | - | - | - |
| W063 | wire | P_LIMIT:A2 | XW:2 | - | - | - |
| W064 | wire | L | XW:15 | - | - | - |
| W065 | wire | XW:16 | A | - | - | - |
| W066 | wire | A | FILL:21 | - | - | - |
| W067 | wire | FILL:22 | ARM_COIL | - | - | - |
| W068 | wire | A | K_ARM:11 | - | - | - |
| W069 | wire | K_ARM:14 | ARM_COIL | - | - | - |
| W070 | wire | ARM_COIL | K_ARM:A1 | - | - | - |
| W071 | wire | K_ARM:A2 | XW:2 | - | - | - |
| W072 | wire | A | K_ARM:21 | - | - | - |
| W073 | wire | K_ARM:24 | AF | - | - | - |
| W074 | wire | AF | FILL:13 | - | - | - |
| W075 | wire | FILL:14 | FILL_COIL | - | - | - |
| W076 | wire | AF | K_FILL:11 | - | - | - |
| W077 | wire | K_FILL:14 | FILL_COIL | - | - | - |
| W078 | wire | FILL_COIL | K_FILL:A1 | - | - | - |
| W079 | wire | K_FILL:A2 | XW:2 | - | - | - |
| W080 | wire | FILL_COIL | P_CMD:A1 | - | - | - |
| W081 | wire | P_CMD:A2 | XW:2 | - | - | - |
| W082 | wire | DV | KM_R:21 | - | - | - |
| W083 | wire | KM_R:24 | RD | - | - | - |
| W084 | wire | RD | K_EMPTY:21 | - | - | - |
| W085 | wire | K_EMPTY:24 | TD_POWER | - | - | - |
| W086 | wire | TD_POWER | T_DRAIN:A1 | - | - | - |
| W087 | wire | T_DRAIN:A2 | XW:2 | - | - | - |
| W088 | wire | H | XW:25 | - | - | - |
| W089 | wire | XW:25 | BED_R:13 | - | - | - |
| W090 | wire | BED_R:14 | XW:26 | - | - | - |
| W091 | wire | XW:26 | R_LOCKED | - | - | - |
| W092 | wire | R_LOCKED | K_EMPTY:11 | - | - | - |
| W093 | wire | K_EMPTY:14 | RE | - | - | - |
| W094 | wire | RE | T_DRAIN:15 | - | - | - |
| W095 | wire | T_DRAIN:18 | RR | - | - | - |
| W096 | wire | RR | R_TD:1 | - | - | - |
| W097 | wire | R_TD:2 | XW:2 | - | - | - |
| W098 | wire | PC | K_MIN:11 | - | - | - |
| W099 | wire | K_MIN:14 | PR | - | - | - |
| W100 | wire | J | K_FILL:21 | - | - | - |
| W101 | wire | K_FILL:22 | NOT_FILL | - | - | - |
| W102 | wire | NOT_FILL | SETUP_RUN:13 | - | - | - |
| W103 | wire | SETUP_RUN:14 | RUN_READY | - | - | - |
| W104 | wire | RUN_READY | AUTO_DRAIN:21 | - | - | - |
| W105 | wire | AUTO_DRAIN:22 | READY_COIL | - | - | - |
| W106 | wire | READY_COIL | K_READY:A1 | - | - | - |
| W107 | wire | K_READY:A2 | XW:2 | - | - | - |
| W108 | wire | HEAD_SAFE | XW:31 | - | - | - |
| W109 | wire | XW:31 | K_READY:11 | - | - | - |
| W110 | wire | K_READY:14 | XW:32 | - | - | - |
| W111 | wire | XW:32 | IF_READY:IN+ | - | - | - |
| W112 | wire | IF_READY:IN- | XW:2 | - | - | - |
| W113 | wire | C | XH:1 | - | - | - |
| W114 | wire | XH:2 | HARD_SAFE | - | - | - |
| W115 | wire | HARD_SAFE | XH:3 | - | - | - |
| W116 | wire | XH:4 | DOOR_SAFE | - | - | - |
| W117 | wire | DOOR_SAFE | XH:5 | - | - | - |
| W118 | wire | XH:6 | HEAD_SAFE | - | - | - |
| W119 | wire | HEAD_SAFE | XW:33 | - | - | - |
| W120 | wire | XW:33 | K_READY:21 | - | - | - |
| W121 | wire | K_READY:24 | XW:34 | - | - | - |
| W122 | wire | XW:34 | PERMIT | - | - | - |
| W123 | wire | C | IF_RUN:13 | - | - | - |
| W124 | wire | IF_RUN:14 | REQUEST_COIL | - | - | - |
| W125 | wire | REQUEST_COIL | K_REQUEST:A1 | - | - | - |
| W126 | wire | K_REQUEST:A2 | XW:2 | - | - | - |
| W127 | wire | PERMIT | K_REQUEST:11 | - | - | - |
| W128 | wire | K_REQUEST:12 | RUN_ARM_COIL | - | - | - |
| W129 | wire | PERMIT | K_RUN_ARM:11 | - | - | - |
| W130 | wire | K_RUN_ARM:14 | RUN_ARM_COIL | - | - | - |
| W131 | wire | RUN_ARM_COIL | K_RUN_ARM:A1 | - | - | - |
| W132 | wire | K_RUN_ARM:A2 | XW:2 | - | - | - |
| W133 | wire | PERMIT | K_RUN_ARM:21 | - | - | - |
| W134 | wire | K_RUN_ARM:24 | ARMED_PERMIT | - | - | - |
| W135 | wire | ARMED_PERMIT | K_REQUEST:21 | - | - | - |
| W136 | wire | K_REQUEST:24 | REQUEST | - | - | - |
| W137 | wire | REQUEST | KM_R:31 | - | - | - |
| W138 | wire | KM_R:34 | VFD_RUN_COIL | - | - | - |
| W139 | wire | VFD_RUN_COIL | K_VFD_RUN:A1 | - | - | - |
| W140 | wire | K_VFD_RUN:A2 | XW:2 | - | - | - |
| W141 | wire | REQUEST | KM_P:31 | - | - | - |
| W142 | wire | KM_P:34 | TORCH_RUN_COIL | - | - | - |
| W143 | wire | TORCH_RUN_COIL | K_TORCH_RUN:A1 | - | - | - |
| W144 | wire | K_TORCH_RUN:A2 | XW:2 | - | - | - |
| F_CONTROL | contact | F_CONTROL:1 | F_CONTROL:2 | Fuse continuity | f_control = true | - |
| F_VALVE | contact | F_VALVE:1 | F_VALVE:2 | Fuse continuity | f_valve = true | - |
| MODE_R:13-14 | contact | MODE_R:13 | MODE_R:14 | NO | router = true | MODE / Schneider XB5AD33, router block |
| MODE_P:13-14 | contact | MODE_P:13 | MODE_P:14 | NO | plasma = true | MODE / Schneider XB5AD33, plasma block |
| KM_P:41-42 | contact | KM_P:41 | KM_P:42 | NC | KM_P = false | - |
| KM_R:41-42 | contact | KM_R:41 | KM_R:42 | NC | KM_R = false | - |
| XW:11-12 | contact | XW:11 | XW:12 | External closure; device form unspecified | empty = true | - |
| XW:13-14 | contact | XW:13 | XW:14 | External closure; device form unspecified | minimum = true | - |
| XW:21-22 | contact | XW:21 | XW:22 | External closure; device form unspecified | stop_ok = true | - |
| XW:17-18 | contact | XW:17 | XW:18 | External closure; device form unspecified | high_high_healthy = true | - |
| KM_R:11-14 | contact | KM_R:11 | KM_R:14 | NO | KM_R = true | - |
| AUTO_DRAIN:13-14 | contact | AUTO_DRAIN:13 | AUTO_DRAIN:14 | NO | drain_override = true | Schneider XB5AD25 |
| K_DRAIN:11-14 | contact | K_DRAIN:11 | K_DRAIN:14 | NO | K_DRAIN = true | - |
| KM_P:11-14 | contact | KM_P:11 | KM_P:14 | NO | KM_P = true | - |
| K_DRAIN:21-22 | contact | K_DRAIN:21 | K_DRAIN:22 | NC | K_DRAIN = false | - |
| KM_P:21-24 | contact | KM_P:21 | KM_P:24 | NO | KM_P = true | - |
| BED_P:13-14 | contact | BED_P:13 | BED_P:14 | NO | bed_clear = true | BED_CONFIRM / Schneider XB5AG03, plasma block |
| T_CLOSE:15-18 | contact | T_CLOSE:15 | T_CLOSE:18 | NO | T_CLOSE = true | - |
| SETUP_RUN:21-22 | contact | SETUP_RUN:21 | SETUP_RUN:22 | NC | setup = true | Schneider XB5AD25 |
| XW:19-20 | contact | XW:19 | XW:20 | External closure; device form unspecified | reservoir_healthy = true | - |
| XW:15-16 | contact | XW:15 | XW:16 | External closure; device form unspecified | fill_stop_healthy = true | - |
| FILL:21-22 | contact | FILL:21 | FILL:22 | NC | fill_pressed = false | Schneider XB5AA35 |
| K_ARM:11-14 | contact | K_ARM:11 | K_ARM:14 | NO | K_ARM = true | - |
| K_ARM:21-24 | contact | K_ARM:21 | K_ARM:24 | NO | K_ARM = true | - |
| FILL:13-14 | contact | FILL:13 | FILL:14 | NO | fill_pressed = true | Schneider XB5AA35 |
| K_FILL:11-14 | contact | K_FILL:11 | K_FILL:14 | NO | K_FILL = true | - |
| KM_R:21-24 | contact | KM_R:21 | KM_R:24 | NO | KM_R = true | - |
| K_EMPTY:21-24 | contact | K_EMPTY:21 | K_EMPTY:24 | NO | K_EMPTY = true | - |
| BED_R:13-14 | contact | BED_R:13 | BED_R:14 | NO | bed_locked = true | BED_CONFIRM / Schneider XB5AG03, router block |
| K_EMPTY:11-14 | contact | K_EMPTY:11 | K_EMPTY:14 | NO | K_EMPTY = true | - |
| T_DRAIN:15-18 | contact | T_DRAIN:15 | T_DRAIN:18 | NO | T_DRAIN = true | - |
| K_MIN:11-14 | contact | K_MIN:11 | K_MIN:14 | NO | K_MIN = true | - |
| K_FILL:21-22 | contact | K_FILL:21 | K_FILL:22 | NC | K_FILL = false | - |
| SETUP_RUN:13-14 | contact | SETUP_RUN:13 | SETUP_RUN:14 | NO | setup = false | Schneider XB5AD25 |
| AUTO_DRAIN:21-22 | contact | AUTO_DRAIN:21 | AUTO_DRAIN:22 | NC | drain_override = false | Schneider XB5AD25 |
| K_READY:11-14 | contact | K_READY:11 | K_READY:14 | NO | K_READY = true | - |
| XH:1-2 | contact | XH:1 | XH:2 | External closure; device form unspecified | hardware_stop_ok = true | - |
| XH:3-4 | contact | XH:3 | XH:4 | External closure; device form unspecified | door_closed = true | - |
| XH:5-6 | contact | XH:5 | XH:6 | Normally-off PhotoMOS | breakaway_seated = true | U_HEAD / Panasonic AQY212GS output; head-interface.json |
| K_READY:21-24 | contact | K_READY:21 | K_READY:24 | NO | K_READY = true | - |
| IF_RUN:13-14 | contact | IF_RUN:13 | IF_RUN:14 | Normally-off PhotoMOS | run_request = true | Panasonic AQY212GS output; interface terminal numbers |
| K_REQUEST:11-12 | contact | K_REQUEST:11 | K_REQUEST:12 | NC | K_REQUEST = false | - |
| K_RUN_ARM:11-14 | contact | K_RUN_ARM:11 | K_RUN_ARM:14 | NO | K_RUN_ARM = true | - |
| K_RUN_ARM:21-24 | contact | K_RUN_ARM:21 | K_RUN_ARM:24 | NO | K_RUN_ARM = true | - |
| K_REQUEST:21-24 | contact | K_REQUEST:21 | K_REQUEST:24 | NO | K_REQUEST = true | - |
| KM_R:31-34 | contact | KM_R:31 | KM_R:34 | NO | KM_R = true | - |
| KM_P:31-34 | contact | KM_P:31 | KM_P:34 | NO | KM_P = true | - |
| K_VFD_RUN:11-14 | contact | XVFD:RUN | XVFD:COM | NO | K_VFD_RUN = true | - |
| K_TORCH_RUN:11-14 | contact | XPLASMA:START1 | XPLASMA:START2 | NO | K_TORCH_RUN = true | - |
| D_R | diode | DR_REQ | DRAIN_COIL | - | - | - |
| D_O | diode | DO_REQ | DRAIN_COIL | - | - | - |
| D_R_READY | diode | RR | J | - | - | - |
| D_P_READY | diode | PR | J | - | - | - |
