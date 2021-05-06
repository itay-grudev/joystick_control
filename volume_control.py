import sys
import pulsectl

class VolumeControl:
    def __init__( self ):
        self.pulse = pulsectl.Pulse( sys.argv[0] )

    def set_default_sink( self, index ):
        pass

    def move_inputs_to_sink( self, index ):
        pass

    def set_volume( self, level ):
        self.pulse.volume_set_all_chans( self.__default_sync(), level )

    def __get_sink_by_index( self, index ):
        sink = None
        for sink in self.pulse.sink_list():
            if sink.index == index:
                break
        return sink

    def __default_sync( self ):
        sink = None
        for sink in self.pulse.sink_list():
            if sink.name == self.pulse.server_info().default_sink_name:
                break
        return sink
