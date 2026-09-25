/* GPL-3.0-or-later. Board-specific idle state for unused Kraken drivers. */
#include "driver.h"
#ifdef BOARD_MY_MACHINE
static void output_high(GPIO_TypeDef *port, uint16_t pins)
{
    port->BSRR = pins; // Set output latch before switching mode; EN is active low.
    GPIO_InitTypeDef io = { .Pin=pins, .Mode=GPIO_MODE_OUTPUT_PP,
                          .Pull=GPIO_PULLUP, .Speed=GPIO_SPEED_FREQ_LOW };
    HAL_GPIO_Init(port, &io);
}
void board_init(void)
{
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOG_CLK_ENABLE();
    // S5-S8 enable inputs HIGH (disabled).
    output_high(GPIOG, GPIO_PIN_13 | GPIO_PIN_12 | GPIO_PIN_14);
    output_high(GPIOB, GPIO_PIN_5);
    // S5-S8 CS HIGH (not selected). Do not initialise their 75mOhm drivers.
    output_high(GPIOD, GPIO_PIN_2);
    output_high(GPIOA, GPIO_PIN_15 | GPIO_PIN_9 | GPIO_PIN_10);
}
#endif
