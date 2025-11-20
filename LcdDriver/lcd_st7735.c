

#include "lcd.h"
#include "hal_lcd.h"
#include "../hal/include/gpio.h"



// LCD Screen Dimensions
#define LCD_VERTICAL_MAX                   128
#define LCD_HORIZONTAL_MAX                 128


// STT735 Instruction Set
typedef enum { 
    NOP       = 0x00U, 
    SWRESET   = 0x01U, 
    RDDID     = 0x04U,
    RDDST     = 0x09U,
    RDDPM     = 0x0AU,
    RDDMADCTL = 0x0BU, 
    RDDCOLMOD = 0x0CU, 
    RDDIM     = 0x0DU, 
    RDDSM     = 0x0EU,
    SLPIN     = 0x10U,
    SLPOUT    = 0x11U,
    PLTON     = 0x12U, 
    NORON     = 0x13U,
    INVOFF    = 0x20U,
    INVON     = 0x21U, 
    GAMSET    = 0x26U, 
    DISPOFF   = 0x28U,
    DISPON    = 0x29U,
    CASET     = 0x2AU, 
    RASET     = 0x2BU,
    RAMWR    = 0x2CU,
    RAMRD     = 0x2EU,
    PTLAR     = 0x30U,
    TEOFF     = 0x34U,
    TEON      = 0x35U,
    MADCTL    = 0x36U,
    IDMOFF    = 0x38U,
    IDMON     = 0x39U,
    COLMOD    = 0x3AU,
    RDID1     = 0xDAU,
    RDID2     = 0xDBU,
    RDID3     = 0xDCU
} st7735_system_command_t;


typedef enum {
    FRMCTR1 = 0xB1U,
    FRMCTR2 = 0xB2U,
    FRMCTR3 = 0xB3U,
    INVCTR  = 0xB4U,
    DISSET5 = 0xB6U,
    PWCTR1  = 0xC0U,
    PWCTR2  = 0xC1U,
    PWCTR3  = 0xC2U,
    PWCTR4  = 0xC3U,
    PWCTR5  = 0xC4U,
    VMCTR1  = 0xC5U,
    VMOFCTR = 0xC7U,
    WRID2   = 0xD1U,
    WRID3   = 0xD2U,
    PWCTR6  = 0xFCU,
    NVCTR1  = 0xD9U,
    NVCTR2  = 0xDEU,
    NVCTR3  = 0xDFU,
    GAMCTRP1= 0xE0U,
    GAMCTRN1= 0xE1U,
    EXTCTRL = 0xF0U,
    VCOM4L  = 0xFFU

} st7735_panel_command_t;



typedef enum  {
    PIXEL_12BIT = 0b011, // 12-bit/pixel
    PIXEL_16BIT = 0b101, // 16 bit/pixel
    PIXEL_18BIT = 0b110  // 18-bit/pixel
} pixel_format_t;




void lcd_init() { 

    HAL_LCD_PORT_init();
    HAL_LCD_SPI_init();


    // pulse RST pin briefly 
    gpio_write(&lcd_rst, false);
    HAL_LCD_delay(20); // This reset should be longer than 9 us according to ST7735 datasheet. 1 cycle is normally around ~42 us on default settings
    gpio_write(&lcd_rst, true);
    HAL_LCD_delay(20);

    gpio_write(&lcd_cs, false);
    // Software reset to default initialized values
    HAL_LCD_write_command(SWRESET);

    gpio_write(&lcd_cs, true);
    HAL_LCD_delay(50000);


    // Wake device from sleep mode
    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(SLPOUT); 
    gpio_write(&lcd_cs, true);
    HAL_LCD_delay(50000);  // Wait >=120 ms before sending next command
    

    // Frame rate control 68 Hz for 128x128 Refer to datasheet for calculation
    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(FRMCTR1); 
    HAL_LCD_write_data(0x02);
    HAL_LCD_write_data(0x2C);
    HAL_LCD_write_data(0x2D);
    gpio_write(&lcd_cs, true);



    // Set pixel format 
    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(COLMOD);
    HAL_LCD_write_data(PIXEL_16BIT);
    gpio_write(&lcd_cs, true);

    // Select row and column frame address 
    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(MADCTL);
    HAL_LCD_write_data(0x00);
    gpio_write(&lcd_cs, true);
    

    // Turn Normal Display mode on 
    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(DISPON);
    gpio_write(&lcd_cs, true);

    lcd_set_window(0, 0, 127, 127);

    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(RAMWR);
    for (int i = 0; i < 16384; i++)
    {
        HAL_LCD_write_data(0x00);
        HAL_LCD_write_data(0x00);

    }
    gpio_write(&lcd_cs, true);
}


void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) { 

    /* x0 += 2;
    y0 += 3;
    x1 += 2;
    y1 += 3; */

    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(CASET);
    HAL_LCD_write_data(x0 >> 8);     // XS
    HAL_LCD_write_data(x0 & 0xFF);
    HAL_LCD_write_data(x1 >> 8);     // XE
    HAL_LCD_write_data(x1 & 0xFF);
    gpio_write(&lcd_cs, true);

    gpio_write(&lcd_cs, false);
    HAL_LCD_write_command(RASET);
    HAL_LCD_write_data(y0 >> 8);     // XS
    HAL_LCD_write_data(y0 & 0xFF);
    HAL_LCD_write_data(y1 >> 8);     // XE
    HAL_LCD_write_data(y1 & 0xFF);
    gpio_write(&lcd_cs, true);

}

void lcd_draw_pixel(const uint16_t x, const uint16_t y, const uint16_t color) { 

    lcd_set_window(x, y, x, y);
    HAL_LCD_write_command(RAMWR);
    HAL_LCD_write_data(color >> 8);
    HAL_LCD_write_data(color & 0xFF);
    
}

