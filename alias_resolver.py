import os
import yaml

class AliasResolver:
    ALIAS_CONFIG = yaml.safe_load(
        open( os.path.dirname(os.path.realpath(__file__)) + '/conf/joystick_aliases.yaml', 'r' )
    )

    @classmethod
    def event_alias( cls, event_details ):
        (device, device_type, device_id, trigger_type, event_type, event_id, event_value) = event_details

        if event_type:
            return '%s/%s#%s' % (cls.device_name_alias( event_details ), cls.event_name_alias( event_details ), event_type)
        else:
            return '%s/%s#%s' % (cls.device_name_alias( event_details ), cls.event_name_alias( event_details ), event_type)

    @classmethod
    def device_name_alias( cls, event_details ):
        (device, device_type, device_id, trigger_type, event_type, event_id, event_value) = event_details

        return cls.ALIAS_CONFIG['%ss' % device ]['%s-%s' % (device_type, device_id) ]['name']

    @classmethod
    def event_name_alias( cls, event_details ):
        (device, device_type, device_id, trigger_type, event_type, event_id, event_value) = event_details
        try:
            return cls.ALIAS_CONFIG['%ss' % device ]['%s-%s' % (device_type, device_id) ][ '%ss' % trigger_type.lower() ][event_id]
        except (KeyError, TypeError):
            return '%s%s' % (trigger_type, event_id)
