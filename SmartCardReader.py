import os
import time
import subprocess
import sys
from smartcard.System import readers
from smartcard.util import toHexString

def restart_smart_card_service():
    """Restarts the Windows Smart Card Service (requires Admin)."""
    print("-" * 50)
    print("Step 1: Resetting Windows Smart Card Service...")
    try:
        # Stop and Start using the Windows Service Controller (sc)
        subprocess.run(["sc", "stop", "SCardSvr"], capture_output=True)
        time.sleep(1)
        result = subprocess.run(["sc", "start", "SCardSvr"], capture_output=True)
        
        if result.returncode == 0:
            print("✅ Service restarted and ready.")
        else:
            print("⚠️ Could not restart service. (Are you running as Admin?)")
    except Exception as e:
        print(f"❌ Error resetting service: {e}")
    print("-" * 50)

def search_for_card():
    """Main loop to catch the connection as it flickers."""
    print("\nStep 2: Searching for your Pakistan Smart ID...")
    print("Note: If the light blinks, hold the card firmly in that position.")
    
    while True:
        try:
            available_readers = readers()
            if not available_readers:
                print("🔴 No reader found! Is the keyboard plugged in?", end="\r")
                time.sleep(1)
                continue

            # Target the Dell Keyboard Reader
            reader = available_readers[0]
            connection = reader.createConnection()

            # Connect in SHARED mode (1) to be less sensitive to disconnects
            connection.connect(mode=1)

            # Grab the ATR (the card's hardware fingerprint)
            atr = connection.getATR()
            print("\n" + "=" * 50)
            print("✨ SUCCESS! CARD DETECTED.")
            print(f"READER: {reader}")
            print(f"CARD ID (ATR): {toHexString(atr)}")
            print("=" * 50)

            # --- Stability Test ---
            print("\nStep 3: Testing connection stability for 5 seconds...")
            print("Hold the card PERFECTLY STILL now.")
            
            for i in range(5, 0, -1):
                # Send a 'Heartbeat' command to verify card is still there
                connection.transmit([0x00, 0xA4, 0x00, 0x00])
                print(f"  Stability Check... {i}", end="\r")
                time.sleep(1)
            
            print("\n\n✅ CONNECTION STABLE! Your hardware is functioning.")
            break # Exit the script once a stable read is achieved

        except Exception:
            # Silently keep trying while the connection flickers or is loose
            print("🔴 No contact... adjust pressure or flip card (Chip UP)", end="\r")
            time.sleep(0.1)

if __name__ == "__main__":
    # Check if the required library is installed
    try:
        from smartcard.System import readers
    except ImportError:
        print("❌ Error: 'pyscard' library not found.")
        print("Run: pip install pyscard")
        sys.exit()

    restart_smart_card_service()
    search_for_card()
