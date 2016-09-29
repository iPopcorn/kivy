from kivy.uix.screenmanager import Screen
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.models import SelectableDataItem
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.listview import ListItemButton, CompositeListItem, ListView
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.app import App

import sqlite3
import GroupForms
import copy

# dbConnection
def createFriendListFromDB():
    friend_list = []
    appRoot = App.get_running_app().root
    conn = sqlite3.connect(appRoot.dbFile)
    cursor = conn.cursor()
    myUid = appRoot.curUser

    cursor.execute('''
        SELECT friend_uid
        FROM FriendTable
        WHERE uid = ?
    ''', (myUid,))

    resultList = cursor.fetchall()

    if resultList:
        for fTuple in resultList:
            friendID = fTuple[0]
            tempFriend = Friend(friendID)
            friend_list.append(tempFriend)
    else:
        print("No friends found for userID: " + str(myUid))
        return

    return friend_list

'''
submitMsg() takes a Friend object and TextInput object as its arguments.
It gets the senderID from the app's root manager, and the receiverID from the Friend object. It then compiles a
tuple with the 2 ID's and the text attribute from the TextInput object for insertion into the database.

dbConnection
'''
def submitMsg(friendObject, messageInput):
    # get root widget of the app and use it to get the dbFile and senderID
    appRoot = App.get_running_app().root
    senderID = appRoot.curUser

    # grab id from Friend object
    receiverID = friendObject.userID

    # connect to the database
    conn = sqlite3.connect(appRoot.dbFile)
    cursor = conn.cursor()

    # compile tuple for insertion into database
    msgTuple = (senderID, receiverID, messageInput.text)

    # database query
    cursor.execute('''
        INSERT INTO Messages (sender_id, receiver_id, message)
        VALUES (?,?,?)
    ''', msgTuple)

    # save changes to database and close connection
    conn.commit()
    conn.close()
    # popup.dismiss()
    print("submitMsg() finished!")

'''
SubmitMessageButton class is a subclass of Button
This class is responsible for putting the messages in the database. The constructor takes a Friend object and
a TextInput object.
'''
class SubmitMessageButton(Button):
    # popupObject is needed to close the popup after sending the message
    popupObject = None
    def __init__(self, friendObject, messageInput, **kwargs):
        super(SubmitMessageButton, self).__init__(**kwargs)
        self.friendObject = friendObject
        self.messageInput = messageInput

    # on_press calls the submitMsg() function
    def on_press(self):
        submitMsg(self.friendObject, self.messageInput)
        self.popupObject.dismiss()

    # setter function for popupObject
    def setPopupObject(self, popupObject):
        self.popupObject = popupObject


class FriendBackButton(Button):
    def __init__(self, **kwargs):
        super(FriendBackButton, self).__init__(**kwargs)


class Friend(SelectableDataItem):
    userID = -1
    userName = ""
    facebook = ""
    twitter = ""
    reddit = ""
    google = ""
    skype = ""
    xbl = ""
    psn = ""
    nintendo = ""
    steam = ""
    privacyDict = {}

    def __init__(self, uid, **kwargs):
        super(Friend, self).__init__(**kwargs)
        self.userID = uid
        self.userName = self.setUserName()
        self.setHandles()
        self.getPrivacy()
# dbConnection
    def setUserName(self):
        # connect to database
        AppRoot = App.get_running_app().root
        conn = sqlite3.connect(AppRoot.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username
            FROM Login
            WHERE uid = ?
        ''', (self.userID,))

        result = cursor.fetchone()

        # if result return the username, else print that username couldn't be found and return empty string
        if result:
            return result[0]
        else:
            print("No username found for user id: " + str(self.userID))
            return ""

    # dbConnection
    def setHandles(self):
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM ContactInfo
            WHERE uid = ?
        ''', (self.userID,))

        result = cursor.fetchone()
        if result:
            self.facebook = result[1]
            self.twitter = result[2]
            self.reddit = result[3]
            self.google = result[4]
            self.skype = result[5]
            self.xbl = result[6]
            self.psn = result[7]
            self.nintendo = result[8]
            self.steam = result[9]
        else:
            print("No handles found for user id: " + str(self.userID))
            return

    # dbConnection
    def getPrivacy(self):
        # connect to database
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        # grab privacy settings for current user
        cursor.execute('''
            SELECT *
            FROM Privacy
            WHERE uid = ?
        ''', (self.userID,))

        result = cursor.fetchone()
        if result:
            if result[1] == 1:
                self.privacyDict['facebook'] = self.facebook
            if result[2] == 1:
                self.privacyDict['twitter'] = self.twitter
            if result[3] == 1:
                self.privacyDict['reddit'] = self.reddit
            if result[4] == 1:
                self.privacyDict['google'] = self.google
            if result[5] == 1:
                self.privacyDict['skype'] = self.skype
            if result[6] == 1:
                self.privacyDict['xbl'] = self.xbl
            if result[7] == 1:
                self.privacyDict['psn'] = self.psn
            if result[8] == 1:
                self.privacyDict['nintendo'] = self.nintendo
            if result[9] == 1:
                self.privacyDict['steam'] = self.steam
            print(str(self.privacyDict))
        else:
            print("No privacy settings found for userID: " + str(self.userID))
            return


# FriendInfoScreen displays public profile information of the selected user
# todo: clear off old friendInfoScreen
class FriendInfoScreen(Screen):
    def __init__(self, friendObject, **kwargs):
        super(FriendInfoScreen, self).__init__(**kwargs)

        for key, value in friendObject.privacyDict.items():
            keyLabel = Label(text=key)
            valueLabel = Label(text=value)
            self.ids.myGridLayout.add_widget(keyLabel)
            self.ids.myGridLayout.add_widget(valueLabel)

        backButton = FriendBackButton(text='Go Back', size_hint_y=0.1)
        self.ids.myLayout.add_widget(backButton)


class GroupPopup(Popup):
    friendObject = ObjectProperty(None)

    def __init__(self, friendObject, **kwargs):
        super(GroupPopup,  self).__init__(**kwargs)
        self.friendObject = friendObject

    def inviteToGroup(self):
        pass


class InviteToGroup(ListItemButton):
    def sendInvite(self, parentScreen):
        parentScreen.sendInvite(self.index)
# todo: group invite logic
class GroupInviteButton(ListItemButton):

    def inviteToGroup(self):
        # get friend object from list
        manager = App.get_running_app().root
        parentScreen = manager.children[0]
        adapter = parentScreen.myListAdapter
        index = self.parent.index
        friendObject = adapter.get_data_item(index)

        parentScreen.setFriendID(friendObject.userID)


        # invPopup = Popup(title='Invite to Group', content=invPopupContent, size_hint=(0.5, 0.5))


        # closeButton.bind(on_press=invPopup.dismiss)

        parentScreen.invitePopup.open()
        # submit invite to database

'''
The SendMsgButton is one of the class that makes up the CompositeListItem of the FriendScreen ListView.
In the friendlist.kv file, it is defined to call the sendMessage() function on_release.
The sendMessage() function opens up a popup. When the user clicks send, the text in the textbox is stored in the
Messages table of the database.
'''
class SendMsgButton(ListItemButton):
    '''
    sendMessage() adds messages to the Message table of the database. The Message table has 4 columns.
    message_id, sender_id, receiver_id, message. sendMessage() is only concerned with the last 3 columns.

    The first thing sendMessage() does is get the Friend object that is represented by the list item. Then it creates
    a BoxLayout widget to store all the widgets as the 'content' for the popup. Finally, the function opens the popup()
    '''
    def sendMessage(self):
        # get Friend object
        manager = App.get_running_app().root
        parentScreen = manager.children[0]
        adapter = parentScreen.myListAdapter
        index = self.parent.index
        friendObject = adapter.get_data_item(index)

        # create the 'content' of the popup object
        msgPopupContent = BoxLayout(orientation='vertical')
        msgPopupContent.spacing = msgPopupContent.height * 0.05

        msgInput = TextInput()

        buttonLayout = BoxLayout(size_hint_y=0.3)
        buttonLayout.spacing = buttonLayout.width * 0.05

        closeButton = Button(text='Close this popup')

        # submitButton is an instance of a special button class made just for handling the database logic
        submitButton = SubmitMessageButton(friendObject, msgInput, text='Send Message!')

        buttonLayout.add_widget(closeButton)
        buttonLayout.add_widget(submitButton)
        msgPopupContent.add_widget(msgInput)
        msgPopupContent.add_widget(buttonLayout)

        # create and open the popup object
        msgPopup = Popup(title='Send Message', content=msgPopupContent, size_hint=(0.5, 0.5))
        closeButton.bind(on_release=msgPopup.dismiss)
        submitButton.setPopupObject(msgPopup)
        msgPopup.open()


class FriendItemButton(ListItemButton):

    def displayFriendInfo(self):
        myFriend = Friend(1)
        print(str(self) + ".displayFriendInfo() called")
        rootApp = App.get_running_app()
        manager = rootApp.root
        manager.add_widget(FriendInfoScreen(myFriend))
        manager.current = 'friendinfoscreen'
        # parentScreen = self.parent.parent.parent.parent.parent.parent
        # print(str(parentScreen.manager))
        # print(str(manager))


class ListCreator:
    def __init__(self, data):
        self.data = data

        self.myConverter = lambda row_index, obj: {
            'text': obj.userName,
            'size_hint_y': None,
            'height': 25,
            'cls_dicts': [{'cls': FriendItemButton,
                           'kwargs': {'text': obj.userName,
                                      'is_representing_cls': True}},
                          {'cls': SendMsgButton,
                           'kwargs': {'text': 'Send Message'}},
                          {'cls': GroupInviteButton,
                           'kwargs': {'text': 'Invite to group'}}]}

        self.myAdapter = ListAdapter(data=self.data,
                                     args_converter=self.myConverter,
                                     propagate_selection_to_data=True,
                                     cls=CompositeListItem)

        self.myListView = ListView(adapter=self.myAdapter)
'''
# working code: do not touch
class ListCreator:
    def __init__(self, data):
        self.data = data
        self.myConverter = lambda row_index, rec: {
            'text': rec['Name'],
            'size_hint_y': None,
            'height': 25,
            'cls_dicts': [{'cls': FriendItemButton,
                           'kwargs': {'text': rec['Name'],
                                      'is_representing_cls': True}},
                          {'cls': SendMsgButton,
                           'kwargs': {'text': 'Send Message'}},
                          {'cls': GroupInviteButton,
                           'kwargs': {'text': 'Invite to group'}}]}
        self.item_strings = ['{0}'.format(index) for index in range(10)]
        self.myAdapter = DictAdapter(sorted_keys=self.item_strings,
                                     data=friend_dict,
                                     args_converter=self.myConverter,
                                     selection_mode='single',
                                     allow_empty_selection=True,
                                     cls=CompositeListItem)

'''


# todo: friend button should open up friend profile screen
class FriendScreen(Screen):
    friendID = NumericProperty(0)
    groupList = ListProperty()
    invitePopup = ObjectProperty(None)
    def __init__(self, data, **kwargs):
        super(FriendScreen, self).__init__(**kwargs)
        self.myListCreator = ListCreator(data)
        self.myListAdapter = self.myListCreator.myAdapter
        self.myListView = self.myListCreator.myListView

        self.mainMenuButton = Button(text='Main Menu', size_hint_y=0.1)
        self.mainMenuButton.bind(on_release=self.goBack)

        closePopupButton = Button(text='Close', size_hint_y=0.1)
        popupContent = self.createPopupContent()
        self.invitePopup = Popup(title='Invite To Group', content=popupContent, size_hint=(0.5, 0.5))
        self.bindCloseButton(closePopupButton)

        self.ids.friendLayout.add_widget(self.myListView)
        self.ids.friendLayout.add_widget(self.mainMenuButton)

    def bindCloseButton(self, button):
        button.bind(on_release=self.invitePopup.dismiss)
        self.invitePopup.content.add_widget(button)
    def createPopupContent(self):
        # create popup widget
        invPopupContent = BoxLayout(orientation='vertical')
        invPopupContent.spacing = invPopupContent.height * 0.05

        # List of groups user belongs to
        groupList = GroupForms.createGroupListFromDB()
        self.setGroupList(groupList)

        # create ListView
        argsConverter = lambda row_index, obj: {'text': obj.name,
                                                'size_hint_y': None,
                                                'height': 25}

        myAdapter = ListAdapter(data=groupList,
                                args_converter=argsConverter,
                                propagate_selection_to_data=True,
                                cls=InviteToGroup)

        myListView = ListView(adapter=myAdapter)

        # closeButton = Button(text='Close')
        createGroupButton = Button(text='Create New Group', size_hint_y=0.1)
        createGroupButton.bind(on_release=self.createGroup)
        invPopupContent.add_widget(myListView)
        # invPopupContent.add_widget(closeButton)
        invPopupContent.add_widget(createGroupButton)

        return invPopupContent

    def createGroup(self, obj):
        self.invitePopup.dismiss()
        self.manager.current = 'creategroup'
    def goBack(self, obj):
        self.manager.current = 'mainscreen'

    def setGroupList(self, groupList):
        self.groupList = groupList

    def setFriendID(self, friendID):
        print("friend id received: " + str(friendID))
        self.friendID = float(friendID)
        print("self.friendID: " + str(self.friendID))

    # dbConnection
    def sendInvite(self, index):
        print(str(self.ids.friendLayout.children))

        group = self.groupList[index]
        groupID = group.groupID
        appRoot = App.get_running_app().root
        senderID = appRoot.curUser
        inviteTuple = (senderID, int(self.friendID), groupID)

        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO GroupInvite (sender_id, receiver_id, group_id)
            VALUES (?,?,?)
        ''', inviteTuple)

        conn.commit()
        conn.close()

        self.invitePopup.dismiss()