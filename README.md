## Summary

A basic guide on how to build and execute this project for the MSP432P4xxx
series microcontroller by Texas Instruments

## Prerequisites 

* MSP432P410R Launchpad 
* arm-none-eabi-gcc compiler 
* openocd 
* gdb-multiarch 
* makefile

## How To Run 


1. To compile the project using make: 
```
$ cd gcc 
$ make all
``` 

2.  Open an openocd session and run the following command 

``` 
$ openocd -f board/ti_msp432_launchpad.cfg 
```gi


3. Open an arm gdb session and connect to openocd server and load application
``` 
$ gdb-multiarch
$ (gdb) target remote :3333
$ (gdb) load <executable_name.out>
```

1. That's all! you can type `continue` or press physical reset button to continue programs
