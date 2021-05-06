import os
import ctypes
import logging
from sdl2 import *

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
        }
    }

    @classmethod
    def run( cls ):
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
                elif event.type == SDL_JOYBUTTONUP:
                    self.button[event.jbutton.button] = False

    def _volume_control( self, event ):
        os.system( f"amixer -D pulse set Master {self.__translate( event.value, -32768, 32767, 0, 100 )}% 2>&1 1>/dev/null" )

    @staticmethod
    def __translate( value, from_min, from_max, to_min, to_max):
        # Figure out how 'wide' each range is
        left_span = from_max - from_min
        right_span = to_max - to_min

        # Convert the left range into a 0-1 range (float)
        scaled_value = float( value - from_min ) / float( left_span )

        # Convert the 0-1 range into a value in the right range.
        return to_min + scaled_value * right_span
