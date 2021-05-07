import sys
import pulsectl

class VolumeControl:
    def __init__( self ):
        self.pulse = pulsectl.Pulse( sys.argv[0] )

    def set_default_sink( self, sink_index ):
        self.pulse.sink_default_set( self.__get_sink_by_index( sink_index ))

    def move_inputs_to_sink( self, sink_index ):
        for input in self.pulse.sink_input_list():
            self.pulse.sink_input_move( input.index, sink_index )

    def set_volume( self, level, sink_index = None ):
        if sink_index == None:
            sink = self.__default_sink()
        else:
            sink = self.__get_sink_by_index( sink_index )
        self.pulse.volume_set_all_chans( sink, level )

    def __get_sink_by_index( self, index ):
        sink = None
        for sink in self.pulse.sink_list():
            if sink.index == index:
                break
        return sink

    def __default_sink( self ):
        return self.pulse.get_sink_by_name(
            self.pulse.server_info().default_sink_name
        )
