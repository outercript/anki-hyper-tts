import constants
import voice

"""
the various objects here dictate how HyperTTS is configured and these objects will serialize to/from the anki config
"""

class BatchConfig():
    def __init__(self, mode: constants.BatchMode):
        self.mode = mode
        self._source = None
        self._target = None
        self._voice_selection = None

    def get_source(self):
        return self._source
    def set_source(self, source):
        self._source = source

    def get_target(self):
        return self._target
    def set_target(self, target):
        self._target = target

    def get_voice_selection(self):
        return self._voice_selection
    def set_voice_selection(self, voice_selection):
        self._voice_selection = voice_selection

    source = property(get_source, set_source)
    target = property(get_target, set_target)
    voice_selection = property(get_voice_selection, set_voice_selection)

    def serialize(self):
        return {
            'mode': self.mode.name,
            'source': self.source.serialize(),
            'target': self.target.serialize(),
            'voice_selection': self.voice_selection.serialize()
        }

class BatchSourceSimple():
    def __init__(self, source_field):
        self.source_field = source_field

    def serialize(self):
        return {
            'source_field': self.source_field
        }

class BatchSourceTemplate():
    def __init__(self, source_template: str, template_format_version: constants.TemplateFormatVersion):
        self.source_template = source_template
        self.template_format_version = template_format_version

    def serialize(self):
        return {
            'template_format_version': self.template_format_version.name,
            'source_template': self.source_template
        }

class BatchTarget():
    def __init__(self, target_field, text_and_sound_tag, remove_sound_tag):
        self.target_field = target_field
        self.text_and_sound_tag = text_and_sound_tag
        self.remove_sound_tag = remove_sound_tag

    def serialize(self):
        return {
            'target_field': self.target_field,
            'text_and_sound_tag': self.text_and_sound_tag,
            'remove_sound_tag': self.remove_sound_tag
        }


# voice selection models
# ======================

class VoiceWithOptions():
    def __init__(self, voice: voice.VoiceBase, options):
        self.voice = voice
        self.options = options

    def serialize(self):
        return {
            'voice': self.voice.serialize(),
            'options': self.options
        }

    def options_str(self):
        options_array = []
        for key, value in self.options.items():
            if value != self.voice.options[key]['default']:
                options_array.append(f'{key}: {value}')
        if len(options_array) > 0:
            return ' (' + ', '.join(options_array) + ')'
        return ''


    def __str__(self):
        return f'{self.voice}{self.options_str()}'

class VoiceWithOptionsRandom(VoiceWithOptions):
    def __init__(self, voice: voice.VoiceBase, options, random_weight=1):
        VoiceWithOptions.__init__(self, voice, options)
        self._random_weight = random_weight

    def serialize(self):
        return {
            'voice': self.voice.serialize(),
            'options': self.options,
            'weight': self.random_weight
        }        

    def get_random_weight(self):
        return self._random_weight

    def set_random_weight(self, weight):
        self._random_weight = weight

    random_weight = property(get_random_weight, set_random_weight)

class VoiceWithOptionsPriority(VoiceWithOptions):
    def __init__(self, voice: voice.VoiceBase, options):
        VoiceWithOptions.__init__(self, voice, options)


class VoiceSelectionBase():
    def __init__(self):
        self._selection_mode = None

    def get_selection_mode(self):
        return self._selection_mode

    # properties
    selection_mode = property(get_selection_mode, None)

class VoiceSelectionSingle(VoiceSelectionBase):
    def __init__(self):
        VoiceSelectionBase.__init__(self)
        self._selection_mode = constants.VoiceSelectionMode.single
        self._voice_with_options = None
    
    def serialize(self):
        return {
            'voice_selection_mode': self._selection_mode.name,
            'voice': self._voice_with_options.serialize()
        }

    def get_voice(self):
        return self._voice_with_options
    def set_voice(self, voice_with_options):
        self._voice_with_options = voice_with_options

    voice = property(get_voice, set_voice)

class VoiceSelectionMultipleBase(VoiceSelectionBase):
    def __init__(self):
        VoiceSelectionBase.__init__(self)
        self._voice_list = []

    def get_voice_list(self):
        return self._voice_list

    def clear_voice_list(self):
        self._voice_list = []

    def add_voice(self, voice):
        self._voice_list.append(voice)

    def remove_voice(self, voice):
        self._voice_list.remove(voice)

    def move_up_voice(self, voice):
        index = self._voice_list.index(voice)
        if index == 0:
            return
        entry_1 = self._voice_list[index - 1]
        entry_2 = self._voice_list[index]
        self._voice_list[index - 1] = entry_2
        self._voice_list[index] = entry_1

    def move_down_voice(self, voice):
        index = self._voice_list.index(voice)
        if index == len(self._voice_list) - 1:
            return
        entry_1 = self._voice_list[index]
        entry_2 = self._voice_list[index + 1]
        self._voice_list[index] = entry_2
        self._voice_list[index + 1] = entry_1

    voice_list = property(get_voice_list, None)

    def serialize(self):
        return {
            'voice_selection_mode': self._selection_mode.name,
            'voice_list': [x.serialize() for x in self._voice_list]
        }

class VoiceSelectionRandom(VoiceSelectionMultipleBase):
    def __init__(self):
        VoiceSelectionMultipleBase.__init__(self)
        self._selection_mode = constants.VoiceSelectionMode.random

    def set_random_weight(self, voice_index, weight):
        self._voice_list[voice_index].random_weight = weight

class VoiceSelectionPriority(VoiceSelectionMultipleBase):
    def __init__(self):
        VoiceSelectionMultipleBase.__init__(self)
        self._selection_mode = constants.VoiceSelectionMode.priority

