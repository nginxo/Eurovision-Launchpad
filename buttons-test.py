import mido
import time

def test_launchpad():
    print("=== TEST LAUNCHPAD ===")
    
    print("Input devices:", mido.get_input_names())
    print("Output devices:", mido.get_output_names())
    
    input_name = None
    output_name = None
    
    for name in mido.get_input_names():
        if "launchpad" in name.lower():
            input_name = name
            break
    
    for name in mido.get_output_names():
        if "launchpad" in name.lower():
            output_name = name
            break
    
    if not input_name or not output_name:
        print("❌ Launchpad not found!")
        return False

    print(f"Found Launchpad: {input_name} / {output_name}")

    try:
        launchpad_in = mido.open_input(input_name)
        launchpad_out = mido.open_output(output_name)

        print("✅ Connected to Launchpad!")

        print("Turning on all LEDs...")
        for i in range(128):
            msg = mido.Message('note_on', channel=0, note=i, velocity=3) 
            launchpad_out.send(msg)
            time.sleep(0.001)
        
        time.sleep(1)
        
        print("Turning off all LEDs...")
        for i in range(128):
            msg = mido.Message('note_on', channel=0, note=i, velocity=0)
            launchpad_out.send(msg)

        print("✅ LED test completed!")
        print("Now press some buttons on the Launchpad...")
        print("Press Ctrl+C to exit")

        # Listen for input
        for message in launchpad_in:
            print(f"Received: {message}")

            if message.type == 'note_on' and message.velocity > 0:
                pad = message.note
                print(f"🔘 Button {pad} pressed!")

                msg = mido.Message('note_on', channel=0, note=pad, velocity=48) 
                launchpad_out.send(msg)
    
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            for i in range(128):
                msg = mido.Message('note_on', channel=0, note=i, velocity=0)
                launchpad_out.send(msg)
            launchpad_in.close()
            launchpad_out.close()
        except:
            pass
        print("👋 Test completed!")

if __name__ == "__main__":
    test_launchpad()