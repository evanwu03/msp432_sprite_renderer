

#include "Crystalfontz128x128_ST7735.h"
#include "HAL_MSP432P401R_LCD_ST7735.h"
#include "../hal/include/gpio.h"


void Crystalfontz128x128_init() { 

    HAL_LCD_PORT_init();
    HAL_LCD_SPI_init();


    // pulse RST pin briefly 
    gpio_write(&lcd_rst, false);
    HAL_LCD_delay(10); // This reset should be longer than 9 us according to ST7735 datasheet. 1 cycle is normally around ~42 us on default settings
    gpio_write(&lcd_rst, true);
    HAL_LCD_delay(10);


}