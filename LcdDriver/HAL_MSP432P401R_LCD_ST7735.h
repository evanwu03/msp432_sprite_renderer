
#ifndef HAL_MSP432P401R_LCD_ST7735 
#define HAL_MSP432P401R_LCD_ST7735

#include <stdint.h>
#include <stddef.h>



extern struct gpio lcd_dc;
extern struct gpio lcd_cs;
extern struct gpio lcd_spi_mosi;
extern struct gpio lcd_spi_clk;
extern struct gpio lcd_rst;


/// @brief 
/// @param  
void HAL_LCD_PORT_init(void);


/// @brief 
/// @param  
void HAL_LCD_SPI_init(void);


/// @brief 
/// @param command 
void HAL_LCD_write_command(uint8_t command);


/// @brief 
/// @param data
void HAL_LCD_write_data(uint8_t data);


/// @brief 
/// @param data_buffer
/// @param length
void HAL_LCD_read_data(uint8_t* data_buffer, size_t length);



/// @brief delay function calls __NOP for x cycles
/// @param cycles 
void HAL_LCD_delay(volatile uint32_t cycles); 



#endif // HAL_MSP432P401R_LCD_ST7735