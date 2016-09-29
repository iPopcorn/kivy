from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.listview import ListView, ListItemButton
from kivy.properties import StringProperty, ObjectProperty
from kivy.adapters.models import SelectableDataItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App

import sqlite3


class GroupFilterDisplay(Screen):
    list_view = ObjectProperty(None)
    list_adapter = ObjectProperty(None)

    def __init__(self, listAdapter, **kwargs):
        super(GroupFilterDisplay, self).__init__(**kwargs)
        self.list_view = ListView(adapter=listAdapter)
        self.list_adapter = listAdapter
        self.ids.myLayout.add_widget(self.list_view)

    # todo: make this method global instead of repeating it twice
    def displayGroup(self, groupButton):
        curGroup = self.list_adapter.data[groupButton.index]
        myGroupInfoScreen = GroupInfoScreen(curGroup)
        for screen in self.manager.screens:
            if screen.name == myGroupInfoScreen.name:
                self.manager.remove_widget(screen)
        self.manager.add_widget(myGroupInfoScreen)
        self.manager.current = myGroupInfoScreen.name


class BackButton(Button):
    def __init__(self, **kwargs):
        super(BackButton, self).__init__(**kwargs)


class GroupButton(ListItemButton):
    pass


# dbConnection
def getIDbyName(name):
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()
        nameTuple = (name,)
        cursor.execute('''
            SELECT game_id
            FROM Game
            WHERE name=?
        ''', nameTuple)

        result = cursor.fetchone()
        if result:
            gameID = result[0]
        else:
            print("No game with that name found.")
            conn.close()
            return -1

        conn.close()
        return gameID

class GroupFilter(Screen):

    # todo: better way to query db that takes all arguments of form, or change the form
    # dbConnection
    def applyQuery(self):
        # connect to or create db file
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        # genreText = self.ids.genreSpinner.text
        gameText = self.ids.gameInput.text
        consoleText = self.ids.consoleSpinner.text
        typeText = self.ids.typeSpinner.text

        gameID = getIDbyName(gameText)

        if gameID == -1:
            print("No Game With that Name")
            return

        queryTuple = (gameID, consoleText, typeText)

        cursor.execute('''
                       SELECT *
                       FROM Groups
                       WHERE temp_group = 0
                       AND game_id = ?
                       AND console = ?
                       AND type = ?
                       ''', queryTuple)

        resultList = cursor.fetchall()
        if resultList:
            print(resultList)
            self.displayGroups(resultList)
        else:
            print("No results")

        conn.close()

        # print("Genre: %s\nGame: %s\nConsole: %s\nType: %s\n" % (self.ids.genreSpinner.text, self.ids.gameInput.text, \
            # self.ids.consoleSpinner.text, self.ids.typeSpinner.text))

    def displayGroups(self, groupList):
        groupObjectList = []
        for groupTuple in groupList:
            tempGroup = Group(groupTuple)
            groupObjectList.append(tempGroup)

        myListVar = ListVariables(groupObjectList)
        displayScreen = GroupFilterDisplay(myListVar.lvAdapter)
        self.manager.add_widget(displayScreen)
        self.manager.current = 'groupfilterdisplay'


class BrowseGroups(Screen):
    # dbConnection
    def viewAll(self):
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM Groups
            WHERE temp_group = 0
        ''')

        groupList = []
        resultList = cursor.fetchall()

        if resultList:
            for result in resultList:
                tempGroup = Group(result)
                groupList.append(tempGroup)
        else:
            print("No results")
            return

        myListVar = ListVariables(groupList)

        displayScreen = GroupFilterDisplay(myListVar.lvAdapter)
        for screen in self.manager.screens:
            if screen.name == 'groupfilterdisplay':
                self.manager.remove_widget(screen)

        self.manager.add_widget(displayScreen)
        self.manager.current = 'groupfilterdisplay'

        conn.close()


# TODO: add database logic
class CreateGroup(Screen):

    # dbConnection
    def submitGroup(self):
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        name = self.ids.nameInput.text
        description = self.ids.descriptionInput.text
        console = self.ids.consoleSpinner.text
        gameName = self.ids.gameInput.text
        myType = self.ids.typeSpinner.text
        gameID = GroupFilter.getIDbyName(gameName)

        creatorID = appRoot.curUser

        # todo: set public group option, right now defaults to true
        insertTuple = (0, gameID, 1, creatorID, 1, myType, name, description, console)

        cursor.execute('''
            INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
            VALUES (?,?,?,?,?,?,?,?,?)
        ''', insertTuple)

        conn.commit()

        # get group ID
        cursor.execute('''
            SELECT group_id
            FROM Groups
            WHERE name=?
        ''', (name,))
        result = cursor.fetchone()
        if result:
            groupID = result[0]

            # add user to group
            cursor.execute('''
                      INSERT INTO GroupTable
                      VALUES (?,?)
                  ''', (creatorID, groupID))

            conn.commit()
        else:
            print("Group not found")

        conn.close()
        print("INSERT SUCCESS")


class GroupInfoScreen(Screen):
    def __init__(self, group, **kwargs):
        super(GroupInfoScreen, self).__init__(**kwargs)
        self.myGroup = group
        self.name = 'groupinfoscreen'
        myListview = self.initList()
        # myLayout = BoxLayout(orientation='vertical',
        #                     size_hint=(None, None),
        #                     size=parentScreen.ids.myGroupsLayout.size,
        #                     pos=parentScreen.ids.myGroupsLayout.pos,
        #                     spacing=self.height*0.05)
        nameLabel = Label(text="Name: "+self.myGroup.name)
        gameLabel = Label(text="Game: "+self.myGroup.game)
        membersLabel = Label(text="Members")
        descriptionLabel = Label(text="Description: "+self.myGroup.description)
        backBtn = BackButton(text="Go Back")
        self.ids.myLayout.add_widget(nameLabel)
        self.ids.myLayout.add_widget(gameLabel)
        self.ids.myLayout.add_widget(descriptionLabel)
        self.ids.myLayout.add_widget(membersLabel)
        self.ids.myLayout.add_widget(myListview)
        self.ids.myLayout.add_widget(backBtn)

    def initList(self):
        data = self.myGroup.members
        # argsConverter = lambda row_index, str: {'text': str,
        #                                        'size_hint_y': None,
        #                                        'height': 25}
        self.list_adapter = SimpleListAdapter(data=data, cls=Label)
        listView = ListView(adapter=self.list_adapter)
        return listView


"""
::class:: GroupInfo is a widget that is responsible for displaying the
information related to the selected group
"""

'''
class GroupInfo(Widget):
    myGroup = None
    list_adapter = ObjectProperty(None)

    def __init__(self, group, parentScreen, **kwargs):
        super(GroupInfo, self).__init__(**kwargs)
        self.myGroup = group
        myListView = self.initList()
        nameLabel = Label(text="Name: "+self.myGroup.name)
        gameLabel = Label(text="Game: "+self.myGroup.game)
        descriptionLabel = Label(text="Description: "+self.myGroup.description)
        backBtn = BackButton(text="Go Back")
        myLayout = BoxLayout(orientation='vertical',
                             size_hint=(None, None),
                             size=parentScreen.ids.myGroupsLayout.size,
                             pos=parentScreen.ids.myGroupsLayout.pos,
                             spacing=self.height*0.05)

        myLayout.add_widget(nameLabel)
        myLayout.add_widget(gameLabel)
        myLayout.add_widget(descriptionLabel)
        myLayout.add_widget(myListView)
        myLayout.add_widget(backBtn)
        self.add_widget(myLayout)

    def reDraw(self):
        self.parent.reDraw()

    def initList(self):
        data = self.myGroup.members
        # argsConverter = lambda row_index, str: {'text': str,
        #                                        'size_hint_y': None,
        #                                        'height': 25}
        self.list_adapter = SimpleListAdapter(data=data, cls=Label)
        listView = ListView(adapter=self.list_adapter)
        return listView

    def goBack(self):
        print(str(self))
'''


class ListVariables:
    def __init__(self, data):
        # print("data: " + str(data))
        # print("memberList1: " + str(data[0].members))
        # print("memberList2: " + str(data[1].members))
        self.lvData = data
        self.argsConverter = lambda row_index, obj: {'text': obj.text,
                                                     'size_hint_y': None,
                                                     'height': 25}
        self.lvAdapter = ListAdapter(data=self.lvData,
                                     args_converter=self.argsConverter,
                                     propagate_selection_to_data=True,
                                     cls=GroupButton)
        self.listView = ListView(adapter=self.lvAdapter)


class Group(SelectableDataItem):
    groupID = 0
    gameID = 0
    curSize = 0
    creatorID = 0
    pub_group = False
    type = ""
    name = ""
    game = ""
    description = ""
    console = ""
    # members is a list of strings that are the usernames of the users that belong to the group

    # assumes myTuple is a complete tuple with all fields from 'groups' table
    def __init__(self, myTuple, **kwargs):
        super(Group, self).__init__(**kwargs)
        # TODO: grab dbFile from root
        self.dbFile = "temp.db"
        self.members = []
        self.groupID = myTuple[0]
        self.gameID = myTuple[2]
        self.curSize = myTuple[3]
        self.creatorID = myTuple[4]
        self.setPubGroup(myTuple[6])
        self.type = myTuple[7]
        self.name = myTuple[8]
        self.description = myTuple[9]
        self.getGameNameFromID()
        self.text = self.name
        self.is_selected = False
        # TODO: write method to get members of a group from 'GroupTable'
        # self.members = ['John', 'Tim', 'Bob']
        self.getMembers()

    # query db to fill in list of member usernames
    # dbConnection
    def getMembers(self):
        # connect to or create db file
        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
                   SELECT *
                   FROM GroupTable
                   WHERE group_id=?
                   ''', (self.groupID,))

        resultList = cursor.fetchall()
        # print("resultList: %s" % (str(resultList)))
        if resultList:
            # print("memberList at beginning of result loop: " + str(self.members))
            # result is a single tuple
            for result in resultList:
                uid = result[0]
                # grab username from uid
                cursor.execute('''
                SELECT username
                FROM Login
                WHERE uid=?
                ''', (uid,))

                uNameTuple = cursor.fetchone()
                username = uNameTuple[0]

                self.members.append(username)
                # print("self.members: " + str(self.members))
        else:
            print("Group has no members.")

        conn.close()

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
            self.game = result[0]
        else:
            print("No game found with that id")

        conn.close()

    def setPubGroup(self, myInt):
        if myInt is 0:
            self.pub_group = False
        elif myInt is 1:
            self.pub_group = True
        else:
            print("Error setPubGroup, Invalid int, setting pub_group to False")
            self.pub_group = False

    def printGroup(self):
        print("Name: " + self.name + "\n" + "Description: " + self.description + "\n" + "Game: " + self.game + "\n")

# myGroupList = [Group('Group1'), Group('Group2'), Group('Group3')]


# todo: figure out better way to do this
def createGroupListFromDB():
    # print("made it to createGroupListFromDB()")
    appRoot = App.get_running_app().root
    groupList = []
    conn = sqlite3.connect(appRoot.dbFile)
    cursor = conn.cursor()

    curUser = appRoot.curUser

    # get all group id's that user is associated with
    cursor.execute('''
        SELECT *
        FROM GroupTable
        WHERE uid = ?
    ''', (curUser,))

    # loop through grabbing and creating groups
    resultList = cursor.fetchall()
    if resultList:
        for result in resultList:
            groupID = result[1]
            cursor.execute('''
                SELECT *
                FROM Groups
                WHERE group_id=? AND temp_group = 0
            ''', (groupID,))

            groupTuple = cursor.fetchone()
            if groupTuple:
                tempGroup = Group(groupTuple)
                groupList.append(tempGroup)
    else:
        print("No Groups found for this user: " + str(curUser))

    # resultList = cursor.fetchall()
    # if resultList:
    #    for result in resultList:
    #        # print(result)
    #        tempGroup = Group(result)
    #        groupList.append(tempGroup)
    # else:
    #    print("No groups found")

    # print(groupList)
    conn.close()
    return groupList


# todo: fix MyGroups initialization from no db file
class MyGroups(Screen):
    # print("made it to MyGroups(Screen)")
    myApp = App.get_running_app()
    # manager = myApp.root
    myList = ObjectProperty(None)
    # myList = ListVariables(manager.groupList)
    # list_adapter = ObjectProperty(myList.lvAdapter)
    # selected_value = StringProperty('Select a button')

    def __init__(self, data, **kwargs):
        super(MyGroups, self).__init__(**kwargs)
        self.myList = ListVariables(data)
        self.list_adapter = self.myList.lvAdapter
        self.myListView = self.myList.listView
        self.ids.myLayout.add_widget(self.myListView)
        self.backButton = Button(text='Go Back', size_hint_y=0.1)
        self.backButton.bind(on_release=self.goBack)
        self.ids.myLayout.add_widget(self.backButton)

        print("MyGroups screen initialized with data: " + str(data))

    def goBack(self, obj):
        print("Object is: " + str(obj))
        self.manager.current = 'groupscreen'

    def displayGroup(self, groupButton):
        curGroup = self.list_adapter.data[groupButton.index]
        myGroupInfoScreen = GroupInfoScreen(curGroup)
        for screen in self.manager.screens:
            if screen.name == myGroupInfoScreen.name:
                self.manager.remove_widget(screen)
        self.manager.add_widget(myGroupInfoScreen)
        self.manager.current = myGroupInfoScreen.name


class GroupScreen(Screen):
    pass
