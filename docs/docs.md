



# 2025117 
- Started writing HAL LCD drivers 
- Consolidated HAL library from other MSP432 projects to current project


# 20251118
- Completed HAL drivers, began testing SPI loopback and measured with logic analyzer to verify operation
- Plan to write application level logic. First goal should be to set the drawing frame and draw a single pixel at said frame.
- More investigation needed in datasheet to understand different write commands as well as RGB color formatting options for pixel

# 20251119
- Looking at the ST7735 datasheet I believe I can ignore all of the read instructions not implemented since I will only focus on writing
- I have the initialization code setup and the commands are being decoded correctly on logic analyzer but it does not seem to actually draw a pixel on the screen. I may need to check timing to make sure my SPI settings are compatible with the ST7735
- Figured out the root cause of my issue. I had simply had the SPI clock phase wrong! Instead of capturing on the rising edge and changing on the falling edge I had it reversed. Now I will need to fix my SPI driver.

# 20251120 
- Successfully uploaded an image to the LCD for the first time! My friends gave me a few images to test out and it was lot of fun. To fit the image on the LCD I first had to resize the image to 128x128 and then convert it into a C array of RGB565 values
- Currently program only displays one image and that's it but I could program it so you can cycle through a deck of images 
- Rendering overall is pretty slow and it takes on average 6.2 seconds to flush the screen and load an image on boot. This is probably due to only using a 3 Mhz clock for SPI and latency from SPI based polling. 
- In future I would like to switch to Interrupt-based DMA SPI to reduce overhead on CPU and improve refresh rate. 

# 20251122
- My next goal will be to render a 17 second @ 25 fps video of a man riding a bicycle with Ordinary by Alex Warren playing in the background. This will not be an easy feat without some offline video compression techniques because while you could save the video as MP4 which is already very compressed, the ST7735 LCD only takes raw RGB565 pixel values. Therefore we have to decode the video frames back to RGB565 for the MSP432 to process. Problem is we can't store this entire MP4 file as a raw RGB565 array because that would be roughly 14.9 MB of flash which is roughly 58x more flash than we have available to us on the MSP432. Now why not just load the video from an external SD card? Well that would be the easy path, but in my opinion not the rewarding one. 
- I believe my next plan is exploring video compression strategies like delta frame encoding or run length encoding. I may also need to implement buffering logic or tile systems. 

I think before we even touch the MSP432, we need a tool that:

1. Loads the video/GIF

2. Converts each frame to 128×128 RGB565

3. Computes deltas between consecutive frames

4. Visualizes the delta mask (so you can see what changed)

5. Saves both:
   - the full reconstructed frame (for debugging)
   - the delta overlay (for tuning compression)


# 20251124

## Compression pipeline
1. delta compression
2. zigzag encoding
3. RLE (zero length runs)
4. VLE (variable-length encode)
5.  write bytes to file


# 20251128 
- After sacrificing many frames, resolution, and color I can successfully fit some pretty decently long GIFs (longest is 17 seconds so far) within 256KB including the first frame needed to decode delta compression. For the 17 second GIF I'm forced to downsize to 96x96 @ 12fps and BGR444 while for shorter videos around 3-6 seconds I can retain 128x128 resolution very easily. Overall genuinely impressed by what is achievable with codecs and while mine is probably very suboptimal compared to popular formats out there, the compression ratio is pretty impressive at compressing RAW RGB/BGR frames into something that my ST7735 can read. This project has definitely taught me a lot about how to make do with the resources you have and those sort of constraints often lead to creative solutions. 
- Next step is to finally port the codec to the MCU and implement DMA, so the CPU isn't bottlenecked by SPI transfers. 
- Also need to start writing a script to convert the generated bin files to a C style array
- Currently exploring palette quantization techniques such as K-means and Median cut. My method currently just naively truncate bits to fit them into 8, 12 and 16 bits but no statistical methods are employed to cluster similar colors together. 

# 20251129
  
I noticed throughout this project I have been slowly adding new pieces to the compression pipeline I think for me it started with learning delta compression, then learning VLE To compact bytes, then applying RLE to exploit the temporal behavior from delta compression and zigzag encoding to support VLE by mapping all negative numbers to positive ones. After all of that I supplemented the system with a color quantizer to reduce the RGB down to 8 bits/256 colors. With that said and done the performance was getting pretty good, but that's when I solved the issue with my RLE by adding run length maximums and adding a control bit to mark starts of run. Now we have looped back and are now optimizing the RLE with vertical replication

# 20251219

Goals for today are to: 
- Add frame boundaries in my run length encoder  
- develop python implementation of decoder
- Write utility to cocnvert encoded video to a C-style array
- ~~Optimize euclidean distance calculaitons (they are slow!)~~ We achieved about 2x speedup by removing the np.sqrt() and precomputing norms