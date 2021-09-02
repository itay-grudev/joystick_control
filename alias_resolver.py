import os
import yaml
import logging

class AliasResolver:
    ALIAS_CONFIG = {}
    logger = logging.getLogger( __name__ )

    @classmethod
    def event_alias( cls, event_details ):
        (device, device_type, vendor_id, product_id, trigger_type, event_type, event_id, event_value) = event_details

        if event_type:
            return '%s/%s#%s' % (cls.device_name_alias( event_details ), cls.event_name_alias( event_details ), event_type)
        else:
            return '%s/%s#%s' % (cls.device_name_alias( event_details ), cls.event_name_alias( event_details ), event_type)

    @classmethod
    def device_name_alias( cls, event_details ):
        (device, device_type, vendor_id, product_id, trigger_type, event_type, event_id, event_value) = event_details

        cls._load_vendor_yaml( vendor_id )

        try:
            return cls.ALIAS_CONFIG[vendor_id]['%ss' % device ]['%s-%s' % (device_type, product_id) ]['name']
        except (KeyError, TypeError):
            return '%s/%s-%s' % (vendor_id, device_type, product_id)

        return cls.ALIAS_CONFIG[vendor_id]['%ss' % device ]['%s-%s' % (device_type, product_id) ]['name']

    @classmethod
    def event_name_alias( cls, event_details ):
        (device, device_type, vendor_id, product_id, trigger_type, event_type, event_id, event_value) = event_details

        cls._load_vendor_yaml( vendor_id )

        try:
            return cls.ALIAS_CONFIG[vendor_id]['%ss' % device ]['%s-%s' % (device_type, product_id) ][ '%ss' % trigger_type.lower() ][event_id]
        except (KeyError, TypeError):
            return '%ss/%s' % (trigger_type.lower(), event_id)

    @classmethod
    def _load_vendor_yaml( cls, vendor_id ):
        try:
            if cls.ALIAS_CONFIG[vendor_id] == None: return
        except (KeyError):
            try:
                cls.ALIAS_CONFIG[vendor_id] = yaml.safe_load(
                    open( os.path.dirname(os.path.realpath(__file__)) + '/conf/%s.yml' % vendor_id, 'r' )
                )
            except (FileNotFoundError):
                if vendor_id not in cls.ALIAS_CONFIG:
                    cls.ALIAS_CONFIG[vendor_id] = None
                    cls.logger.error( 'Failed to load alias configuration for vendor id: %s' % vendor_id )
