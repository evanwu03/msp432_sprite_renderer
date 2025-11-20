



# 2025117 
- Started writing HAL LCD drivers 
- Consolidated HAL library from other MSP432 projects to current project


# 20251118
- Completed HAL drivers, began testing SPI loopback and measured with logic analyzer to verify operation
- Plan to write application level logic. First goal should be to set the drawing frame and draw a single pixel at said frame.
- More investigation needed in datasheet to understand different write commands as well as RGB color formatting options for pixels.

# 20251119
- Looking at the ST7735 datasheet I believe I can ignore all of the read instructions not implemented since I will only focus on writing
- I have the initialization code setup and the commands are being decoded correctly on logic analyzer but it does not seem to actually draw a pixel on the screen. I may need to check timing to make sure my SPI settings are compatible with the ST7735
- Figured out the root cause of my issue. I had simply had the SPI clock phase wrong! Instead of capturing on the rising edge and changing on the falling edge I had it reversed. Now I will need to fix my SPI driver.