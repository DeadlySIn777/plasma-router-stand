/* Kraken V1.1 engineering port, GPL-3.0-or-later, 2026.
 * Pin source: BIGTREETECH Kraken schematic + official generic Klipper map.
 * X=S1, Y=S2, Y2=M3=S3, Z=S4. Only these four 50mOhm channels are enabled.
 * NOT for Kraken V1.0 (22mOhm); no solder modifications required.
 */
#if !defined(STM32H723xx) || HSE_VALUE != 25000000
#error "Kraken requires STM32H723 and a 25MHz crystal"
#endif
#if N_AXIS != 3 || N_ABC_MOTORS != 1 || !Y_AUTO_SQUARE
#error "This port is exclusively XYZ with one independent auto-squared Y motor"
#endif
#define BOARD_NAME "Kraken V1.1 XYYZ engineering"
#define BOARD_URL "https://github.com/bigtreetech/BIGTREETECH-Kraken"
#define SERIAL_PORT 32  // SBC header PD8/PD9; USB CDC is the selected host transport.
#define STEP_OUTMODE GPIO_SINGLE
#define DIRECTION_OUTMODE GPIO_SINGLE
#define LIMIT_INMODE GPIO_SINGLE

#define X_STEP_PORT GPIOC
#define X_STEP_PIN 14
#define X_DIRECTION_PORT GPIOC
#define X_DIRECTION_PIN 13
#define X_ENABLE_PORT GPIOE
#define X_ENABLE_PIN 6
#define X_LIMIT_PORT GPIOC
#define X_LIMIT_PIN 15

#define Y_STEP_PORT GPIOE
#define Y_STEP_PIN 5
#define Y_DIRECTION_PORT GPIOE
#define Y_DIRECTION_PIN 4
#define Y_ENABLE_PORT GPIOE
#define Y_ENABLE_PIN 3
#define Y_LIMIT_PORT GPIOF
#define Y_LIMIT_PIN 0

#define Z_STEP_PORT GPIOB
#define Z_STEP_PIN 9
#define Z_DIRECTION_PORT GPIOB
#define Z_DIRECTION_PIN 8
#define Z_ENABLE_PORT GPIOB
#define Z_ENABLE_PIN 7
#define Z_LIMIT_PORT GPIOF
#define Z_LIMIT_PIN 2

#define M3_AVAILABLE
#define M3_STEP_PORT GPIOE
#define M3_STEP_PIN 2
#define M3_DIRECTION_PORT GPIOE
#define M3_DIRECTION_PIN 1
#define M3_ENABLE_PORT GPIOE
#define M3_ENABLE_PIN 0
#define M3_LIMIT_PORT GPIOF
#define M3_LIMIT_PIN 1

#define TRINAMIC_R_SENSE 50 // milliohms, Kraken V1.1 S1-S4 only
#define TRINAMIC_SOFT_SPI
#define TRINAMIC_MOSI_PORT GPIOC
#define TRINAMIC_MOSI_PIN 8
#define TRINAMIC_MISO_PORT GPIOC
#define TRINAMIC_MISO_PIN 7
#define TRINAMIC_SCK_PORT GPIOC
#define TRINAMIC_SCK_PIN 6
#define MOTOR_CSX_PORT GPIOD
#define MOTOR_CSX_PIN 6
#define MOTOR_CSY_PORT GPIOD
#define MOTOR_CSY_PIN 5
#define MOTOR_CSZ_PORT GPIOD
#define MOTOR_CSZ_PIN 3
#define MOTOR_CSM3_PORT GPIOD
#define MOTOR_CSM3_PIN 4

// Free aux inputs deliberately first: isolated Arc OK / DOWN / UP.
// EXP1 has raw logic connections; interface outputs must be 3.3V-compatible.
#define AUXINPUT0_PORT GPIOD // EXP1 pin 8: Arc OK
#define AUXINPUT0_PIN 12
#define AUXINPUT1_PORT GPIOD // EXP1 pin 7: THC DOWN
#define AUXINPUT1_PIN 13
#define AUXINPUT2_PORT GPIOD // EXP1 pin 6: THC UP
#define AUXINPUT2_PIN 14
#define AUXINPUT3_PORT GPIOG // EXP1 pin 2: hardware stop-chain status
#define AUXINPUT3_PIN 4
#define AUXINPUT4_PORT GPIOG // EXP1 pin 3: feed hold
#define AUXINPUT4_PIN 3
#define AUXINPUT5_PORT GPIOG // EXP1 pin 1: cycle start
#define AUXINPUT5_PIN 5
#define AUXINPUT6_PORT GPIOE // EXP2 pin 4: floating head/router probe
#define AUXINPUT6_PIN 11
#define AUXINPUT7_PORT GPIOG // EXP2 pin 7: breakaway/door/machine-permissive status
#define AUXINPUT7_PIN 6

#define RESET_PORT AUXINPUT3_PORT
#define RESET_PIN AUXINPUT3_PIN
#define FEED_HOLD_PORT AUXINPUT4_PORT
#define FEED_HOLD_PIN AUXINPUT4_PIN
#define CYCLE_START_PORT AUXINPUT5_PORT
#define CYCLE_START_PIN AUXINPUT5_PIN
#define PROBE_PORT AUXINPUT6_PORT
#define PROBE_PIN AUXINPUT6_PIN
#define SAFETY_DOOR_PORT AUXINPUT7_PORT
#define SAFETY_DOOR_PIN AUXINPUT7_PIN

// A keyed hardware mode circuit routes this dry-interface request to one tool.
// Outputs are logic signals to isolators, never direct VFD/torch connections.
#define AUXOUTPUT0_PORT GPIOG // EXP1 pin 4: spindle/torch enable
#define AUXOUTPUT0_PIN 2
#define SPINDLE_ENABLE_PORT AUXOUTPUT0_PORT
#define SPINDLE_ENABLE_PIN AUXOUTPUT0_PIN
#if DRIVER_SPINDLE_ENABLE & SPINDLE_PWM
#define AUXOUTPUT1_PORT GPIOE // BLTouch SERVO pin: isolated PWM-to-0..10V module
#define AUXOUTPUT1_PIN 9
#define SPINDLE_PWM_PORT AUXOUTPUT1_PORT
#define SPINDLE_PWM_PIN AUXOUTPUT1_PIN
#endif

// Unused integrated channels share the SPI bus and must remain deselected.
#define HAS_BOARD_INIT
void board_init(void);
