import logging
import subprocess

from lib.linux.volume_control import VolumeControl
from lib.alias_resolver import AliasResolver

##
# Maps events


class Mapper:
    OUTPUT_SINKS = [
        'alsa_output.pci-0000_09_00.1.hdmi-stereo',
        'alsa_output.usb-Razer_Razer_Kraken_Tournament_Edition_000000000000000000000000-00.stereo-chat',
        'alsa_output.usb-0b0e_Jabra_Link_380_50C2ED7D7D89-00.analog-stereo',
    ]
    MAPPING = {
        "Throttle/Rotary4#change": "_volume_control",
        "Throttle/ModeM1#press":   "_sink_0",
        "Throttle/ModeM2#press":   "_sink_1",
        "Throttle/ModeS1#press":   "_sink_2",
        "Throttle/F#press":        "_terminal_open",
        "Throttle/G#press":        "_terminal_close",
        "Throttle/SW1#release":    "_close_slack",
        "Throttle/SW2#release":    "_focus_slack",
        "Throttle/SW3#release":    "_close_gitkraken",
        "Throttle/SW4#release":    "_focus_gitkraken",
        "Throttle/TGL4Up#press":   "_lock_pc",
        "Throttle/TGL4Down#press": "_lock_pc",
        "Throttle/SLD#press":      "_lollypop_open",
        "Throttle/SLD#release":    "_lollypop_close",
        "Throttle/E#press":        "_lollypop_toggle",
        "Throttle/H3Right#press":  "_next_song",
        "Throttle/H3Left#press":   "_prev_song",
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.volume_control = VolumeControl()

    def map(self, event_details):
        if AliasResolver.event_alias(event_details) in self.MAPPING:
            getattr(self, self.MAPPING[AliasResolver.event_alias(event_details)])(
                event_details)

    def _sink_0(self, event_details):
        sink = self.OUTPUT_SINKS[0]
        self.volume_control.set_default_sink(sink)
        self.volume_control.move_inputs_to_sink(sink)

    def _sink_1(self, event_details):
        sink = self.OUTPUT_SINKS[1]
        self.volume_control.set_default_sink(sink)
        self.volume_control.move_inputs_to_sink(sink)

    def _sink_2(self, event_details):
        sink = self.OUTPUT_SINKS[2]
        self.volume_control.set_default_sink(sink)
        self.volume_control.move_inputs_to_sink(sink)

    def _volume_control(self, event_details):
        (device, device_type, vendor_id, product_id, trigger_type,
         event_type, event_id, event_value) = event_details
        self.volume_control.set_volume(
            self.__normalize(event_value, -32768, 32767))

    def _lock_pc(self, event_details):
        subprocess.Popen(['xdg-screensaver', 'lock'])

    def _mute_microphones(self, event_details):
        pass

    def _lollypop_open(self, event_details):
        subprocess.Popen(['lollypop'])

    def _lollypop_close(self, event_details):
        subprocess.Popen(['wmctrl', '-c', 'Lollypop'])

    def _lollypop_toggle(self, event_details):
        subprocess.Popen(['lollypop', '--play-pause'])

    def _terminal_open(self, event_details):
        subprocess.Popen(['gnome-terminal'])

    def _terminal_close(self, event_details):
        subprocess.Popen(['xdotool', 'key', 'Control_L+d'])

    def _close_slack(self, event_details):
        subprocess.Popen(['wmctrl', '-c', 'Slack'])

    def _focus_slack(self, event_details):
        subprocess.Popen(['slack'])

    def _close_gitkraken(self, event_details):
        subprocess.Popen(['wmctrl', '-c', 'GitKraken'])

    def _focus_gitkraken(self, event_details):
        subprocess.Popen(['gitkraken'])
        subprocess.Popen(['wmctrl', '-R', 'GitKraken'])

    def _next_song(self, event_details):
        subprocess.Popen(['lollypop', '--next'])

    def _prev_song(self, event_details):
        subprocess.Popen(['lollypop', '--prev'])

    # Convert a value from a specified range to 0-1 range (float)
    @staticmethod
    def __normalize(value, from_min, from_max):
        return float(value - from_min) / float(from_max - from_min)
