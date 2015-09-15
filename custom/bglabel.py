from kivy.uix.label import Label
from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior

class BGLabel(Label):
    bgcolour = ListProperty([0,0,0,0])

    def __init__(self, **kwargs):
        super(BGLabel, self).__init__(**kwargs)

class BGLabelButton(ButtonBehavior, BGLabel):
    pass
