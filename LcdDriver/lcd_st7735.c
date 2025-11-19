

#include "lcd.h"
#include "hal_lcd.h"
#include "../hal/include/gpio.h"


void lcd_init() { 

    HAL_LCD_PORT_init();
    HAL_LCD_SPI_init();


    // pulse RST pin briefly 
    gpio_write(&lcd_rst, false);
    HAL_LCD_delay(10); // This reset should be longer than 9 us according to ST7735 datasheet. 1 cycle is normally around ~42 us on default settings
    gpio_write(&lcd_rst, true);
    HAL_LCD_delay(10);


    // Figure out start up process 
}


void lcd_set_window() { 


    
}

void lcd_draw_pixel() { 



}

