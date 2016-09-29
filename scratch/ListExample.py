from kivy.uix.listview import ListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class MainView(BoxLayout):
    '''Implementation of a simple list view with 100 items.
    '''

    def __init__(self, **kwargs):
        #kwargs['cols'] = 2
        super(MainView, self).__init__(**kwargs)

        self.orientation = 'vertical'
        myLabel = Label(text='Hello!')
        myButton = Button(text='Whats up?')
        list_view = ListView(item_strings=[str(index) for index in range(100)])

        myListView = self.defineListView()

        self.add_widget(myLabel)
        self.add_widget(list_view)
        self.add_widget(myButton)




if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(MainView(width=800))