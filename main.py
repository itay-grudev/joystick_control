#!/usr/bin/env python3

import sys
import signal
import logging
import threading

from joystick_event_handler import JoystickEventHandler

class Main:
    def run( self ):
        # Initialize logging
        self.logger = logging.getLogger( __name__ )
        self.logger.info( 'Initialising' )

        # Install an exception handler to make sure all exceptions are logged
        sys.excepthook = self.exception_handler

        self.programs = [
            JoystickEventHandler,
        ]

        self.threads = []

        for program in self.programs:
            thread = threading.Thread( target = program.run )
            thread.start()
            self.threads.append( [ program, thread ] )
            self.logger.info( 'Loaded %s' % program.__name__ )

        # Wait for all the program threads to join
        for thread in self.threads:
            while thread[1].is_alive():
                signal.pause()

        self.logger.info( 'Main program clean exit.' )

    def interrupt_handler( self, signal, frame ):
        self.logger.info( 'Shutting down.' )
        for thread in self.threads:
            thread[0].stop_thread = True
            thread[1].join()

    def exception_handler( self, excType, excValue, traceback ):
        self.logger.error( 'Uncaught exception', exc_info = (
            excType,
            excValue,
            traceback
        ))
        self.logger.info( 'Aborting.' )
        sys.exit( 1 )

    def __init__( self ):
        logging.basicConfig( stream=sys.stdout, level=logging.DEBUG )

        signal.signal( signal.SIGHUP, self.interrupt_handler )
        signal.signal( signal.SIGINT, self.interrupt_handler )

        self.run()

if __name__ == "__main__":
    Main()
