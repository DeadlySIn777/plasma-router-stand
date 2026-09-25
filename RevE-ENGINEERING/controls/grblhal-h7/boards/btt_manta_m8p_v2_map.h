/*
  btt_manta_m8p_v2_map.h - Board map for BIGTREETECH MANTA M8P V2.0

  Part of grblHAL

  Copyright (c) 2024-2026 Jon Escombe

  grblHAL is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  grblHAL is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with grblHAL.  If not, see <http://www.gnu.org/licenses/>.
*/

#if N_ABC_MOTORS > 5
#error "BTT Manta M8P v2 board is configuted for 8 motors max."
#endif

#if !(defined(STM32H723xx)) || HSE_VALUE != 25000000
#error "This board has a STM32H723 processor with 25MHz crystal, select a corresponding build!"
#endif

#define BOARD_NAME "BTT Manta M8P V2"
#define BOARD_URL "https://github.com/bigtreetech/Manta-M8P"

#define SERIAL_PORT                 1       // GPIOA: TX =  9, RX = 10

#if SDCARD_ENABLE
#define SPI_PORT                    2       // GPIOB: SCK = 13, MISO = 14, MOSI = 15
#else
#define SPI_PORT                    3       // GPIOC: SCK = 10, MISO - 11, MOSI - 12
#endif

// todo: I2C3 is routed to a board header, however the clock & data pins
//       are split across two ports - which is not currently supported..
//#define I2C_PORT                    3       // GPIOx:

// Motor Reference:
// Motor-1: STEP:PE6  DIR:PE5  ENABLE:PC14 LIMIT:PF4  *AXIS:X*
// Motor-2: STEP:PE2  DIR:PE1  ENABLE:PE4  LIMIT:PF3  *AXIS:Y*
// Motor-3: STEP:PB8  DIR:PB7  ENABLE:PE0  LIMIT:PF2   AXIS:M4
// Motor-4: STEP:PB4  DIR:PB3  ENABLE:PB6  LIMIT:PF1   AXIS:M5
// Motor-5: STEP:PG13 DIR:PG12 ENABLE:PG15 LIMIT:PF0  *AXIS:Z*
// Motor-6: STEP:PG9  DIR:PD7  ENABLE:PG11 LIMIT:PC15 *AXIS:M3*
// Motor-7: STEP:PD4  DIR:PD3  ENABLE:PD6  LIMIT:      AXIS:M6
// Motor-8: STEP:PC7  DIR:PC8  ENABLE:PD2  LIMIT:      AMXI:M7

// Note: Only four axis have limit switch capability.
//       Motor-3 and Motor-4 limit switches clash with opto-isolated control inputs
//       Motor-7 and Motor-8 do not have associated limit switch inputs

// Define step pulse output pins.
#define X_STEP_PORT                 GPIOE
#define X_STEP_PIN                  6
#define Y_STEP_PORT                 GPIOE
#define Y_STEP_PIN                  2
#define Z_STEP_PORT                 GPIOG
#define Z_STEP_PIN                  13
#define STEP_OUTMODE                GPIO_SINGLE

// Define step direction output pins.
#define X_DIRECTION_PORT            GPIOE
#define X_DIRECTION_PIN             5
#define Y_DIRECTION_PORT            GPIOE
#define Y_DIRECTION_PIN             1
#define Z_DIRECTION_PORT            GPIOG
#define Z_DIRECTION_PIN             12
#define DIRECTION_OUTMODE           GPIO_SINGLE

// Define stepper driver enable/disable output pin.
#define X_ENABLE_PORT               GPIOC
#define X_ENABLE_PIN                14
#define Y_ENABLE_PORT               GPIOE
#define Y_ENABLE_PIN                4
#define Z_ENABLE_PORT               GPIOG
#define Z_ENABLE_PIN                15

// Define homing/hard limit switch input pins.
#define X_LIMIT_PORT                GPIOF
#define X_LIMIT_PIN                 4
#define Y_LIMIT_PORT                GPIOF
#define Y_LIMIT_PIN                 3
#define Z_LIMIT_PORT                GPIOF
#define Z_LIMIT_PIN                 0
#define LIMIT_INMODE                GPIO_SINGLE

// Define M3 step, direction, enable, and limit pins.
#if N_ABC_MOTORS > 0
#define M3_AVAILABLE                // Motor-6
#define M3_STEP_PORT                GPIOG
#define M3_STEP_PIN                 9
#define M3_DIRECTION_PORT           GPIOD
#define M3_DIRECTION_PIN            7
#define M3_LIMIT_PORT               GPIOC
#define M3_LIMIT_PIN                15
#define M3_ENABLE_PORT              GPIOG
#define M3_ENABLE_PIN               11
#endif

// Define M4 step, direction, enable.
#if N_ABC_MOTORS > 1
#define M4_AVAILABLE                // Motor-3
#define M4_STEP_PORT                GPIOB
#define M4_STEP_PIN                 8
#define M4_DIRECTION_PORT           GPIOB
#define M4_DIRECTION_PIN            7
#define M4_ENABLE_PORT              GPIOE
#define M4_ENABLE_PIN               0
#endif

// Define M5 step, direction, enable.
#if N_ABC_MOTORS > 2
#define M5_AVAILABLE                // Motor-4
#define M5_STEP_PORT                GPIOB
#define M5_STEP_PIN                 4
#define M5_DIRECTION_PORT           GPIOB
#define M5_DIRECTION_PIN            3
#define M5_ENABLE_PORT              GPIOB
#define M5_ENABLE_PIN               6
#endif

// Define M6 step, direction, enable.
#if N_ABC_MOTORS > 3
#define M6_AVAILABLE                // Motor-7
#define M6_STEP_PORT                GPIOD
#define M6_STEP_PIN                 4
#define M6_DIRECTION_PORT           GPIOD
#define M6_DIRECTION_PIN            3
#define M6_ENABLE_PORT              GPIOD
#define M6_ENABLE_PIN               6
#endif

// Define M7 step, direction, enable.
#if N_ABC_MOTORS > 4
#define M7_AVAILABLE                // Motor-8
#define M7_STEP_PORT                GPIOC
#define M7_STEP_PIN                 7
#define M7_DIRECTION_PORT           GPIOC
#define M7_DIRECTION_PIN            8
#define M7_ENABLE_PORT              GPIOD
#define M7_ENABLE_PIN               2
#endif

#define AUXOUTPUT0_PORT             GPIOF   // FAN0
#define AUXOUTPUT0_PIN              7
#define AUXOUTPUT1_PORT             GPIOF   // FAN1
#define AUXOUTPUT1_PIN              9
#define AUXOUTPUT2_PORT             GPIOF   // Spindle enable - FAN2
#define AUXOUTPUT2_PIN              6
#define AUXOUTPUT3_PORT             GPIOF   // Spindle direction - FAN3
#define AUXOUTPUT3_PIN              8
#define AUXOUTPUT4_PORT             GPIOE   // Spindle PWM - MOTOR
#define AUXOUTPUT4_PIN              9
#define AUXOUTPUT5_PORT             GPIOA   // Coolant flood - FAN5
#define AUXOUTPUT5_PIN              6
#define AUXOUTPUT6_PORT             GPIOA   // Coolant mist - FAN6
#define AUXOUTPUT6_PIN              2

// Define driver spindle pins.
#if DRIVER_SPINDLE_ENABLE & SPINDLE_ENA
#define SPINDLE_ENABLE_PORT         AUXOUTPUT2_PORT
#define SPINDLE_ENABLE_PIN          AUXOUTPUT2_PIN
#endif
#if DRIVER_SPINDLE_ENABLE & SPINDLE_PWM
#define SPINDLE_PWM_PORT            AUXOUTPUT4_PORT
#define SPINDLE_PWM_PIN             AUXOUTPUT4_PIN
#endif
#if DRIVER_SPINDLE_ENABLE & SPINDLE_DIR
#define SPINDLE_DIRECTION_PORT      AUXOUTPUT3_PORT
#define SPINDLE_DIRECTION_PIN       AUXOUTPUT3_PIN
#endif

// Define flood and mist coolant enable output pins.
#if COOLANT_ENABLE & COOLANT_FLOOD
#define COOLANT_FLOOD_PORT          AUXOUTPUT5_PORT
#define COOLANT_FLOOD_PIN           AUXOUTPUT5_PIN
#endif
#if COOLANT_ENABLE & COOLANT_MIST
#define COOLANT_MIST_PORT           AUXOUTPUT6_PORT
#define COOLANT_MIST_PIN            AUXOUTPUT6_PIN
#endif

// Only 3 optos on the board, ind-det, fan5-det, fan6/cool-det...
#define AUXINPUT0_PORT              GPIOC   // Reset - FAN5 tacho
#define AUXINPUT0_PIN               2
#define AUXINPUT1_PORT              GPIOC   // Feed hold - FAN6 tacho
#define AUXINPUT1_PIN               1
#define AUXINPUT2_PORT              GPIOD   // Cycle start - IND probe
#define AUXINPUT2_PIN               8
#define AUXINPUT3_PORT              GPIOD   // BLTOUCH sensor
#define AUXINPUT3_PIN               13

// Define user-control controls (cycle start, reset, feed hold) input pins.
#if CONTROL_ENABLE & CONTROL_HALT
#define RESET_PORT                  AUXINPUT0_PORT
#define RESET_PIN                   AUXINPUT0_PIN
#endif
#if CONTROL_ENABLE & CONTROL_FEED_HOLD
#define FEED_HOLD_PORT              AUXINPUT1_PORT
#define FEED_HOLD_PIN               AUXINPUT1_PIN
#endif
#if CONTROL_ENABLE & CONTROL_CYCLE_START
#define CYCLE_START_PORT            AUXINPUT2_PORT
#define CYCLE_START_PIN             AUXINPUT2_PIN
#endif


// CAUTION: No protection on this input, tied directly to MCU
#if PROBE_ENABLE
 #define PROBE_PORT                  AUXINPUT3_PORT
 #define PROBE_PIN                   AUXINPUT3_PIN
#endif

#if SAFETY_DOOR_ENABLE
// #define SAFETY_DOOR_PORT            AUXINPUTn_PORT
// #define SAFETY_DOOR_PIN             AUXINPUTn_PIN
#endif

#if SDCARD_ENABLE                   // Wired to SPI2
#define SDCARD_SDIO                 0
#define SD_CS_PORT                  GPIOB
#define SD_CS_PIN                   12
#endif

#if TRINAMIC_UART_ENABLE

#define MOTOR_UARTX_PORT            GPIOC   // Motor-1
#define MOTOR_UARTX_PIN             13
#define MOTOR_UARTY_PORT            GPIOE   // Motor-2
#define MOTOR_UARTY_PIN             3
#define MOTOR_UARTZ_PORT            GPIOG   // Motor-5
#define MOTOR_UARTZ_PIN             14

#ifdef  M3_AVAILABLE
#define MOTOR_UARTM3_PORT           GPIOG   // Motor-6
#define MOTOR_UARTM3_PIN            10
#endif

#ifdef  M4_AVAILABLE
#define MOTOR_UARTM4_PORT           GPIOB   // Motor-3
#define MOTOR_UARTM4_PIN            9
#endif

#ifdef  M5_AVAILABLE
#define MOTOR_UARTM5_PORT           GPIOB   // Motor-4
#define MOTOR_UARTM5_PIN            5
#endif

#ifdef  M6_AVAILABLE
#define MOTOR_UARTM6_PORT           GPIOD   // Motor-7
#define MOTOR_UARTM6_PIN            5
#endif

#ifdef  M7_AVAILABLE
#define MOTOR_UARTM7_PORT           GPIOC   // Motor-8
#define MOTOR_UARTM7_PIN            6
#endif

#elif TRINAMIC_SPI_ENABLE

// The Manta M8P uses software SPI
#define TRINAMIC_SOFT_SPI

#define TRINAMIC_MOSI_PORT          GPIOG
#define TRINAMIC_MOSI_PIN           6
#define TRINAMIC_SCK_PORT           GPIOG
#define TRINAMIC_SCK_PIN            8
#define TRINAMIC_MISO_PORT          GPIOG
#define TRINAMIC_MISO_PIN           7

#define MOTOR_CSX_PORT              GPIOC   // Motor-1
#define MOTOR_CSX_PIN               13
#define MOTOR_CSY_PORT              GPIOE   // Motor-2
#define MOTOR_CSY_PIN               3
#define MOTOR_CSZ_PORT              GPIOG   // Motor-5
#define MOTOR_CSZ_PIN               14

#ifdef  M3_AVAILABLE
#define MOTOR_CSM3_PORT             GPIOG   // Motor-6
#define MOTOR_CSM3_PIN              10
#endif

#ifdef  M4_AVAILABLE
#define MOTOR_CSM4_PORT             GPIOB   // Motor-3
#define MOTOR_CSM4_PIN              9
#endif

#ifdef  M5_AVAILABLE
#define MOTOR_CSM5_PORT             GPIOB   // Motor-4
#define MOTOR_CSM5_PIN              5
#endif

#ifdef  M6_AVAILABLE
#define MOTOR_CSM6_PORT             GPIOD   // Motor-7
#define MOTOR_CSM6_PIN              5
#endif

#ifdef  M7_AVAILABLE
#define MOTOR_CSM7_PORT             GPIOC   // Motor-8
#define MOTOR_CSM7_PIN              6
#endif

#endif

// EOF
