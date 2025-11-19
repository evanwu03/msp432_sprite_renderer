



# 2025117 
- Started writing HAL LCD drivers 
- Consolidated HAL library from other MSP432 projects to current project


# 20251118
- Completed HAL drivers, began testing SPI loopback and measured with logic analyzer to verify operation
- Plan to write application level logic. First goal should be to set the drawing frame and draw a single pixel at said frame.
- More investigation needed in datasheet to understand different write commands as well as RGB color formatting options for pixels.

# 20251119
- Looking at the ST7735 datasheet I believe I can ignore all of the read instructions not implemented since I will only focus on writing
