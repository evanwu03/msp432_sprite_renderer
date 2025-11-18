
#ifndef HAL_MSP432P401R_LCD_ST7735 
#define HAL_MSP432P401R_LCD_ST7735

#include <stdint.h>
#include <stddef.h>

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



#endif // HAL_MSP432P401R_LCD_ST7735