from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import hashlib

def callback(*args):
    hasher = hashlib.sha512()
    btn = args[0]
    myLabel = btn.parent.children[0]
    myTxtIn = btn.parent.children[2]
    myText = myTxtIn.text.encode('utf-8')
    hasher.update(myText)
    myLabel.text = str(hasher.digest())

class RootWidget(Widget):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.size = (400,400)
        l = BoxLayout(size=self.size)
        t = TextInput(size=self.size)
        b = Button()
        b.bind(on_release=callback)
        result = Label(id='result')
        l.add_widget(t)
        l.add_widget(b)
        l.add_widget(result)
        self.add_widget(l)

class ScratchApp(App):
    def build(self):
        return RootWidget()

if __name__ == '__main__':
    ScratchApp().run()