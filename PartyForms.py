# TODO: Make sure game console and form console match
# TODO: Make game name case insensitive

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.listview import ListView, ListItemButton, CompositeListItem, ListItemLabel
from kivy.adapters.models import SelectableDataItem
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ObjectProperty

import sqlite3


class PartyButton(ListItemButton):
    def myCallback(self):
        root = App.get_running_app().root
        currentScreen = root.current_screen
        currentUser = root.curUser
        myPartyObject = currentScreen.partyListAdapter.data[self.index]
        print("My Party Object is: " + str(myPartyObject))
        myPartyObject.addUserToParty(currentUser)


class Party(SelectableDataItem):
    groupID = 0
    gameID = 0
    curSize = 0
    creatorID = 0
    # todo: add expiration times
    # expireTime = 0
    type = ""
    console = ""
    dbFile = ""
    gameName = ""

    def __init__(self, myTuple, **kwargs):
        super(Party, self).__init__(**kwargs)
        # todo: get db file from root
        self.dbFile = "temp.db"
        self.groupID = myTuple[0]
        self.gameID = myTuple[2]
        self.curSize = myTuple[3]
        self.creatorID = myTuple[4]
        self.type = myTuple[7]
        self.console = myTuple[10]

        self.getGameNameFromID()
        self.printParty()

    def printParty(self):
        print("Group ID: %d\nGame ID: %d\nCurrent Size: %d\nCreator ID: %d\nType: %s\nConsole: %s\n" % (
            self.groupID, self.gameID, self.curSize, self.creatorID, self.type, self.console))

    # dbConnection
    def getGameNameFromID(self):
        # connect to or create db file
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT name
        FROM Game
        WHERE game_id=?
        ''', (self.gameID,))

        result = cursor.fetchone()
        if result:
            self.gameName = result[0]
        else:
            print("No game found with that id")

        conn.close()

    """
    addUserToParty() takes the user id as an int. It uses the user id to perform the necessary database logic
    to add a user to the party.

    dbConnection
    """
    def addUserToParty(self, userID):
        # open DB connection
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        # increment self.curSize
        self.curSize += 1

        # update curSize of this party object in database
        myTuple = (self.curSize, self.groupID)
        cursor.execute('''
        UPDATE Groups
        SET current_size=?
        WHERE group_id=?
        ''', myTuple)

        # update user to belong to this party
        # todo: add group table to tie users to groups
        userTuple = (userID, self.groupID)
        cursor.execute('''
        INSERT INTO GroupTable (uid, group_id)
        VALUES (?, ?)
        ''', userTuple)

        conn.commit()
        conn.close()
        pass


class ListVariables:
    def __init__(self, data):
        self.lvData = data
        self.myConverter = lambda row_index, obj: {
            'text': obj.gameName,
            'size_hint_y': None,
            'height': 25,
            'cls_dicts': [{'cls': PartyButton,
                           'kwargs': {'text': obj.gameName,
                                      'is_representing_cls': True}},
                          {'cls': ListItemLabel,  # needs keys 'curSize','type','console'
                           'kwargs': {'text': "Number of Members: " + str(obj.curSize)}},
                          {'cls': ListItemLabel,
                           'kwargs': {'text': "Type: " + obj.type}},
                          {'cls': ListItemLabel,
                           'kwargs': {'text': "Console: " + obj.console}}]}
        self.lvAdapter = ListAdapter(data=self.lvData,
                                     args_converter=self.myConverter,
                                     propagate_selection_to_data=True,
                                     cls=CompositeListItem)
        self.listView = ListView(adapter=self.lvAdapter)


class PartyListBackButton(Button):
    pass





def tuplesToPartyList(listOfTuples):
    data = []
    for myTuple in listOfTuples:
        tempParty = Party(myTuple)
        data.append(tempParty)
    return data

'''
PartyList takes a list of tuples, and turns it into a list of Party objects,
then it uses the list of party objects to create a custom listview
'''
class PartyList(Screen):
    partyListAdapter = ObjectProperty(None)

    def __init__(self, listOfTuples, **kwargs):
        super(PartyList, self).__init__(**kwargs)
        self.name = 'partylist'
        partyList = tuplesToPartyList(listOfTuples)
        myListVariables = ListVariables(partyList)
        self.partyListAdapter = myListVariables.lvAdapter
        self.listView = ListView(adapter=self.partyListAdapter)
        self.backButton = PartyListBackButton(text="Go Back")
        self.ids.myLayout.add_widget(self.listView)
        self.ids.myLayout.add_widget(self.backButton)

    def goBack(self):
        # self.manager.current = 'joinpartyscreen'
        print(self)


class MainMenuButton(Button):
    pass


class NavigationButtons(BoxLayout):
    pass


class InitialForm(Screen):
    def displayJoinPartyForm(self):
        self.parent.displayJoinPartyForm()

    def displayStartPartyForm(self):
        self.parent.displayStartPartyForm()


class JoinPartyForm(Screen):
    def __init__(self, dbFile, **kwargs):
        super(JoinPartyForm, self).__init__(**kwargs)
        self.dbFile = dbFile

    # dbConnection
    def submitForm(self):
        # get root widget of the app
        appRoot = App.get_running_app().root

        # setup database connection
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        # get data from form
        gameName = self.ids.gameInput.text
        console = self.ids.consoleSpinner.text

        # get gameID
        cursor.execute('''
        SELECT game_id
        FROM game
        WHERE name=?;
        ''', (gameName,))

        result = cursor.fetchone()
        if result:
            gameID = result[0]
            print(gameID)

            myTuple = (gameID, console)

            # query database
            cursor.execute('''
            SELECT * FROM Groups
            WHERE temp_group = 1
            AND game_id=?
            AND console=?
            ''', myTuple)

            result = cursor.fetchall()

            if result:
                print(result)

                # create PartyList Screen
                # todo: clear old partyList before adding new one
                partyList = PartyList(result)
                self.manager.add_widget(partyList)
                self.manager.current = 'partylist'
            else:
                print("No groups found")
        else:
            print("No game found")

        print('Form Submitted!')

        conn.close()


class StartPartyForm(Screen):
    def __init__(self, dbFile, **kwargs):
        super(StartPartyForm, self).__init__(**kwargs)
        self.dbFile = dbFile

    # todo: make sure console is a console that the game belongs to
    # todo: make game name case insensitive
    # dbConnection
    def submitForm(self):

        # get root widget of the app
        appRoot = App.get_running_app().root

        # setup database connection
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        # get data from form
        gameName = self.ids.gameInput.text
        gameConsole = self.ids.consoleSpinner.text
        partyType = self.ids.typeSpinner.text

        # get game id
        cursor.execute('''
        SELECT game_id FROM game
        WHERE name=?
        ''', (gameName,))

        result = cursor.fetchone()

        if result:
            print(result[0])
        else:
            print("No game matching that name.")

        gameID = result[0]
        tempGroupBool = 1
        currentSize = 1
        creatorID = appRoot.curUser
        pubGroup = 1

        myTuple = (tempGroupBool, gameID, currentSize, creatorID, pubGroup, partyType, gameConsole)

        cursor.execute('''
        INSERT INTO Groups (temp_group,game_id,current_size,creator_id,pub_group,type,console)
        VALUES (?,?,?,?,?,?,?)
        ''', myTuple)

        conn.commit()
        conn.close()

        print('Form Submitted!')
