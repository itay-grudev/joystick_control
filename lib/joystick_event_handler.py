import sys
import ctypes
import logging
import statistics
from sdl2 import *

from user.mapper import Mapper
from lib.alias_resolver import AliasResolver


class JoystickEventHandler:
    stop_thread = False
    logger = logging.getLogger(__name__)

    @classmethod
    def run(cls, args):
        cls.logger.info('Starting (%s).' % cls.__name__)
        while not cls.stop_thread:
            try:
                event_handler = cls()
                while not cls.stop_thread:
                    try:
                        event_handler.update()
                    except:
                        cls.logger.exception(
                            'Exception caught in (%s)' % cls.__name__)
            except:
                # Log the exception ang gracefully restart
                cls.logger.exception('Exception caught in (%s)' % cls.__name__)

    def __init__(self):
        SDL_Init(SDL_INIT_JOYSTICK)
        self.mapper = Mapper()
        self.filter_memory = {}

    def update(self):
        event = SDL_Event()
        if SDL_WaitEventTimeout(ctypes.byref(event), 175) == 1:
            (drop_event, *event_details) = self._classify_event(event)
            self._log_event(drop_event, event_details)

            if drop_event:
                return

            if event.type != SDL_JOYDEVICEADDED:
                self.mapper.map(event_details)

    def _classify_event(self, event):
        drop_event = False

        if 0x300 <= event.type < 0x400:
            device = 'Keyboard'
            vendor_id = None
            product_id = None
            device_type = None
        elif 0x400 <= event.type < 0x600:
            device = 'Mouse'
            vendor_id = None
            product_id = None
            device_type = None
        elif 0x600 <= event.type < 0x650:
            device_handler = SDL_JoystickOpen(event.jdevice.which)
            device = 'Joystick'
            vendor_id = "%04x" % joystick.SDL_JoystickGetDeviceVendor(
                event.jdevice.which)
            product_id = "%04x" % joystick.SDL_JoystickGetDeviceProduct(
                event.jdevice.which)
            device_type = [
                'Unknown',
                'Gamecontroller',
                'Wheel',
                'Arcade_stick',
                'Flight_stick',
                'Dance_pad',
                'Guitar',
                'Drum_kit',
                'Arcade_pad',
                'Throttle',
            ][joystick.SDL_JoystickGetType(device_handler)]
        elif 0x650 <= event.type < 0x700:
            device = 'Controller'
            vendor_id = None
            product_id = None
            device_type = None
        elif 0x700 <= event.type < 0x800:
            device = 'Touchpad'
            vendor_id = None
            product_id = None
            device_type = None

        if event.type == SDL_JOYAXISMOTION:
            trigger_type = 'Slider'
            event_type = 'change'
            event_id = event.jaxis.axis
            event_value = event.jaxis.value
            # Anti-jitter filter
            prev_values = (
                self.filter_memory
                .setdefault(vendor_id, {})
                .setdefault(product_id, {})
                .setdefault(event.jaxis.axis, [])
            )
            if len(prev_values) > 1:  # You cannot calculate stddev on less than 2 values
                # Check if the moving average of the last val
                avg = sum(prev_values) / len(prev_values)
                if abs(avg - event_value) - statistics.stdev(prev_values) * 1.5 < 0:
                    drop_event = True
            prev_values.append(event_value)
            if len(prev_values) > 10:
                prev_values.pop(0)
        elif event.type == SDL_JOYBUTTONDOWN:
            trigger_type = 'Button'
            event_type = 'press'
            event_id = event.jbutton.button
            event_value = None
        elif event.type == SDL_JOYBUTTONUP:
            trigger_type = 'Button'
            event_type = 'release'
            event_id = event.jbutton.button
            event_value = None
        elif event.type == SDL_JOYHATMOTION:
            trigger_type = 'HAT'
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
            if event_value:
                event_type = 'press'
            else:
                event_type = 'release'
        elif event.type == SDL_JOYDEVICEADDED:
            trigger_type = 'Connected'
            event_type = None
            event_id = None
            event_value = None
        else:
            trigger_type = '[%s]' % hex(event.type)
            event_type = None
            event_id = None
            event_value = None

        return (drop_event, device, device_type, vendor_id, product_id, trigger_type, event_type, event_id, event_value)

    def _log_event(self, drop_event, event_details):
        (device, device_type, vendor_id, product_id, trigger_type,
         event_type, event_id, event_value) = event_details

        prefix = ''
        if drop_event:
            prefix = '[DROPPED] '

        if event_id != None:
            if event_value != None:
                self.logger.debug('%s%s = %s' % (
                        prefix,
                        AliasResolver.event_alias(event_details),
                        event_value
                    )
                )
            else:
                self.logger.debug(
                    '%s%s' % (
                        prefix,
                        AliasResolver.event_alias(event_details)
                    )
                )
        else:
            self.logger.debug(
                '%s%s/%s' % (
                    prefix,
                    AliasResolver.device_name_alias(event_details),
                    trigger_type
                )
            )
