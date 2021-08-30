import logging
import subprocess

from volume_control import VolumeControl
from alias_resolver import AliasResolver

##
# Maps events
class Mapper:
    # SINK_HEADPHONES = 'alsa_output.usb-Razer_Razer_Kraken_Tournament_Edition_000000000000000000000000-00.analog-stereo'
    SINK_HEADPHONES = 'alsa_output.usb-Razer_Razer_Kraken_Tournament_Edition_000000000000000000000000-00.stereo-chat'
    SINK_SPEAKERS = 'alsa_output.pci-0000_0b_00.4.analog-stereo'
    INPUT_CARDS = [
        'alsa_card.usb-Razer_Razer_Kraken_Tournament_Edition_000000000000000000000000-00',
    ]
    MAPPING = {
        "Throttle/Rotary3#change": "_sink_speakers_volume",
        "Throttle/Rotary4#change": "_sink_headphones_volume",
        "Throttle/ModeM1#press": "_sink_headphones",
        "Throttle/ModeM2#press": "_sink_speakers",
        "Throttle/ModeS1#press": "_mute_microphones",
        "Throttle/F#press": "_terminal_open",
        "Throttle/G#press": "_terminal_close",
        "Throttle/SW1#release": "_close_slack",
        "Throttle/SW2#release": "_focus_slack",
        "Throttle/SW3#release": "_close_gitkraken",
        "Throttle/SW4#release": "_focus_gitkraken",
        "Throttle/SW5#press": "_lollypop_toggle",
        "Throttle/SW6#press": "_lollypop_play",
        "Throttle/TGL4Up#press": "_lock_pc",
        "Throttle/TGL4Down#press": "_lock_pc",
        "Throttle/H3Right#press": "_next_song",
        "Throttle/H3Left#press": "_prev_song",
    }

    def __init__( self ):
        self.logger = logging.getLogger( __name__ )
        self.volume_control = VolumeControl()

    def map( self, event_details ):
        if AliasResolver.event_alias( event_details ) in self.MAPPING:
            getattr( self, self.MAPPING[AliasResolver.event_alias( event_details )])( event_details )

    def _sink_headphones( self, event_details ):
        self.volume_control.set_default_sink( self.SINK_HEADPHONES )
        self.volume_control.move_inputs_to_sink( self.SINK_HEADPHONES )

    def _sink_speakers( self, event_details ):
        self.volume_control.set_default_sink( self.SINK_SPEAKERS )
        self.volume_control.move_inputs_to_sink( self.SINK_SPEAKERS )

    def __volume_control( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ))

    def _sink_headphones_volume( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ), sink = self.SINK_HEADPHONES )

    def _sink_speakers_volume( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ), sink = self.SINK_SPEAKERS )

    def _lock_pc( self, event_details ):
        subprocess.Popen(['xdg-screensaver', 'lock'] )


    def _mute_microphones( self, event_details):
	    pass

    def _lollypop_play( self, event_details):
        subprocess.Popen(['lollypop'] )

    def _lollypop_toggle( self, event_details):
        subprocess.Popen(['lollypop', '--play-pause'] )

    def _terminal_open( self, event_details ):
        subprocess.Popen(['gnome-terminal'] )

    def _terminal_close( self, event_details ):
        subprocess.Popen(['xdotool', 'key', 'Control_L+d'] )

    def _close_slack( self, event_details ):
        subprocess.Popen(['wmctrl', '-c', 'Slack'])

    def _focus_slack( self, event_details ):
        subprocess.Popen(['slack'])

    def _close_gitkraken( self, event_details ):
        subprocess.Popen(['wmctrl', '-c', 'GitKraken'])

    def _focus_gitkraken( self, event_details ):
        subprocess.Popen(['gitkraken'])
        subprocess.Popen(['wmctrl', '-R', 'GitKraken'])

    def _next_song( self, event_details ):
        subprocess.Popen(['lollypop', '--next'])

    def _prev_song( self, event_details ):
        subprocess.Popen(['lollypop', '--prev'])

    # Convert a value from a specified range to 0-1 range (float)
    @staticmethod
    def __normalize( value, from_min, from_max):
        return float( value - from_min ) / float( from_max - from_min )
