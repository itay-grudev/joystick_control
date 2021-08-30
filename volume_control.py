import sys
import pulsectl

class VolumeControl:
    def __init__( self ):
        self.pulse = pulsectl.Pulse( sys.argv[0] )

    def set_default_sink( self, sink ):
        self.pulse.sink_default_set( self.__get_sink( sink ))

    def move_inputs_to_sink( self, sink ):
        # If one sink move fails - don't fail the entire operation
        # but raise the exception afterwards to assist in debugging
        exception = None
        for input in self.pulse.sink_input_list():
            try:
                self.pulse.sink_input_move( input.index, self.__get_sink( sink ).index)
            except pulsectl.pulsectl.PulseOperationFailed as e:
                exception = e
        if exception:
            raise exception

    def set_volume( self, level, sink = None ):
        if sink == None:
            sink = self.__default_sink()
        else:
            sink = self.__get_sink( sink )
        self.pulse.volume_set_all_chans( sink, level )

    def _mute_microphones( self ):
        for card in self.pulse.source_list():
            pass

    def __get_sink( self, sink ):
        if type( sink ) is int:
            return self.__get_sink_by_index( sink )
        elif type( sink ) is str:
            return self.__get_sink_by_name( sink )

    def __get_sink_by_index( self, index ):
        sink = None
        for sink in self.pulse.sink_list():
            if sink.index == index:
                break
        return sink

    def __get_sink_by_name( self, sink_name ):
        return self.pulse.get_sink_by_name( sink_name )

    def __get_card_by_name( self, sink_name ):
        return self.pulse.get_sink_by_name( sink_name )

    def __default_sink( self ):
        return self.pulse.get_sink_by_name(
            self.pulse.server_info().default_sink_name
        )
