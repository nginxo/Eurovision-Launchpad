# Eurovision Launchpad Controller

A comprehensive control system for managing Eurovision-like live events using a Novation Launchpad Mini, or any Launchpad but they aren't fully tested, OBS Studio, and VLC media player. This project provides an intuitive interface for switching between camera scenes, controlling background music, and managing special effects during live broadcasts.

## ⚠️ Legal Disclaimer

**This project is NOT affiliated with the European Broadcasting Union (EBU) or Eurovision in any way.** This is an independent, non-commercial project created for educational and entertainment purposes only. The name "Eurovision" is used purely for descriptive purposes to indicate the style of event this controller is designed for.

**This software is provided free of charge and generates no revenue.** The developer assumes no responsibility for any legal issues that may arise from its use. Users are responsible for ensuring compliance with all applicable laws and regulations in their jurisdiction.

## 🔊 Audio Files Source

This project is based on the official Eurovision Song Contest 2024's OST that is published on Eurovision's Channel.

## 🎛️ Features

- **Multi-Menu System**: 4 different control modes (Scenes, Music, Effects, Utility)
- **Scene Management**: Control up to 16 different camera angles and scenes
- **Audio Control**: Play background music with real-time progress tracking
- **Visual Effects**: Flash lights, celebration modes, and voting sequences
- **OBS Integration**: Seamless scene switching in OBS Studio
- **VLC Integration**: Professional audio playback with volume control
- **LED Feedback**: Color-coded button illumination for easy operation

## 📋 Requirements

### Hardware
- Novation Launchpad Mini [Preferably] (MK1, MK2 or MK3) | If your Launchpad doesn't support certain colour types, it will fallback to a gradient or another colour.
- Computer with USB port
- Audio interface (recommended for professional audio output)

### Software Dependencies
```bash
pip install mido python-rtmidi vlc-python obsws-python
```

### External Software
- **OBS Studio** (with WebSocket plugin enabled)
- **VLC Media Player** (for audio playback)

## 🔧 Installation & Setup

### 1. Hardware Setup
1. Connect your Novation Launchpad Mini to your computer via USB
2. Ensure the device is recognized by your operating system
3. Install any necessary drivers (usually automatic)

### 2. Software Installation
1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install OBS Studio and enable the WebSocket server:
   - Go to Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set port to 4455
   - Set a password (remember this for configuration)

### 3. Configuration

#### OBS Configuration
The script will create a `eurovision_config.json` file on first run. Edit this file to match your setup:

```json
{
    "obs": {
        "host": "localhost",
        "port": 4455,
        "password": "your_password_here" # When asking for support, don't share this line!
    },
    "music_files": {
        "intro": "music/eurovision-intro.mp3",
        "hosts": "music/hosts.mp3",
        "green-room": "music/green-room.mp3",
        "northernlights": "music/northern-lights.mp3",
        "malmoarena": "music/malmo-arena.mp3",
        "beginning": "music/beginning.mp3",
        "stageready": "music/stage-ready.mp3",
        "postcard-piano": "music/postcard-piano.mp3",
        "postcard-flow": "music/postcard-flow.mp3",
        "postcard-drums": "music/postcard-drums.mp3",
        "postcard-dreams": "music/postcard-dreams.mp3",
        "postcard-calm": "music/postcard-calm.mp3",
        "postcard-arpeggio": "music/postcard-arpeggio.mp3",
        "voting-music": "music/voting-music.mp3",
        "lines-closed": "music/lines-closed.mp3",
        "douze-points": "music/douze-points.mp3",
        "winners-theme": "music/winners-theme.mp3",
        "winners-walk": "music/winners-walk.mp3"
    },
    "scenes": {
        "intro": "Eurovision Intro",
        "video": "Eurovision Video",
        "stage1": "Main Stage CAM1",
        "stage2": "Main Stage CAM2",
        "stage3": "Main Stage CAM3",
        "stage4": "Main Stage CAM4",
        "stage5": "Main Stage CAM5",
        "stage6": "Main Stage CAM6",
        "stage7": "Main Stage CAM7",
        "stage8": "Main Stage CAM8",
        "greenroom1": "Green Room CAM1",
        "greenroom2": "Green Room CAM2",
        "greenroom3": "Green Room CAM3",
        "greenroom4": "Green Room CAM4",
        "break": "Commercial Break",
        "scoreboard": "Scoreboard",
        "winner": "Winner Announcement",
        "credits": "End Credits",
        "backup": "Technical Difficulties"
    }
}
```

#### Scene Names
Replace the scene names in the config file with your actual OBS scene names. The scene keys (like "intro", "stage1") must match what's used in the code, but the values should be your actual OBS scene names.

## 🎵 Adding Music

### 1. Create Music Directory
Create a `music/` folder in your project directory:
```
eurovision_controller/
├── launchpad_control.py
├── eurovision_config.json
└── music/
    ├── eurovision_intro.mp3
    ├── interval_act.mp3
    ├── tension_music.mp3
    ├── winner_fanfare.mp3
    ├── hosts.mp3
    ├── credits.mp3
    ├── greenroom.mp3
    └── break_intro.mp3
```

### 2. Supported Audio Formats
- MP3 (recommended)
- WAV
- FLAC
- OGG
- Any format supported by VLC

### 3. Music File Configuration
Edit the `music_files` section in `eurovision_config.json`:

```json
"music_files": {
        "intro": "music/eurovision-intro.mp3",
        "hosts": "music/hosts.mp3",
        "green-room": "music/green-room.mp3",
        "northernlights": "music/northern-lights.mp3",
        "malmoarena": "music/malmo-arena.mp3",
        "beginning": "music/beginning.mp3",
        "stageready": "music/stage-ready.mp3",
        "postcard-piano": "music/postcard-piano.mp3",
        "postcard-flow": "music/postcard-flow.mp3",
        "postcard-drums": "music/postcard-drums.mp3",
        "postcard-dreams": "music/postcard-dreams.mp3",
        "postcard-calm": "music/postcard-calm.mp3",
        "postcard-arpeggio": "music/postcard-arpeggio.mp3",
        "voting-music": "music/voting-music.mp3",
        "lines-closed": "music/lines-closed.mp3",
        "douze-points": "music/douze-points.mp3",
        "winners-theme": "music/winners-theme.mp3",
        "winners-walk": "music/winners-walk.mp3"
}
```

### 4. Audio Tips
- Use consistent audio levels (normalize your tracks)
- Recommended bitrate: 320kbps MP3 or higher
- Keep file sizes reasonable for quick loading
- Test all audio files before live use

## 🎨 Button Layout & LED Colors

**Note**: These button mappings are hardcoded in the Python file. To change them, you must edit the `menu_functions` and `menu_colors` dictionaries in `launchpad_control.py`.

### Menu Selection (Circular Buttons - Hardcoded)
- **Button 8** (Top-Right): SCENES Menu (Blue)
- **Button 24** (Middle-Right): MUSIC Menu (Green)  
- **Button 40** (Bottom-Right): EFFECTS Menu (Amber)
- **Button 56** (Bottom-Left): UTILITY Menu (Orange)

### 🎬 SCENES Menu (Blue Circle Button)

*Defined in `menu_functions[MenuMode.SCENES]` starting around line 90*

| Button | Function             | LED Color | Scene Key  |
| ------ | -------------------- | --------- | ---------- |
| 0      | `scene_intro()`      | Yellow    | intro      |
| 1      | `scene_video()`      | Yellow    | video      |
| 6      | `backup_scene()`     | Red       | backup     |
| 7      | `scene_break()`      | Yellow    | break      |
| 16     | `scene_stage1()`     | Green     | stage1     |
| 17     | `scene_stage2()`     | Green     | stage2     |
| 18     | `scene_stage3()`     | Green     | stage3     |
| 19     | `scene_stage4()`     | Green     | stage4     |
| 20     | `scene_stage5()`     | Green     | stage5     |
| 21     | `scene_stage6()`     | Green     | stage6     |
| 22     | `scene_stage7()`     | Green     | stage7     |
| 23     | `scene_stage8()`     | Green     | stage8     |
| 32     | `scene_greenroom1()` | Yellow    | greenroom1 |
| 33     | `scene_greenroom2()` | Yellow    | greenroom2 |
| 34     | `scene_greenroom3()` | Yellow    | greenroom3 |
| 35     | `scene_greenroom4()` | Yellow    | greenroom4 |
| 64     | `scene_scoreboard()` | Red       | scoreboard |
| 65     | `scene_winner()`     | Yellow    | winner     |
| 66     | `scene_credits()`    | Green     | credits    |


### 🎵 MUSIC Menu (Green Circle Button)

*Defined in `menu_functions[MenuMode.MUSIC]` starting around line 105*

| Button | Function                              | LED Color | Music Key         |
| ------ | ------------------------------------- | --------- | ----------------- |
| 0      | `play_music("intro", 0)`              | Green     | intro             |
| 1      | `play_music("northernlights", 1)`     | Green     | northernlights    |
| 2      | `play_music("malmoarena", 2)`         | Green     | malmoarena        |
| 3      | `play_music("beginning", 3)`          | Amber     | beginning         |
| 7      | `play_music("stageready", 7)`         | Yellow    | stageready        |
| 16     | `play_music("hosts", 16)`             | Blue      | hosts             |
| 17     | `play_music("green-room", 17)`        | Blue      | green-room        |
| 48     | `play_music("postcard-piano", 48)`    | Red       | postcard-piano    |
| 49     | `play_music("postcard-flow", 49)`     | Red       | postcard-flow     |
| 50     | `play_music("postcard-drums", 50)`    | Red       | postcard-drums    |
| 51     | `play_music("postcard-dreams", 51)`   | Red       | postcard-dreams   |
| 52     | `play_music("postcard-calm", 52)`     | Red       | postcard-calm     |
| 53     | `play_music("postcard-arpeggio", 53)` | Red       | postcard-arpeggio |
| 80     | `play_music("voting-music", 80)`      | Green     | voting-music      |
| 81     | `play_music("lines-closed", 81)`      | Red       | lines-closed      |
| 82     | `play_music("douze-points", 82)`      | Amber     | douze-points      |
| 96     | `play_music("winners-theme", 96)`     | Yellow    | winners-theme     |
| 97     | `play_music("winners-walk", 97)`      | Yellow    | winners-walk      |
| 72     | `stop_music()`                        | Red       | -                 |
| 88     | `volume_up()`                         | Green     | -                 |
| 104    | `volume_down()`                       | Red       | -                 |
| 120    | `mute_toggle()`                       | Orange    | -                 |


### EFFECTS Menu (Amber Circle Button)
*Defined in `menu_functions[MenuMode.EFFECTS]` starting around line 117*

| Button |     Function     | LED Color |
|--------|------------------|-----------|
| 32     |   flash_lights   |   Yellow  |
| 33     | celebration_mode |   Amber   |
| 34     |    voting_mode   |   Orange  |
| 35     |  technical_break |   Amber   |

### UTILITY Menu (Orange Circle Button)
*Defined in `menu_functions[MenuMode.UTILITY]` starting around line 122*

| Button |    Function    | LED Color |
|--------|----------------|-----------|
| 48     |    reset_all   |    Red    |
| 49     |    test_mode   |    Blue   |
| 50     | emergency_stop |    Red    |
| 51     |   show_status  |   Green   |

## 🔧 Customizing Buttons & LEDs

**Important**: All button mappings and LED colors are defined directly in the Python code, not in the config file. To customize buttons, you need to edit `launchpad_control.py`.

### Adding New Functions
1. Define the function in the `EurovisionController` class:
```python
def my_custom_function(self):
    """Your custom function"""
    logger.info("Custom function executed")
    # Your code here
```

2. Add the function to the appropriate menu in the `menu_functions` dictionary (around line 90):
```python
self.menu_functions = {
    MenuMode.SCENES: {
        # existing buttons...
        72: self.my_custom_function,  # Add new button mapping
    },
    # other menus...
}
```

3. Set the LED color in the `menu_colors` dictionary (around line 130):
```python
self.menu_colors = {
    MenuMode.SCENES: {
        # existing colors...
        72: LaunchpadColors.BLUE_FULL,  # Set button color
    },
    # other menus...
}
```

### Modifying Existing Button Mappings
To change what a button does, find the button number in the `menu_functions` dictionary and change the function assignment:

```python
# Example: Change button 16 from scene_stage1 to scene_intro
MenuMode.SCENES: {
    16: self.scene_intro,  # Changed from self.scene_stage1
    # other buttons...
}
```

### Available LED Colors
```python
LaunchpadColors.OFF = 0           # No light
LaunchpadColors.RED_LOW = 1       # Dim red
LaunchpadColors.RED_FULL = 3      # Bright red
LaunchpadColors.AMBER_LOW = 17    # Dim amber
LaunchpadColors.AMBER_FULL = 51   # Bright amber
LaunchpadColors.YELLOW_FULL = 50  # Bright yellow
LaunchpadColors.GREEN_LOW = 16    # Dim green
LaunchpadColors.GREEN_FULL = 48   # Bright green
LaunchpadColors.ORANGE_FULL = 35  # Bright orange
LaunchpadColors.BLUE_FULL = 79    # Bright blue
```

### Button Numbering
The Launchpad Mini uses this button layout:
```
[  0][  1][  2][  3][  4][  5][  6][  7][ 8]
[ 16][ 17][ 18][ 19][ 20][ 21][ 22][ 23][24]
[ 32][ 33][ 34][ 35][ 36][ 37][ 38][ 39][40]
[ 48][ 49][ 50][ 51][ 52][ 53][ 54][ 55][56]
[ 64][ 65][ 66][ 67][ 68][ 69][ 70][ 71][72]
[ 80][ 81][ 82][ 83][ 84][ 85][ 86][ 87][88]
[ 96][ 97][ 98][ 99][100][101][102][103][104]
[112][113][114][115][116][117][118][119][120]
```

## 🚀 Running the Controller

1. Start OBS Studio and ensure WebSocket server is running
2. Connect your Launchpad Mini
3. Run the controller:
   ```bash
   python launchpad_control.py
   ```
4. The Launchpad will perform a startup animation
5. Use the circular buttons to switch between menus
6. Press Ctrl+C to stop the controller

## 🔧 Troubleshooting

### Common Issues

**Launchpad not detected:**
- Ensure the device is properly connected
- Check if drivers are installed
- Try a different USB port

**OBS connection failed:**
- Verify OBS WebSocket server is enabled
- Check host, port, and password in config
- Ensure OBS is running before starting the controller

**Music files not playing:**
- Check file paths in configuration
- Verify VLC is installed
- Ensure audio files are in supported formats

**Scene switching not working:**
- Verify scene names match exactly (case-sensitive)
- Check OBS WebSocket connection
- Ensure scenes exist in OBS

### Debug Mode
Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 📝 Configuration Tips

1. **Test thoroughly** before live use
2. **Create backups** of your configuration
3. **Use consistent naming** for scenes and music files
4. **Keep file paths relative** for portability
5. **Document your custom functions** for future reference

## 🤝 Contributing

This is an open-source project. Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests
- Share your custom configurations

## 📄 License

This project is provided as-is for educational and entertainment purposes. MIT license. Use at your own risk and ensure compliance with all applicable laws and regulations.

---

**Remember**: This project is not affiliated with Eurovision or the EBU. It's designed for creating your own Eurovision-style events and broadcasts.