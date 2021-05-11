import logging

from volume_control import VolumeControl
from alias_resolver import AliasResolver

##
# Maps events
class Mapper:
    MAPPING = {
        "Throttle/Rotary3#change": "_sink0_volume_control",
        "Throttle/Rotary4#change": "_sink1_volume_control",
        "Throttle/ModeM1#press": "_sink0",
        "Throttle/ModeM2#press": "_sink1",
    }

    def __init__( self ):
        self.logger = logging.getLogger( __name__ )
        self.volume_control = VolumeControl()

    def map( self, event_details ):
        if AliasResolver.event_alias( event_details ) in self.MAPPING:
            getattr( self, self.MAPPING[AliasResolver.event_alias( event_details )])( event_details )

    def _sink0( self, event_details ):
        self.volume_control.set_default_sink( 0 )
        self.volume_control.move_inputs_to_sink( 0 )

    def _sink1( self, event_details ):
        self.volume_control.set_default_sink( 1 )
        self.volume_control.move_inputs_to_sink( 1 )

    def __volume_control( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ))

    def _sink0_volume_control( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ), sink_index = 0 )

    def _sink1_volume_control( self, event_details):
        (device, device_id, trigger_type, event_type, event_id, event_value) = event_details
        self.volume_control.set_volume( self.__normalize( event_value, -32768, 32767 ), sink_index = 1 )

    # Convert a value from a specified range to 0-1 range (float)
    @staticmethod
    def __normalize( value, from_min, from_max):
        return float( value - from_min ) / float( from_max - from_min )
