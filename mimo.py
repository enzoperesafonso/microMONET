import asyncio
from typing import Union, List, Tuple
from aioserial import AioSerial
import re

class MicroMONET:
    def __init__(self, device: str = "/dev/ttyS0", baudrate: int = 9600):
        """
        Initialize the MicroMONET class with the serial device and baudrate.
        
        :param device: The serial device (e.g., "/dev/ttyS0" or "COM3").
        :param baudrate: The baudrate for serial communication (default: 9600).
        """
        self._aioserial = AioSerial(device, baudrate=baudrate)

    async def send_command(self, command: str) -> str:
        """
        Send a command to the Arduino and wait for a response.
        
        :param command: The command to send (e.g., "GET_POS", "LED_ON", etc.).
        :return: The response from the Arduino.
        """
        # Send the command to the Arduino
        await self._aioserial.write_async((command + "\n").encode())
        
        # Wait for the response
        response = await self._aioserial.read_until_async(b"\n")
        return response.decode().strip()

    async def wait_for_ready(self):
        """
        Wait for the Arduino to send its "ready" message.
        """
        while True:
            response = await self._aioserial.read_until_async(b"\n")
            response = response.decode().strip()
            if "microMONET is ready for some stargazing!" in response:
                print("Arduino is ready!")
                break

    async def get_position(self) -> Tuple[float, float]:
        """
        Get the current altitude and azimuth position from the Arduino.
        
        :return: A tuple containing (altitude, azimuth) in degrees.
        """
        response = await self.send_command("GET_POS")
        
        # Try to parse the response in the expected format (e.g., "ALT: 45.0 AZ: 90.0")
        match = re.match(r"ALT: ([\d.]+) AZ: ([\d.]+)", response)
        if match:
            return float(match.group(1)), float(match.group(2))
        
        # Try to parse the response in the "aborted" format (e.g., "Aborted at ALT: 39.90 AZ: 246.45")
        match = re.match(r"Aborted at ALT: ([\d.]+) AZ: ([\d.]+)", response)
        if match:
            return float(match.group(1)), float(match.group(2))
        
        # If neither format matches, raise an error
        raise ValueError(f"Invalid position response: {response}")

    async def set_position(self, altitude: float, azimuth: float):
        """
        Command the Arduino to slew to a specific altitude and azimuth.
        
        :param altitude: The target altitude in degrees.
        :param azimuth: The target azimuth in degrees.
        """
        command = f"ALT:{altitude} AZ:{azimuth}"
        await self.send_command(command)

    async def set_speed(self, speed: int):
        """
        Set the motor speed in RPM (1-15).
        
        :param speed: The motor speed in RPM.
        """
        if speed < 1 or speed > 15:
            raise ValueError("Speed must be between 1 and 15 RPM.")
        await self.send_command(f"SET_SPEED {speed}")

    async def led_on(self):
        """Turn the LED on."""
        await self.send_command("LED_ON")

    async def led_off(self):
        """Turn the LED off."""
        await self.send_command("LED_OFF")

    async def ccd_on(self):
        """Turn the CCD LED on."""
        await self.send_command("CCD_ON")

    async def ccd_off(self):
        """Turn the CCD LED off."""
        await self.send_command("CCD_OFF")

    async def get_temperature(self) -> float:
        """
        Get the temperature reading from the DHT11 sensor.
        
        :return: The temperature in degrees Celsius.
        """
        response = await self.send_command("GET_TEMP")
        # Parse the response (e.g., "Temperature: 25.0 °C")
        match = re.match(r"Temperature: ([\d.]+)", response)
        if match:
            return float(match.group(1))
        else:
            raise ValueError(f"Invalid temperature response: {response}")

    async def get_humidity(self) -> float:
        """
        Get the humidity reading from the DHT11 sensor.
        
        :return: The humidity in percentage.
        """
        response = await self.send_command("GET_HUMI")
        # Parse the response (e.g., "Humidity: 50.0 %")
        match = re.match(r"Humidity: ([\d.]+)", response)
        if match:
            return float(match.group(1))
        else:
            raise ValueError(f"Invalid humidity response: {response}")

    async def abort_slew(self):
        """Abort the current slew operation."""
        await self.send_command("ABORT")

    async def close(self):
        """Close the serial connection."""
        self._aioserial.close()