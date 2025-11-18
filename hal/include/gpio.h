
#ifndef GPIO_H
#define GPIO_H

#include <stdint.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>


typedef enum {
    GPIO_DIRECTION_INPUT = 0,
    GPIO_DIRECTION_OUTPUT = 1
} gpio_direction_t;

typedef enum  {
    GPIO_AFSEL_NONE,
    GPIO_AFSEL1, // Primary
    GPIO_AFSEL2, // Secondary
    GPIO_AFSEL3, // Tertiary
    GPIO_AFSEL4, 
    GPIO_AFSEL5,
    GPIO_AFSEL6,
    GPIO_AFSEL7,   
    GPIO_AFSEL8,
    GPIO_AFSEL9,
    GPIO_AFSEL10,
    GPIO_AFSEL11,
    GPIO_AFSEL12,
    GPIO_AFSEL13,
    GPIO_AFSEL14,
    GPIO_AFSEL15
} gpio_function_t;
// depends on how many alternate functions MCU has

/// @brief GPIO port structure
struct gpio { 
    uintptr_t base;    
    size_t pin; // pin mask BITO, BIT1, ...
    gpio_direction_t direction; // input/output
    uint8_t pull_en; // pull-up/pull-down enable
    gpio_function_t function; // function select
};



/// @brief Initialize a GPIO port as output
/// @param gpio_port GPIO Port
/// @param base Base address of the GPIO port
/// @param pinMask Pin mask for the desired pin(s)
void gpio_init_output(struct gpio* gpio_port, unsigned long base, size_t pinMask);


/// @brief Initialize a GPIO port as output
/// @param gpio_port GPIO Port
/// @param base Base address of the GPIO port
/// @param pinMask Pin mask for the desired pin(s)
void gpio_init_input(struct gpio* gpio_port, unsigned long base, size_t pinMask, uint8_t pull_en);


/// @brief Write a value to the GPIO port
/// @param gpio_port GPIO Port
/// @param value Value to write (true for high, false for low)
void gpio_write(struct gpio* gpio_port, _Bool value);


/// @brief Toggle the state of the GPIO port
/// @param gpio_port GPIO Port
void gpio_toggle(struct gpio* gpio_port);


/// @brief Read the current state of the GPIO port
/// @param gpio_port GPIO Port
/// @return Current state of the GPIO port (true for high, false for low)
_Bool gpio_read(struct gpio* gpio_port);  


/// @brief Sets the function of the GPIO port (alternate function selection)
/// @param gpio_port 
/// @param function 
void gpio_set_function(struct gpio* gpio_port, gpio_function_t function);


#endif