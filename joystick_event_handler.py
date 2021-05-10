import ctypes
import logging
from sdl2 import *

from volume_control import VolumeControl

class JoystickEventHandler:
    stop_thread = False
    logger = logging.getLogger( __name__ )

    MAPPINGS = {
        "sliders": {
            6: {
                "function": "_sink1_volume_control",
            },
            7: {
                "function": "_sink0_volume_control",
            },
        },
        "buttons": {
            33: {
                "press": {
                    "function": "_sink0",
                },
            },
            34: {
                "press": {
                    "function": "_sink1",
                },
            },
        }
    }

    @classmethod
    def run( cls, args ):
        cls.logger.info( 'Starting (%s).' % cls.__name__ )
        while not cls.stop_thread:
            try:
                event_handler = cls()
                while not cls.stop_thread:
                    try:
                        event_handler.update()
                    except:
                        cls.logger.exception( 'Exception caught in (%s)' % cls.__name__ )
            except:
                # Log the exception ang gracefully restart
                cls.logger.exception( 'Exception caught in (%s)' % cls.__name__ )


    def __init__( self ):
        SDL_Init( SDL_INIT_JOYSTICK )
        self.axis = {}
        self.button = {}
        self.volume_control = VolumeControl()

    def update( self ):
        event = SDL_Event()
        if SDL_WaitEventTimeout( ctypes.byref( event ), 175 ) == 1:
            event_details = self._classify_event( event )
            self._log_event( event_details )

            (device, device_id, event_type, event_id, event_value) = event_details

            # Joystick events only for now :(
            if device != 'Joystick':
                raise NotImplementedError( 'Unsupported device.' % event.type )

            if event.type == SDL_JOYDEVICEADDED:
                SDL_JoystickOpen( event.jdevice.which )

            elif event.type == SDL_JOYAXISMOTION:
                self.axis[event_id] = event_value
                if event_id in self.MAPPINGS["sliders"]:
                    getattr( self, self.MAPPINGS["sliders"][event_id]["function"] )( event_value )
            elif event.type == SDL_JOYBUTTONDOWN:
                self.button[event_id] = True
                if event_id in self.MAPPINGS["buttons"]:
                    if "press" in self.MAPPINGS["buttons"][event_id]:
                        getattr( self, self.MAPPINGS["buttons"][event_id]["press"]["function"] )()

            elif event.type == SDL_JOYBUTTONUP:
                self.button[event.jbutton.button] = False

    def _classify_event( self, event ):
        if 0x300 <= event.type < 0x400:
            device = 'Keyboard'
            device_id = None
        elif 0x400 <= event.type < 0x600:
            device = 'Mouse'
            device_id = None
        elif 0x600 <= event.type < 0x650:
            device = 'Joystick'
            device_id = event.jdevice.which
        elif 0x650 <= event.type < 0x700:
            device = 'Controller'
            device_id = None
        elif 0x700 <= event.type < 0x800:
            device = 'Touchpad'
            device_id = None

        if event.type == SDL_JOYAXISMOTION:
            event_type = 'Slider'
            event_id = event.jaxis.axis
            event_value = event.jaxis.value
        elif event.type == SDL_JOYBUTTONDOWN:
            event_type = 'Button'
            event_id = event.jbutton.button
            event_value = True
        elif event.type == SDL_JOYBUTTONUP:
            event_type = 'Button'
            event_id = event.jbutton.button
            event_value = False
        elif event.type == SDL_JOYHATMOTION:
            event_type = 'HAT'
            event_id = event.jhat.hat
            event_value = {
                SDL_HAT_CENTERED: 0,
                SDL_HAT_UP: 1,
                SDL_HAT_RIGHTUP: 5,
                SDL_HAT_RIGHT: 9,
                SDL_HAT_RIGHTDOWN: 13,
                SDL_HAT_DOWN: 17,
                SDL_HAT_LEFTDOWN: 21,
                SDL_HAT_LEFT: 25,
                SDL_HAT_LEFTUP: 29,
            }[event.jhat.value]
        elif event.type == SDL_JOYDEVICEADDED:
            event_type = 'Connected'
            event_id = None
            event_value = None
        else:
            event_type = '[%s]' % hex(event.type)
            event_id = None
            event_value = None

        return (device, device_id, event_type, event_id, event_value)

    def _log_event( self, event_values ):
        (device, device_id, event_type, event_id, event_value) = event_values

        if event_id != None:
            if event_value != None:
                self.logger.debug( "%s%s/%s%s = %s" % (device, device_id, event_type, event_id, event_value))
            else:
                self.logger.debug( "%s%s/%s%s" % (device, device_id, event_type, event_id))
        else:
            self.logger.debug( "%s%s/%s" % (device, device_id, event_type))

    def _sink0( self ):
        self.volume_control.set_default_sink( 0 )
        self.volume_control.move_inputs_to_sink( 0 )

    def _sink1( self ):
        self.volume_control.set_default_sink( 1 )
        self.volume_control.move_inputs_to_sink( 1 )

    def _volume_control( self, value ):
        self.volume_control.set_volume( self.__normalize( value, -32768, 32767 ))

    def _sink0_volume_control( self, value ):
        self.volume_control.set_volume( self.__normalize( value, -32768, 32767 ), sink_index = 0 )

    def _sink1_volume_control( self, value ):
        self.volume_control.set_volume( self.__normalize( value, -32768, 32767 ), sink_index = 1 )

    # Convert the left range into a 0-1 range (float)
    @staticmethod
    def __normalize( value, from_min, from_max):
        return float( value - from_min ) / float( from_max - from_min )
