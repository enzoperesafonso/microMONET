from mimo import MicroMONET
import asyncio

async def main():
    # Initialize the MicroMONET class
    micro_monet = MicroMONET(device="/dev/cu.usbmodem142101", baudrate=9600)
    
    try:
        # Wait for the Arduino to be ready
        print("Waiting for Arduino to initialize...")
        await micro_monet.wait_for_ready()
        
        while True:
            # Display menu
            print("\n--- MicroMONET Control Menu ---")
            print("1. Get Current Position")
            print("2. Set New Position")
            print("3. Turn LED On")
            print("4. Turn LED Off")
            print("5. Turn CCD LED On")
            print("6. Turn CCD LED Off")
            print("7. Get Temperature")
            print("8. Get Humidity")
            print("9. Abort Slew")
            print("10. Exit")
            
            # Get user input
            choice = input("Enter your choice (1-10): ").strip()
            
            if choice == "1":
                # Get current position
                alt, az = await micro_monet.get_position()
                print(f"Current Position - ALT: {alt}, AZ: {az}")
            
            elif choice == "2":
                # Set new position
                try:
                    alt = float(input("Enter target altitude (degrees): "))
                    az = float(input("Enter target azimuth (degrees): "))
                    await micro_monet.set_position(altitude=alt, azimuth=az)
                    print("Slewing to new position...")
                    
                    # Wait for slew to complete or allow abort
                    while True:
                        alt_current, az_current = await micro_monet.get_position()
                        print(f"Current Position - ALT: {alt_current}, AZ: {az_current}")
                        
                        if abs(alt_current - alt) < 0.1 and abs(az_current - az) < 0.1:
                            print("Slew completed successfully!")
                            break
                        
                        # Check if user wants to abort
                        abort = input("Type 'ABORT' to stop the slew or press Enter to continue: ").strip()
                        if abort.upper() == "ABORT":
                            await micro_monet.abort_slew()
                            print("Slew aborted!")
                            break
                except ValueError:
                    print("Invalid input! Please enter numeric values for altitude and azimuth.")
            
            elif choice == "3":
                # Turn LED on
                await micro_monet.led_on()
                print("LED turned on.")
            
            elif choice == "4":
                # Turn LED off
                await micro_monet.led_off()
                print("LED turned off.")
            
            elif choice == "5":
                # Turn CCD LED on
                await micro_monet.ccd_on()
                print("CCD LED turned on.")
            
            elif choice == "6":
                # Turn CCD LED off
                await micro_monet.ccd_off()
                print("CCD LED turned off.")
            
            elif choice == "7":
                # Get temperature
                try:
                    temperature = await micro_monet.get_temperature()
                    print(f"Temperature: {temperature} °C")
                except ValueError as e:
                    print(e)
            
            elif choice == "8":
                # Get humidity
                try:
                    humidity = await micro_monet.get_humidity()
                    print(f"Humidity: {humidity} %")
                except ValueError as e:
                    print(e)
            
            elif choice == "9":
                # Abort slew
                await micro_monet.abort_slew()
                print("Slew aborted!")
            
            elif choice == "10":
                # Exit
                print("Exiting...")
                break
            
            else:
                print("Invalid choice! Please enter a number between 1 and 10.")
    
    finally:
        # Close the connection
        await micro_monet.close()

# Run the asyncio event loop
asyncio.run(main())