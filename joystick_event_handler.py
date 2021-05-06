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
                "min": -32768,
                "max": 32767,
                "function": "_volume_control",
            }
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
                if event.type == SDL_JOYDEVICEADDED:
                    self.device = SDL_JoystickOpen( event.jdevice.which )
                elif event.type == SDL_JOYAXISMOTION:
                    self.axis[event.jaxis.axis] = event.jaxis.value
                    if event.jaxis.axis in self.MAPPINGS["sliders"]:
                        getattr( self, self.MAPPINGS["sliders"][event.jaxis.axis]["function"] )( event.jaxis )
                elif event.type == SDL_JOYBUTTONDOWN:
                    self.button[event.jbutton.button] = True
                    if event.jbutton.button in self.MAPPINGS["buttons"]:
                        if "press" in self.MAPPINGS["buttons"][event.jbutton.button]:
                            getattr( self, self.MAPPINGS["buttons"][event.jbutton.button]["press"]["function"] )()
                elif event.type == SDL_JOYBUTTONUP:
                    self.button[event.jbutton.button] = False

                if self.logger.level <= logging.DEBUG:
                    self.logger.debug( "axis: " + str( self.axis ))
                    self.logger.debug( "button: " + str( self.button ))

    def _sink0( self ):
        self.volume_control.set_default_sink( 0 )
        self.volume_control.move_inputs_to_sink( 0 )

    def _sink1( self ):
        self.volume_control.set_default_sink( 1 )
        self.volume_control.move_inputs_to_sink( 1 )

    def _volume_control( self, event ):
        self.volume_control.set_volume( self.__normalize( event.value, -32768, 32767 ))

    # Convert the left range into a 0-1 range (float)
    @staticmethod
    def __normalize( value, from_min, from_max):
        return float( value - from_min ) / float( from_max - from_min )
