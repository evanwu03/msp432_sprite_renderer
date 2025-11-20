
#ifndef LCD_H
#define LCD_H


#include <stdint.h>



/// @brief Initializes LCD display 
void lcd_init();


/// @brief 
/// @param x0 
/// @param y0 
/// @param x1 
/// @param y1 
void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);


/// @brief 
/// @param x 
/// @param y 
/// @param color 
void lcd_draw_pixel(const uint16_t x, const uint16_t y, const uint16_t color);





#endif // LCD_H
