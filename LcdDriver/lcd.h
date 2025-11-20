
#ifndef LCD_H
#define LCD_H


#include <stdint.h>



/// @brief Initializes LCD display 
void lcd_init();


/// @brief Sets frame address pointer that will be written to
/// @param x0 start x coordinate
/// @param y0 start y coordinate
/// @param x1 end x coordinate
/// @param y1 end y coordinate
void lcd_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1); // Wrap coordinates into struct in future?


/// @brief Draw a single pixel at (x,y) pixel
/// @param x x coordinate
/// @param y y coordinate
/// @param red   red value 
/// @param green green value
/// @param blue  blue value
void lcd_draw_pixel(const uint16_t x, const uint16_t y, const uint16_t red, const uint16_t green, const uint16_t blue); // Wrap RGB into struct?





#endif // LCD_H
