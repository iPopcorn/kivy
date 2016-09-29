from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListView, ListItemButton, CompositeListItem, ListItemLabel
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.adapters.models import SelectableDataItem
from kivy.uix.label import Label
from kivy.factory import Factory

import sqlite3

testTuple = (1, 1, 1, 1, 0, None, 1, 'Competitive', None, None, 'PC')

class BackToJoinPartyFormButton(Button):
    pass

class PartyButton(ListItemButton):
    def myCallback(self):
        print("I would like to add some join party logic here")

class Party(SelectableDataItem):
    groupID = 0
    gameID = 0
    curSize = 0
    creatorID = 0
    #todo: add expiration times
    #expireTime = 0
    type = ""
    console = ""
    dbFile = ""
    gameName = ""
    #todo: get game name from game id
    def __init__(self,tuple, **kwargs):
        super(Party, self).__init__(**kwargs)
        #todo: get db file from root
        self.dbFile = "temp.db"
        self.groupID = tuple[0]
        self.gameID = tuple[2]
        self.curSize = tuple[3]
        self.creatorID = tuple[4]
        self.type = tuple[7]
        self.console = tuple[10]

        self.getGameNameFromID()
        self.printParty()

    def printParty(self):
        print("Group ID: %d\nGame ID: %d\nCurrent Size: %d\nCreator ID: %d\nType: %s\nConsole: %s\n"%(self.groupID,self.gameID,self.curSize,self.creatorID,self.type,self.console))

    def getGameNameFromID(self):
        #connect to or create db file
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT name
        FROM Game
        WHERE game_id=?
        ''',(self.gameID,))

        result = cursor.fetchone()
        if(result):
            self.gameName = result[0]
        else:
            print("No game found with that id")

class ListVariables():
    def __init__(self, data):
        self.lvData = data
        self.myConverter = lambda row_index, obj: {
            'text': obj.gameName,
            'size_hint_y': None,
            'height': 25,
            'cls_dicts':[{'cls': PartyButton,
                         'kwargs':{'text': obj.gameName,
                                   'is_representing_cls': True}},
                         {'cls': ListItemLabel, #needs keys 'curSize','type','console'
                          'kwargs':{'text': "Number of Members: " + str(obj.curSize)}},
                         {'cls': ListItemLabel,
                          'kwargs':{'text': "Type: " + obj.type}},
                         {'cls': ListItemLabel,
                          'kwargs':{'text': "Console: "+ obj.console}}]}
        self.lvAdapter = ListAdapter(data=self.lvData,
                                     args_converter=self.myConverter,
                                     propagate_selection_to_data=True,
                                     cls=CompositeListItem)
        self.listView = ListView(adapter=self.lvAdapter)

'''
PartyList takes a list of tuples, and turns it into a list of Party objects,
then it uses the list of party objects to create a custom listview
'''
class PartyList(Screen):
    def __init__(self,listOfTuples, **kwargs):
        super(PartyList, self).__init__(**kwargs)
        self.name = 'partylist'
        data = self.tuplesToDataList(listOfTuples)
        myListVariables = ListVariables(data)
        self.listView = ListView(adapter=myListVariables.lvAdapter)
        self.backButton = BackToJoinPartyFormButton()
        self.ids.myLayout.add_widget(self.listView)
        self.ids.myLayout.add_widget(self.backButton)

    def tuplesToDataList(self, list):
        data = []
        for tuple in list:
            tempParty = Party(tuple)
            data.append(tempParty)
        return data

class BaseScreen(Screen):
    def openPartyList(self):
        tupleList = [testTuple]
        self.manager.add_widget(PartyList(tupleList))
        self.manager.current = 'partylist'

class RootWidget(ScreenManager):
    pass

class FormEditorApp(App):
    def build(self):
        #r = RootWidget()
        return RootWidget()

if __name__ == '__main__':
    FormEditorApp().run()