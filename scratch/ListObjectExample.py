from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.listview import ListItemButton, ListView
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

class ListVariables():
    def __init__(self, data):
        self.lvData = data
        self.argsConverter = lambda row_index, obj: {'text': obj.text,
                                                'size_hint_y': None,
                                                'height': 25}
        self.lvAdapter = ListAdapter(data=self.lvData,
                                     args_converter=self.argsConverter,
                                     propagate_selection_to_data=True,
                                     cls=ListItemButton)
        self.listView = ListView(adapter=self.lvAdapter)

class DataItem():
    def __init__(self, string):
        self.text = string
        self.is_selected = False

someData = [DataItem('Cat'),DataItem('Dog'),DataItem('Horse')]

class RootScreen(Screen):
    myList = ListVariables(someData)
    myAdapter = ObjectProperty(myList.lvAdapter)
    '''def __init__(self,listView, **kwargs):
        super(RootScreen, self).__init__(**kwargs)
        self.list_view = listView
        self.add_widget(self.list_view)'''


class ListObjectApp(App):
    def build(self):
        #return RootScreen()
        self.myList = ListVariables(someData)
        return RootScreen()

if __name__ == '__main__':
    ListObjectApp().run()