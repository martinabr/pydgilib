"""This module provides Python bindings for DGILibExtra GPIO interface."""

__author__ = "Erik Wouters <ehwo(at)kth.se>"
__credits__ = "Atmel Corporation. / Rev.: Atmel-42771A-DGILib_User Guide-09/2016"
__license__ = "MIT"
__version__ = "0.1"
__revision__ = " $Id: dgilib_interface_gpio.py 1586 2019-02-13 15:56:25Z EWouters $ "
__docformat__ = "reStructuredText"

from pydgilib.dgilib_config import *


# TODO: make these functions faster
def int2bool(i):
    """Convert int to list of bool
    """
    return [bit is "1" for bit in f"{i:04b}"]


def bool2int(b):
    """Convert list of bool to int
    """
    return int("".join("1" if d else "0" for d in b), 2)


class DGILibInterfaceGPIO(object):
    """Python bindings for DGILib GPIO interface.

    The GPIO interface consists of four lines available, which can be individually set to input or output
    through the configuration interface. This interface can only be used in Timestamp mode. Input lines are
    monitored and will trigger an entry to be added to the timestamp buffer on each change. Output lines can
    be controlled through the send data command.
    
    ## Parsing
    Each received data byte corresponds to an input pattern on the GPIO pins. If a bit is 1 it means that the
    corresponding GPIO pin is high, a 0 means a low level.
    
    ## Configuration
    The GPIO configuration controls the direction of the pins.
    Field ID Description
    Input pins 0 Setting a bit to 1 means the pin is monitored.
    Output pins 1 Setting a bit to 1 means the pin is set to output and can be controlled by the send
    command.
    """

    def __init__(self, *args, **kwargs):
        """
        :Example:

        >>> with DGILibExtra(read_mode=[True] * 4) as dgilib:
        ...     dgilib.get_major_version()
        5
        """

        # Argument parsing
        self.read_mode = kwargs.get("read_mode", [False] * 4)
        self.write_mode = kwargs.get("write_mode", [False] * 4)
        if self.verbose:
            print("read_mode: ", self.read_mode)
            print("write_mode: ", self.write_mode)

    def __enter__(self):
        """
        """
        
        self.gpio_set_config(read_mode=self.read_mode, write_mode=self.write_mode)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        """
        
        self.gpio_set_config()  # Disables interface.

    def gpio_get_config(self):
        """Get the pin-mode for the GPIO pins
        
        The GPIO configuration controls the direction of the pins.
        
        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can be controlled by the send
        command.
        
        :return: Tuple of:
            - List of read modes, Setting a pin to True means the pin is monitored.
            - List of write modes, Setting a pin to True means the pin is set to output and can be controlled by the send command.
        :rtype: (list(bool), list(bool))
        """

        # Get the configuration
        config_id, config_value = self.interface_get_configuration(INTERFACE_GPIO)

        # Convert int to lists of bool
        read_mode = int2bool(config_value[0])
        write_mode = int2bool(config_value[1])

        return read_mode, write_mode

#     def gpio_set_config(self, read_mode=[False] * 4, write_mode=[False] * 4):
        
#         # Update internal values
#         self.read_mode = read_mode
#         self.write_mode = write_mode
        
    def gpio_set_config(self, **kwargs):
        """Set the pin-mode for the GPIO pins
        
        The GPIO configuration controls the direction of the pins, and enables the interface if needed.
        
        Input pins:  Setting a bit to 1 means the pin is monitored.
        Output pins: Setting a bit to 1 means the pin is set to output and can be controlled by the send
        command.
        
        If any of the pins are set to read mode or write mode the GPIO interface will be enabled. If none of the pins are set to read mode
        or write mode the GPIO interface will be disabled.
        
        :param read_mode: List of modes, Setting a pin to True means the pin is monitored.
        :type read_mode: list(bool)
        :param write_mode: List of modes, Setting a pin to True means the pin is set to output and can be controlled by the send command.
        :type write_mode: list(bool)
        """
        
        # Argument parsing
        self.read_mode = kwargs.get("read_mode", self.read_mode)
        self.write_mode = kwargs.get("write_mode", self.write_mode)

        # Convert lists of bool to int
        read_mode = bool2int(self.read_mode)
        write_mode = bool2int(self.write_mode)

        # Set the configuration
        if "read_mode" in kwargs:
            self.interface_set_configuration(INTERFACE_GPIO, [0], [read_mode])
        if "write_mode" in kwargs:
            self.interface_set_configuration(INTERFACE_GPIO, [1], [write_mode])

        # Enable the interface if any of the pins are set to read mode or write mode
        if read_mode + write_mode:
            if not INTERFACE_GPIO in self.enabled_interfaces:
                self.interface_enable(INTERFACE_GPIO)
                self.enabled_interfaces.append(INTERFACE_GPIO)
            if self.timer_factor is None:
                self.timer_factor = self.get_time_factor()
        elif INTERFACE_GPIO in self.enabled_interfaces:  # Disable the interface if none of the pins are set to read mode or write mode
            self.interface_disable(INTERFACE_GPIO)
            self.enabled_interfaces.remove(INTERFACE_GPIO)

    def gpio_read(self):
        """Get the state of the GPIO pins.
        
        Clears the buffer and returns the values.
        
        :return: Tuple of list of list of pin states (bool) and list of timestamps in seconds
        :rtype: (list(list(bool)), list(float)
        """

        # Read the data from the buffer
        pin_values, ticks = self.interface_read_data(INTERFACE_GPIO)

        pin_values = [int2bool(pin_value) for pin_value in pin_values]
        timestamps = [tick * self.timer_factor for tick in ticks]
        
        if self.verbose >= 2:
            print(f"Collected {len(pin_values)} gpio samples (4 pins per sample)")

        return pin_values, timestamps

    def gpio_write(self, pin_values):
        """Set the state of the GPIO pins
        
        Make sure to set the pin to write mode first. Possibly also needs to be configured properly on the board
        
        A maximum of 255 elements can be written each time. An error return code will be given if data hasn’t been written yet.
        
        :param pin_values: List of pin values. Has to include all four pins ? TODO: TEST
        :type pin_values: list(bool)
        """

        # Convert list of bool to int
        pin_values = bool2int(pin_values)

        self.interface_write_data(INTERFACE_GPIO, [pin_values])
        
        if self.verbose >= 2:
            print(f"Sent gpio packet")