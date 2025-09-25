#!/usr/bin/env python3
"""Demo script for IKEA OBEGRÄNSAD LED Control."""
import ikea_led_obegraensad_python_control
import time

def main():
    """Main demo function."""
    # Connect to the device - change this IP address to match your device
    light = ikea_led_obegraensad_python_control.setup("192.168.5.60")

    # Initialize the device
    light.turn_on()
    light.set_plugin(9)

    print("IKEA OBEGRÄNSAD LED Controller Started!")
    print("Commands:")
    print("  b <value>  - Set brightness (0-255)")
    print("  p <id>     - Set plugin ID")
    print("  r <dir>    - Rotate display (left/right)")
    print("  on         - Turn on")
    print("  off        - Turn off")
    print("  info       - Show current state")
    print("  q          - Quit")
    print("\nPress Ctrl+C to exit\n")

    try:
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == 'q':
                    break
                elif command == 'on':
                    light.turn_on()
                    print("Light turned on")
                elif command == 'off':
                    light.turn_off()
                    print("Light turned off")
                elif command == 'info':
                    info = light.get_info()
                    print(f"Current state: {info}")
                elif command.startswith('b '):
                    try:
                        brightness = int(command.split()[1])
                        light.set_brightness(brightness)
                        print(f"Brightness set to {brightness}")
                    except (IndexError, ValueError):
                        print("Invalid brightness value. Use: b <0-255>")
                elif command.startswith('p '):
                    try:
                        plugin_id = int(command.split()[1])
                        light.set_plugin(plugin_id)
                        print(f"Plugin set to {plugin_id}")
                    except (IndexError, ValueError):
                        print("Invalid plugin ID. Use: p <number>")
                elif command.startswith('r '):
                    try:
                        direction = command.split()[1]
                        if direction in ['left', 'right']:
                            light.set_rotation(direction)
                            print(f"Rotated {direction}")
                        else:
                            print("Invalid direction. Use: r left or r right")
                    except IndexError:
                        print("Missing direction. Use: r <left|right>")
                else:
                    print("Unknown command. Type 'q' to quit or use the commands listed above.")
                    
            except EOFError:
                break
            except Exception as e:
                print(f"Error executing command: {e}")
                
    except KeyboardInterrupt:
        print("\nShutting down...")

    print("Goodbye!")

if __name__ == "__main__":
    main()