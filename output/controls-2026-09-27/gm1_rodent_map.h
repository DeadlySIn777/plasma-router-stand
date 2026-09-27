/*
  gm1_rodent_map.h - GM1 board map for the BTT Rodent V1.1, derived from grblHAL's
  ESP32 main/boards/btt_rodent_map.h (Terje Io, GPLv3; see that file for the licence).

  DRAFT - NOT COMPILED, NOT FLASHED. It records the GM1 pin allocation in the
  form grblHAL expects. See RODENT-IO.md for the reasons and the open items.

  Changes from btt_rodent_map.h:
  - No RS485/Modbus: GPIO15 (RS485 TX) becomes the arc-OK input and GPIO14
    (RS485 direction) the THCAD-300 frequency input. The VFD takes run through its FWD
    terminal (GM1 relay panel) and speed through the SP-PWM 0-10 V output and an
    isolated signal conditioner.
  - E1-MAX (GPIO39 on V1.1, GPIO37 on V1.0) is the safety-door input, fed
    by the GM1 panel's dry "request not armed" contacts.
  - The E-stop has no input: the safety relay removes the Rodent's 48 V, so
    the board restarts after every stop and must be homed again.
  - Spindle direction moves to V-MOS HE1 (GPIO2), since GPIO15 is an input here. It drives
    the K_DIR relay, which turns the VFD run command from FWD to REV for M4 (the
    RapidChange tool changer unloads in reverse; controls M12). No flood output.

  Add to my_machine.h with this map: SAFETY_DOOR_ENABLE 1, PROBE_ENABLE 1,
  MCP23017_ENABLE 1 (status inputs and the tool-changer I/O), PLASMA_ENABLE 1 (the plasma plugin must be
  added to the ESP32 CMakeLists.txt; it is not in the ESP32 build today) and
  MODBUS_ENABLE 0. THCAD_ENABLE is new: the ESP32 THCAD capture driver that
  reads THCAD_PIN does not exist yet.
*/

#if N_ABC_MOTORS > 1
#error "Axis configuration is not supported!"
#endif

// Four motors keep the TMC driver SPI chain intact: X, Y, Z and Y2 (M3).
#if N_ABC_MOTORS == 0 && N_GANGED == 0
#undef N_ABC_MOTORS
#undef N_GANGED
#undef Y_GANGED
#define N_ABC_MOTORS 1
#define N_GANGED 1
#define Y_GANGED 1
#endif

#if MODBUS_ENABLE
#error "GM1: GPIO14/GPIO15 are THCAD and arc-OK inputs, so RS485/Modbus cannot be used."
#endif

#if KEYPAD_ENABLE == 1
#error No free pins for I2C keypad!
#endif

#include "use_i2s_out.h"

#define BOARD_NAME "BTT Rodent (GM1)"
#define BOARD_URL "https://github.com/bigtreetech/Rodent/tree/master"

#define I2S_OUT_BCK             GPIO_NUM_22
#define I2S_OUT_WS              GPIO_NUM_17
#define I2S_OUT_DATA            GPIO_NUM_21

#define TMC_STEALTHCHOP         0

#define X_STEP_PIN              I2SO(2)
#define X_DIRECTION_PIN         I2SO(1)
#define X_ENABLE_PIN            I2SO(0)
#define X_LIMIT_PIN             GPIO_NUM_35     // X-MAX

#define Y_STEP_PIN              I2SO(5)
#define Y_DIRECTION_PIN         I2SO(4)
#define Y_ENABLE_PIN            I2SO(7)
#define Y_LIMIT_PIN             GPIO_NUM_34     // Y-MAX: Y1

#define Z_STEP_PIN              I2SO(10)
#define Z_DIRECTION_PIN         I2SO(9)
#define Z_ENABLE_PIN            I2SO(8)
#define Z_LIMIT_PIN             GPIO_NUM_33     // Z-MAX

#define M3_AVAILABLE
#define M3_STEP_PIN             I2SO(13)
#define M3_DIRECTION_PIN        I2SO(12)
#define M3_ENABLE_PIN           I2SO(15)
#define M3_LIMIT_PIN            GPIO_NUM_32     // E0-MAX: Y2

#define AUXOUTPUT0_PIN          GPIO_NUM_25     // Sp-Enable: run request -> isolated U_RUN -> K_REQ_A/K_REQ_B
#define AUXOUTPUT1_PIN          GPIO_NUM_13     // SP-PWM 0-10 V (onboard filter and LM358)
#define AUXOUTPUT2_PIN          GPIO_NUM_2      // V-MOS HE1: K_DIR coil, spindle direction (M4 = REV)
#define AUXOUTPUT3_PIN          GPIO_NUM_4      // V-MOS HE0: router mist solenoid

#if DRIVER_SPINDLE_ENABLE & SPINDLE_PWM
#define SPINDLE_PWM_PIN         AUXOUTPUT1_PIN
#endif
#if DRIVER_SPINDLE_ENABLE & SPINDLE_ENA
#define SPINDLE_ENABLE_PIN      AUXOUTPUT0_PIN
#endif
#if DRIVER_SPINDLE_ENABLE & SPINDLE_DIR
#define SPINDLE_DIRECTION_PIN   AUXOUTPUT2_PIN  // K_DIR: M4 runs the VFD in REV (RapidChange unload)
#endif

#if COOLANT_ENABLE & COOLANT_FLOOD
#error "GM1: V-MOS HE1 is the spindle direction output; there is no flood coolant output."
#endif
#if COOLANT_ENABLE & COOLANT_MIST
#define COOLANT_MIST_PIN        AUXOUTPUT3_PIN
#endif

#define AUXINPUT0_PIN           GPIO_NUM_36     // Probe: plasma float via U_PROBE (healthy high, trip low)
#define AUXINPUT1_PIN           GPIO_NUM_39     // E1-MAX: GM1 door input. Rodent V1.0: GPIO_NUM_37
#define AUXINPUT2_PIN           GPIO_NUM_15     // Sp-Direction header: arc OK (low = arc on); plasma $367

#if PROBE_ENABLE
#define PROBE_PIN               AUXINPUT0_PIN
#endif
#if SAFETY_DOOR_ENABLE
#define SAFETY_DOOR_PIN         AUXINPUT1_PIN
#endif

// Sp-Feedback header, THCAD-300 output buffered to 3.3 V. Read by the new
// capture driver, which must present the arc voltage as an analog aux port
// for plasma $366.
#define THCAD_PIN               GPIO_NUM_14

// OLED header: MCP23017 status expander (board pull-ups go to +5 V).
#define I2C_PORT                I2C_NUM_1
#define I2C_SDA                 GPIO_NUM_27
#define I2C_SCL                 GPIO_NUM_26
#define I2C_CLOCK               100000

#define SPI_MISO_PIN            GPIO_NUM_19
#define SPI_MOSI_PIN            GPIO_NUM_23
#define SPI_SCK_PIN             GPIO_NUM_18
#define MOTOR_CS_PIN            GPIO_NUM_5
#if SDCARD_ENABLE
#define SD_CS_PIN               GPIO_NUM_0
#endif
