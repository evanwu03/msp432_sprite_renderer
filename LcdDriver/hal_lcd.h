
#ifndef HAL_LCD_H 
#define HAL_LCD_H

#include <stdint.h>
#include <stddef.h>



extern struct gpio lcd_dc;  // // D/CX according to datasheet
extern struct gpio lcd_cs; 
extern struct gpio lcd_spi_mosi;
extern struct gpio lcd_spi_clk;
extern struct gpio lcd_rst;


/// @brief Initializes GPIO pins for LCD SPI port
/// @param  None
void HAL_LCD_PORT_init(void);


/// @brief Configures LCD spi port
/// @param  None
void HAL_LCD_SPI_init(void);


/// @brief Sends a command to the LCD SPI controller
/// @param command 
void HAL_LCD_write_command(uint8_t command);


/// @brief Writes data to the LCD SPI controller
/// @param data
void HAL_LCD_write_data(uint8_t data);


/// @brief delay function calls __NOP for x cycles
/// @param cycles 
void HAL_LCD_delay(volatile uint32_t cycles); 



#endif // HAL_LCD_H