#!/usr/bin/env python3
"""
Eurovision Control Center - Enhanced Launchpad Mini Controller
A comprehensive control system for managing Eurovision-like live events
using a Novation Launchpad Mini, OBS Studio, and VLC media player.

Enhanced with menu system and audio progress features.
"""

import mido
import time
import threading
import vlc
import os
import json
import logging
from typing import Dict, Optional, Callable
from obsws_python import ReqClient as ObsWS
from obsws_python.error import OBSSDKError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LaunchpadColors:
    OFF = 0
    RED_LOW = 1
    RED_FULL = 3
    AMBER_LOW = 17
    AMBER_FULL = 51
    YELLOW_FULL = 50
    GREEN_LOW = 16
    GREEN_FULL = 48
    ORANGE_FULL = 35
    BLUE_FULL = 79

class MenuMode:
    SCENES = 0
    MUSIC = 1
    EFFECTS = 2
    UTILITY = 3

class EurovisionController:
    def __init__(self, config_file="eurovision_config.json"):
        self.config = self.load_config(config_file)
        self.launchpad_input = None
        self.launchpad_output = None
        self.obs_client = None
        self.vlc_instance = vlc.Instance()
        self.current_player = None
        self.current_scene = None
        self.current_music = None
        self.current_music_button = None
        self.running = False
        self.current_menu = MenuMode.SCENES
        self.progress_pads = list(range(112, 120))
        self.audio_thread = None
        self.audio_monitoring = False
        self.circular_buttons = {
            8: MenuMode.SCENES,
            24: MenuMode.MUSIC,
            40: MenuMode.EFFECTS,
            56: MenuMode.UTILITY
        }
        self.menu_functions = {
            MenuMode.SCENES: {
                0: self.scene_intro,
                1: self.scene_video,
                16: self.scene_stage1,
                17: self.scene_stage2,
                18: self.scene_stage3,
                19: self.scene_stage4,
                20: self.scene_stage5,
                21: self.scene_stage6,
                22: self.scene_stage7,
                23: self.scene_stage8,
                32: self.scene_greenroom1,
                33: self.scene_greenroom2,
                34: self.scene_greenroom3,
                35: self.scene_greenroom4,
                7: self.scene_break,
                64: self.scene_scoreboard,
                65: self.scene_winner,
                66: self.scene_credits,
                6: self.backup_scene,
            },
            MenuMode.MUSIC: {
                0: lambda: self.play_music("intro", 0),
                1: lambda: self.play_music("breakintro", 1),
                2: lambda: self.play_music("hosts", 2),
                3: lambda: self.play_music("greenroom", 3),
                4: lambda: self.play_music("interval", 4),
                5: lambda: self.play_music("tension", 5),
                6: lambda: self.play_music("winner", 6),
                7: lambda: self.play_music("credits", 7),
                32: self.stop_music,
                33: self.volume_up,
                34: self.volume_down,
                35: self.mute_toggle,
            },
            MenuMode.EFFECTS: {
                32: self.flash_lights,
                33: self.celebration_mode,
                34: self.voting_mode,
                35: self.technical_break,
            },
            MenuMode.UTILITY: {
                48: self.reset_all,
                49: self.test_mode,
                50: self.emergency_stop,
                51: self.show_status,
            }
        }
        self.menu_colors = {
            MenuMode.SCENES: {
                0: LaunchpadColors.YELLOW_FULL,
                1: LaunchpadColors.YELLOW_FULL,
                16: LaunchpadColors.GREEN_FULL,
                17: LaunchpadColors.GREEN_FULL,
                18: LaunchpadColors.GREEN_FULL,
                19: LaunchpadColors.GREEN_FULL,
                20: LaunchpadColors.GREEN_FULL,
                21: LaunchpadColors.GREEN_FULL,
                22: LaunchpadColors.GREEN_FULL,
                23: LaunchpadColors.GREEN_FULL,
                32: LaunchpadColors.YELLOW_FULL,
                33: LaunchpadColors.YELLOW_FULL,
                34: LaunchpadColors.YELLOW_FULL,
                35: LaunchpadColors.YELLOW_FULL,
                7: LaunchpadColors.YELLOW_FULL,
                64: LaunchpadColors.RED_FULL,
                65: LaunchpadColors.YELLOW_FULL,
                66: LaunchpadColors.GREEN_FULL,
                6: LaunchpadColors.RED_FULL,
            },
            MenuMode.MUSIC: {
                0: LaunchpadColors.GREEN_FULL,
                1: LaunchpadColors.GREEN_FULL,
                2: LaunchpadColors.GREEN_FULL,
                3: LaunchpadColors.AMBER_FULL,
                4: LaunchpadColors.AMBER_FULL,
                5: LaunchpadColors.RED_FULL,
                6: LaunchpadColors.GREEN_FULL,
                7: LaunchpadColors.YELLOW_FULL,
                32: LaunchpadColors.RED_FULL,
                33: LaunchpadColors.GREEN_FULL,
                34: LaunchpadColors.RED_FULL,
                35: LaunchpadColors.ORANGE_FULL,
            },
            MenuMode.EFFECTS: {
                32: LaunchpadColors.YELLOW_FULL,
                33: LaunchpadColors.AMBER_FULL,
                34: LaunchpadColors.ORANGE_FULL,
                35: LaunchpadColors.AMBER_FULL,
            },
            MenuMode.UTILITY: {
                48: LaunchpadColors.RED_FULL,
                49: LaunchpadColors.BLUE_FULL,
                50: LaunchpadColors.RED_FULL,
                51: LaunchpadColors.GREEN_FULL,
            }
        }
        self.circular_button_colors = {
            8: LaunchpadColors.BLUE_FULL,
            24: LaunchpadColors.GREEN_FULL,
            40: LaunchpadColors.AMBER_FULL,
            56: LaunchpadColors.ORANGE_FULL,
        }

    def load_config(self, config_file: str) -> Dict:
        default_config = {
            "obs": {
            "host": "localhost",
             "port": 4455,
             "password": "your_password_here"
            },
            "music_files": {
            "intro": "music/eurovision_intro.mp3",
            "interval": "music/interval_act.mp3",
            "tension": "music/tension_music.mp3",
            "winner": "music/winner_fanfare.mp3",
            "hosts": "music/hosts.mp3",
            "credits": "music/credits.mp3",
            "greenroom": "music/greenroom.mp3",
            "breakintro": "music/break_intro.mp3"
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
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
            else:
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                logger.info(f"Created default config file: {config_file}")
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def initialize_launchpad(self) -> bool:
        try:
            input_names = mido.get_input_names()
            output_names = mido.get_output_names()
            launchpad_input_name = None
            launchpad_output_name = None
            for name in input_names:
                if "Launchpad Mini" in name:
                    launchpad_input_name = name
                    break
            for name in output_names:
                if "Launchpad Mini" in name:
                    launchpad_output_name = name
                    break
            if not launchpad_input_name or not launchpad_output_name:
                logger.error("Launchpad Mini not found! Please connect your device.")
                return False
            self.launchpad_input = mido.open_input(launchpad_input_name)
            self.launchpad_output = mido.open_output(launchpad_output_name)
            logger.info(f"Connected to Launchpad Mini: {launchpad_input_name}")
            self.reset_launchpad_leds()
            self.startup_animation()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Launchpad: {e}")
            return False

    def initialize_obs(self) -> bool:
        try:
            self.obs_client = ObsWS(
                host=self.config["obs"]["host"],
                port=self.config["obs"]["port"],
                password=self.config["obs"]["password"]
            )
            version_info = self.obs_client.get_version()
            logger.info(f"Connected to OBS Studio {version_info.obs_version}")
            current_scene_info = self.obs_client.get_current_program_scene()
            self.current_scene = current_scene_info.current_program_scene_name
            logger.info(f"Current OBS scene: {self.current_scene}")
            return True
        except OBSSDKError as e:
            logger.error(f"Failed to connect to OBS: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to OBS: {e}")
            return False

    def reset_launchpad_leds(self):
        if not self.launchpad_output:
            return
        for note in range(128):
            msg = mido.Message('note_on', channel=0, note=note, velocity=0)
            self.launchpad_output.send(msg)

    def set_pad_color(self, pad_number: int, color: int):
        if not self.launchpad_output:
            return
        msg = mido.Message('note_on', channel=0, note=pad_number, velocity=color)
        self.launchpad_output.send(msg)

    def startup_animation(self):
        if not self.launchpad_output:
            return
        colors = [LaunchpadColors.RED_FULL, LaunchpadColors.AMBER_FULL, 
                 LaunchpadColors.GREEN_FULL, LaunchpadColors.BLUE_FULL]
        for color in colors:
            for pad in range(128):
                self.set_pad_color(pad, color)
                time.sleep(0.001)
            time.sleep(0.2)
        self.update_menu_display()

    def update_menu_display(self):
        for pad in range(128):
            self.set_pad_color(pad, LaunchpadColors.OFF)
        for button, menu_mode in self.circular_buttons.items():
            if menu_mode == self.current_menu:
                self.set_pad_color(button, LaunchpadColors.RED_FULL)
            else:
                self.set_pad_color(button, self.circular_button_colors[button])
        if self.current_menu in self.menu_colors:
            for pad, color in self.menu_colors[self.current_menu].items():
                self.set_pad_color(pad, color)

    def switch_menu(self, menu_mode: int):
        self.current_menu = menu_mode
        self.update_menu_display()
        menu_names = ["SCENES", "MUSIC", "EFFECTS", "UTILITY"]
        logger.info(f"Switched to {menu_names[menu_mode]} menu")

    def flash_pad(self, pad_number: int, duration: float = 0.5):
        original_color = self.get_pad_current_color(pad_number)
        def flash():
            self.set_pad_color(pad_number, LaunchpadColors.RED_FULL)
            time.sleep(duration)
            self.set_pad_color(pad_number, original_color)
        threading.Thread(target=flash, daemon=True).start()

    def get_pad_current_color(self, pad_number: int) -> int:
        if self.current_menu in self.menu_colors:
            return self.menu_colors[self.current_menu].get(pad_number, LaunchpadColors.OFF)
        return LaunchpadColors.OFF

    def blink_music_button(self, pad_number: int):
        def blink():
            original_color = self.get_pad_current_color(pad_number)
            while self.current_player and self.current_music_button == pad_number:
                if self.current_player.get_state() == vlc.State.Playing:
                    self.set_pad_color(pad_number, LaunchpadColors.RED_FULL)
                    time.sleep(0.5)
                    self.set_pad_color(pad_number, LaunchpadColors.OFF)
                    time.sleep(0.5)
                else:
                    break
            self.set_pad_color(pad_number, original_color)
            self.current_music_button = None
        threading.Thread(target=blink, daemon=True).start()

    def update_progress_bar(self):
        def monitor_progress():
            while self.audio_monitoring and self.current_player:
                try:
                    if self.current_player.get_state() == vlc.State.Playing:
                        position = self.current_player.get_position()
                        total_pads = len(self.progress_pads)
                        lit_pads = int(position * total_pads)
                        for i, pad in enumerate(self.progress_pads):
                            if i < lit_pads:
                                self.set_pad_color(pad, LaunchpadColors.GREEN_FULL)
                            else:
                                self.set_pad_color(pad, LaunchpadColors.OFF)
                    elif self.current_player.get_state() in [vlc.State.Ended, vlc.State.Stopped]:
                        for pad in self.progress_pads:
                            self.set_pad_color(pad, LaunchpadColors.OFF)
                        break
                    time.sleep(0.01)
                except Exception as e:
                    logger.error(f"Error updating progress bar: {e}")
                    break
            for pad in self.progress_pads:
                self.set_pad_color(pad, LaunchpadColors.OFF)
            self.audio_monitoring = False
        if not self.audio_monitoring:
            self.audio_monitoring = True
            self.audio_thread = threading.Thread(target=monitor_progress, daemon=True)
            self.audio_thread.start()

    # Scene Control Methods
    def scene_intro(self):
        """Switch to intro scene"""
        self.switch_obs_scene(self.config["scenes"]["intro"])
        self.current_scene = "intro"
        logger.info("Switched to Intro scene")

    def scene_video(self):
        """Switch to video scene"""
        self.switch_obs_scene(self.config["scenes"]["video"])
        self.current_scene = "video"
        logger.info("Switched to Video scene")

    def scene_stage1(self):
        """Switch to main stage scene"""
        self.switch_obs_scene(self.config["scenes"]["stage1"])
        self.current_scene = "stage1"
        logger.info("Switched to Main Stage CAM1 scene")

    def scene_stage2(self):
        """Switch to main stage CAM2 scene"""
        self.switch_obs_scene(self.config["scenes"]["stage2"])
        self.current_scene = "stage2"
        logger.info("Switched to Main Stage CAM2 scene")

    def scene_stage3(self):
        """Switch to main stage CAM3 scene"""
        self.switch_obs_scene(self.config["scenes"]["stage3"])
        self.current_scene = "stage3"
        logger.info("Switched to Main Stage CAM3 scene")

    def scene_stage4(self):
        """Switch to main stage CAM4 scene"""
        self.switch_obs_scene(self.config["scenes"]["stage4"])
        self.current_scene = "stage4"
        logger.info("Switched to Main Stage CAM4 scene")
    
    def scene_stage5(self):
        """Switch to main stage scene"""
        self.switch_obs_scene(self.config["scenes"]["stage5"])
        self.current_scene = "stage5"
        logger.info("Switched to Main Stage CAM5 scene")

    def scene_stage6(self):
        """Switch to main stage scene"""
        self.switch_obs_scene(self.config["scenes"]["stage6"])
        self.current_scene = "stage6"
        logger.info("Switched to Main Stage CAM6 scene")

    def scene_stage7(self):
        """Switch to main stage scene"""
        self.switch_obs_scene(self.config["scenes"]["stage7"])
        self.current_scene = "stage7"
        logger.info("Switched to Main Stage CAM7 scene")

    def scene_stage8(self):
        """Switch to main stage scene"""
        self.switch_obs_scene(self.config["scenes"]["stage8"])
        self.current_scene = "stage8"
        logger.info("Switched to Main Stage CAM8 scene")

    def scene_greenroom1(self):
        """Switch to green room scene"""
        self.switch_obs_scene(self.config["scenes"]["greenroom1"])
        self.current_scene = "greenroom1"
        logger.info("Switched to Green Room CAM1 scene")

    def scene_greenroom2(self):
        """Switch to green room scene"""
        self.switch_obs_scene(self.config["scenes"]["greenroom2"])
        self.current_scene = "greenroom2"
        logger.info("Switched to Green Room CAM2 scene")

    def scene_greenroom3(self):
        """Switch to green room scene"""
        self.switch_obs_scene(self.config["scenes"]["greenroom3"])
        self.current_scene = "greenroom3"
        logger.info("Switched to Green Room CAM3 scene")

    def scene_greenroom4(self):
        """Switch to green room scene"""
        self.switch_obs_scene(self.config["scenes"]["greenroom4"])
        self.current_scene = "greenroom4"
        logger.info("Switched to Green Room CAM4 scene")

    def scene_break(self):
        """Switch to break/commercial scene"""
        self.switch_obs_scene(self.config["scenes"]["break"])
        self.current_scene = "break"
        logger.info("Switched to Break scene")

    def scene_scoreboard(self):
        """Switch to scoreboard scene"""
        self.switch_obs_scene(self.config["scenes"]["scoreboard"])
        self.current_scene = "scoreboard"
        logger.info("Switched to Scoreboard scene")

    def scene_winner(self):
        """Switch to winner announcement scene"""
        self.switch_obs_scene(self.config["scenes"]["winner"])
        self.current_scene = "winner"
        logger.info("Switched to Winner scene")

    def scene_credits(self):
        """Switch to credits scene"""
        self.switch_obs_scene(self.config["scenes"]["credits"])
        self.current_scene = "credits"
        logger.info("Switched to Credits scene")

    def backup_scene(self):
        """Switch to backup/technical difficulties scene"""
        self.switch_obs_scene(self.config["scenes"]["backup"])
        self.current_scene = "backup"
        logger.info("Switched to Backup scene")

    def switch_obs_scene(self, scene_name: str):
        """Switch OBS scene"""
        if not self.obs_client:
            logger.error("OBS not connected")
            return False
        try:
            self.obs_client.set_current_program_scene(scene_name)
            return True
        except OBSSDKError as e:
            logger.error(f"Failed to switch to scene '{scene_name}': {e}")
            return False

    # Music Control Methods
    def play_music(self, music_type: str, button_number: int):
        """Play a specific music file"""
        music_file = self.config["music_files"].get(music_type)
        if not music_file or not os.path.exists(music_file):
            logger.error(f"Music file not found: {music_file}")
            return
        self.stop_music()
        try:
            self.current_player = self.vlc_instance.media_player_new()
            media = self.vlc_instance.media_new(music_file)
            self.current_player.set_media(media)
            self.current_player.play()
            self.current_music = music_type
            self.current_music_button = button_number
            self.blink_music_button(button_number)
            self.update_progress_bar()
            logger.info(f"Playing {music_type} music: {music_file}")
        except Exception as e:
            logger.error(f"Failed to play music: {e}")

    def stop_music(self):
        """Stop currently playing music"""
        self.audio_monitoring = False
        if self.current_player:
            self.current_player.stop()
            self.current_player = None
            self.current_music = None
            self.current_music_button = None
            for pad in self.progress_pads:
                self.set_pad_color(pad, LaunchpadColors.OFF)
            logger.info("Music stopped")

    def volume_up(self):
        """Increase music volume"""
        if self.current_player:
            current_volume = self.current_player.audio_get_volume()
            new_volume = min(100, current_volume + 10)
            self.current_player.audio_set_volume(new_volume)
            logger.info(f"Volume: {new_volume}%")

    def volume_down(self):
        if self.current_player:
            current_volume = self.current_player.audio_get_volume()
            new_volume = max(0, current_volume - 10)
            self.current_player.audio_set_volume(new_volume)
            logger.info(f"Volume: {new_volume}%")

    def mute_toggle(self):
        if self.current_player:
            is_muted = self.current_player.audio_get_mute()
            self.current_player.audio_set_mute(not is_muted)
            logger.info("Audio " + ("unmuted" if is_muted else "muted"))

    # Special Effects Methods
    def flash_lights(self):
        def flash_sequence():
            original_menu = self.current_menu
            for _ in range(3):
                for pad in range(64):
                    self.set_pad_color(pad, LaunchpadColors.RED_FULL)
                time.sleep(0.1)
                for pad in range(64):
                    self.set_pad_color(pad, LaunchpadColors.OFF)
                time.sleep(0.1)
            self.current_menu = original_menu
            self.update_menu_display()
        threading.Thread(target=flash_sequence, daemon=True).start()
        logger.info("Flash lights activated")

    def celebration_mode(self):
        def celebration_sequence():
            colors = [LaunchpadColors.RED_FULL, LaunchpadColors.GREEN_FULL, 
                     LaunchpadColors.BLUE_FULL, LaunchpadColors.YELLOW_FULL]
            for _ in range(10):
                import random
                for pad in range(64):
                    self.set_pad_color(pad, random.choice(colors))
                time.sleep(0.2)
            self.update_menu_display()
        threading.Thread(target=celebration_sequence, daemon=True).start()
        logger.info("Celebration mode activated")

    def voting_mode(self):
        def voting_sequence():
            for _ in range(20):
                for pad in range(64):
                    self.set_pad_color(pad, LaunchpadColors.AMBER_FULL)
                time.sleep(0.5)
                for pad in range(64):
                    self.set_pad_color(pad, LaunchpadColors.AMBER_LOW)
                time.sleep(0.5)
            self.update_menu_display()
        threading.Thread(target=voting_sequence, daemon=True).start()
        logger.info("Voting mode activated")

    def technical_break(self):
        self.switch_obs_scene(self.config["scenes"]["backup"])
        self.stop_music()
        logger.info("Technical break activated")

    def emergency_stop(self):
        self.stop_music()
        self.switch_obs_scene(self.config["scenes"]["backup"])
        self.reset_launchpad_leds()
        self.update_menu_display()
        logger.warning("EMERGENCY STOP ACTIVATED")

    def reset_all(self):
        self.stop_music()
        self.switch_obs_scene(self.config["scenes"]["intro"])
        self.current_menu = MenuMode.SCENES
        self.update_menu_display()
        logger.info("System reset")

    def test_mode(self):
        logger.info("Test mode - cycling through all functions")

    def show_status(self):
        menu_names = ["SCENES", "MUSIC", "EFFECTS", "UTILITY"]
        status = f"Menu: {menu_names[self.current_menu]}, Scene: {self.current_scene}, Music: {self.current_music}"
        logger.info(f"Status: {status}")

    def handle_midi_message(self, message):
        if message.type == 'note_on' and message.velocity > 0:
            pad_number = message.note
            if pad_number in self.circular_buttons:
                self.switch_menu(self.circular_buttons[pad_number])
                return
            self.flash_pad(pad_number)
            if self.current_menu in self.menu_functions:
                if pad_number in self.menu_functions[self.current_menu]:
                    try:
                        self.menu_functions[self.current_menu][pad_number]()
                    except Exception as e:
                        logger.error(f"Error executing function for pad {pad_number}: {e}")
                else:
                    logger.info(f"Pad {pad_number} pressed - no function assigned in current menu")
            else:
                logger.info(f"Pad {pad_number} pressed - no menu active")

    def run(self):
        logger.info("Starting Eurovision Control Center...")
        if not self.initialize_launchpad():
            logger.error("Failed to initialize Launchpad")
            return
        if not self.initialize_obs():
            logger.error("Failed to initialize OBS connection")
            return
        self.running = True
        logger.info("Eurovision Control Center is running!")
        logger.info("Use circular buttons (1-4) to switch between menus:")
        logger.info("1: SCENES | 2: MUSIC | 3: EFFECTS | 4: UTILITY")
        logger.info("Press Ctrl+C to stop")
        try:
            for message in self.launchpad_input:
                if not self.running:
                    break
                self.handle_midi_message(message)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        self.running = False
        self.audio_monitoring = False
        if self.current_player:
            self.current_player.stop()
        if self.launchpad_input:
            self.launchpad_input.close()
        if self.launchpad_output:
            self.reset_launchpad_leds()
            self.launchpad_output.close()
        if self.obs_client:
            self.obs_client.disconnect()
        logger.info("Eurovision Control Center stopped")

def main():
    controller = EurovisionController()
    controller.run()

if __name__ == "__main__":
    main()