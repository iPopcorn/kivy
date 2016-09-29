from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.adapters.listadapter import ListAdapter
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.listview import ListView, ListItemButton
from kivy.properties import ObjectProperty
from kivy.adapters.models import SelectableDataItem
from kivy.uix.label import Label
from kivy.app import App

import sqlite3

from GroupForms import getIDbyName
import LoginScreen


def convertPyBoolToSQL(pyBool):
    if pyBool:
        return 1
    else:
        return 0


# dbConnection
def createGameListFromDB():
    myRoot = LoginScreen.getRoot()
    gameList = []
    conn = sqlite3.connect(myRoot.dbFile)
    cursor = conn.cursor()

    curUser = myRoot.curUser

    cursor.execute('''
    SELECT *
    FROM GameTable
    WHERE uid = ?
    ''', (curUser,))

    resultList = cursor.fetchall()

    if resultList:
        for result in resultList:
            gameID = result[1]

            cursor.execute('''
            SELECT *
            FROM Game
            WHERE game_id = ?
            ''', (gameID,))

            gameTuple = cursor.fetchone()

            tempGame = Game(gameTuple)
            gameList.append(tempGame)
    else:
        print("User not following any games!")

    return gameList


class PrivacySubmitButton(Button):
    def submitPrivacySettings(self):
        # get screen object
        myScreen = App.get_running_app().root.children[0]
        # call submit function
        myScreen.submitToDatabase()


class BrowseScreen(Screen):

    # todo: make findGame query more robust, should return a list of games if at least 1 part of form is filled out
    # currently only uses the game name to find a game
    # dbConnection
    def findGame(self):
        print("findGame() called.")

        myRoot = LoginScreen.getRoot()

        conn = sqlite3.connect(myRoot.dbFile)
        cursor = conn.cursor()

        # genreText = self.ids.genreSpinner.text
        gameText = self.ids.gameInput.text
        # consoleText = self.ids.consoleSpinner.text

        gameID = getIDbyName(gameText)

        if gameID == -1:
            print("No game with that name")
            return

        cursor.execute('''
        SELECT *
        FROM Game
        WHERE game_id = ?
        ''', (gameID,))

        result = cursor.fetchone()

        # create game object from tuple
        # create game info screen from game object

    def addGame(self):
        print("addGame() called.")


class HandlesLayout(GridLayout):
    pass


class SocialPrivacyScreen(Screen):
    def submitToDatabase(self):
        print(str(self) + ".submitToDatabase() called")

        # setup db connection
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        myUid = appRoot.curUser

        # get data from switches
        fbSwitch = convertPyBoolToSQL(self.ids.fbSwitch.active)
        twitterSwitch = convertPyBoolToSQL(self.ids.twitterSwitch.active)
        redditSwitch = convertPyBoolToSQL(self.ids.redditSwitch.active)
        googleSwitch = convertPyBoolToSQL(self.ids.googleSwitch.active)
        skypeSwitch = convertPyBoolToSQL(self.ids.skypeSwitch.active)

        #check if tuple exists
        cursor.execute('''
            SELECT *
            FROM Privacy
            WHERE uid = ?
        ''', (myUid,))

        result = cursor.fetchone()

        if result:
            # update tuple
            updateTuple = (fbSwitch, twitterSwitch, redditSwitch, googleSwitch, skypeSwitch, myUid)

            cursor.execute('''
                UPDATE Privacy
                SET facebook = ?, twitter = ?, reddit = ?, google = ?, skype = ?
                WHERE uid = ?
            ''', updateTuple)
        else:
            insertTuple = (myUid, fbSwitch, twitterSwitch, redditSwitch, googleSwitch, skypeSwitch)

            cursor.execute('''
                INSERT INTO Privacy
                VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
            ''', insertTuple)

        conn.commit()
        conn.close()


class GamePrivacyScreen(Screen):
    # dbConnection
    def submitToDatabase(self):
        print(str(self) + ".submitToDatabase() called")

        # setup db connection
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        myUid = appRoot.curUser

        # get data from switches
        xblSwitch = self.ids.xblSwitch.active
        psnSwitch = self.ids.psnSwitch.active
        nintendoSwitch = self.ids.nintendoSwitch.active
        steamSwitch = self.ids.steamSwitch.active

        xblInt = convertPyBoolToSQL(xblSwitch)
        psnInt = convertPyBoolToSQL(psnSwitch)
        nintendoInt = convertPyBoolToSQL(nintendoSwitch)
        steamInt = convertPyBoolToSQL(steamSwitch)

        cursor.execute('''
            SELECT *
            FROM Privacy
            WHERE uid = ?
        ''', (myUid,))

        result = cursor.fetchone()
        privacyTuple = (xblInt, psnInt, nintendoInt, steamInt, myUid)

        if result:
            # update tuple
            cursor.execute('''
                UPDATE Privacy
                SET xboxlive = ?, psn = ?, nintendo = ?, steam = ?
                WHERE uid = ?
            ''', privacyTuple)
        else:
            insertTuple = (myUid, xblInt, psnInt, nintendoInt, steamInt)
            # insert tuple
            cursor.execute('''
                INSERT INTO Privacy
                VALUES (?, 0, 0, 0, 0, 0, ?, ?, ?, ?)
            ''', insertTuple)

        conn.commit()
        conn.close()



# todo: add submit button
# todo: modify changes in database
class PrivacyScreen(Screen):
    # dbConnection
    def submitToDatabase(self):
        print(str(self) + ".submitToDatabase() called")

        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        myUid = appRoot.curUser

        #get data from forms
        socialMediaValue = self.ids.socialMediaSwitch.active
        gamingNetworksValue = self.ids.gamingNetworksSwitch.active

        if socialMediaValue:
            # figure out if tuple exists for current user
            cursor.execute('''
                SELECT *
                FROM Privacy
                WHERE uid = ?
            ''', (myUid,))

            result = cursor.fetchone()

            # if tuple already exists, update tuple
            if result:
                cursor.execute('''
                    UPDATE Privacy
                    SET facebook = 1, twitter = 1, reddit = 1, google = 1, skype = 1
                    WHERE uid = ?
                ''', (myUid,))

            # insert new tuple for current user
            else:
                cursor.execute('''
                    INSERT INTO Privacy (uid, facebook, twitter, reddit, google, skype)
                    VALUES (?, 1, 1, 1, 1, 1)
                ''', (myUid,))
        if gamingNetworksValue:
            # figure out if tuple exists for current user
            cursor.execute('''
                SELECT *
                FROM Privacy
                WHERE uid = ?
            ''', (myUid,))

            result = cursor.fetchone()

            # if tuple already exists, update tuple
            if result:
                cursor.execute('''
                    UPDATE Privacy
                    SET xboxlive = 1, psn = 1, nintendo = 1, steam = 1
                    WHERE uid = ?
                ''', (myUid,))
            else:
                cursor.execute('''
                    INSERT INTO Privacy (uid, xboxlive, psn, nintendo, steam)
                    VALUES (?, 1, 1, 1, 1)
                ''', (myUid,))
        if not socialMediaValue:
            # figure out if tuple exists for current user
            cursor.execute('''
                SELECT *
                FROM Privacy
                WHERE uid = ?
            ''', (myUid,))

            result = cursor.fetchone()

            # if tuple already exists, update tuple
            if result:
                cursor.execute('''
                    UPDATE Privacy
                    SET facebook = 0, twitter = 0, reddit = 0, google = 0, skype = 0
                    WHERE uid = ?
                ''', (myUid,))

            # insert new tuple for current user
            else:
                cursor.execute('''
                    INSERT INTO Privacy (uid, facebook, twitter, reddit, google, skype)
                    VALUES (?, 0, 0, 0, 0, 0)
                ''', (myUid,))
        if not gamingNetworksValue:
            # figure out if tuple exists for current user
            cursor.execute('''
                SELECT *
                FROM Privacy
                WHERE uid = ?
            ''', (myUid,))

            result = cursor.fetchone()

            # if tuple already exists, update tuple
            if result:
                cursor.execute('''
                    UPDATE Privacy
                    SET xboxlive = 0, psn = 0, nintendo = 0, steam = 0
                    WHERE uid = ?
                ''', (myUid,))
            else:
                cursor.execute('''
                    INSERT INTO Privacy (uid, xboxlive, psn, nintendo, steam)
                    VALUES (?, 0, 0, 0, 0)
                ''', (myUid,))

        conn.commit()
        conn.close()
        print("Switch Values: \nSocial Media: " + str(socialMediaValue) + "\nGaming Networks: " + str(gamingNetworksValue))


class HandleScreen(Screen):
    def __init__(self, **kwargs):
        super(HandleScreen, self).__init__(**kwargs)
        self.loadHandles()

    # dbConnection
    def loadHandles(self):
        # get information from database
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        uid = appRoot.curUser

        cursor.execute('''
            SELECT *
            FROM ContactInfo
            WHERE uid=?
        ''', (uid,))

        # if entry exists, load tuple into form
        result = cursor.fetchone()

        if result:
           self.ids.handlesLayout.ids.fbInput.text = result[1]
           self.ids.handlesLayout.ids.twitterInput.text = result[2]
           self.ids.handlesLayout.ids.redditInput.text = result[3]
           self.ids.handlesLayout.ids.googleInput.text = result[4]
           self.ids.handlesLayout.ids.skypeInput.text = result[5]
           self.ids.handlesLayout.ids.xblInput.text = result[6]
           self.ids.handlesLayout.ids.psnInput.text = result[7]
           self.ids.handlesLayout.ids.nintendoInput.text = result[8]
           self.ids.handlesLayout.ids.steamInput.text = result[9]
        else:
            pass
        pass

    # dbConnection
    def updateHandles(self):
        appRoot = App.get_running_app().root
        conn = sqlite3.connect(appRoot.dbFile)
        cursor = conn.cursor()

        uid = appRoot.curUser
        fb = self.ids.handlesLayout.ids.fbInput.text
        twitter = self.ids.handlesLayout.ids.twitterInput.text
        reddit = self.ids.handlesLayout.ids.redditInput.text
        google = self.ids.handlesLayout.ids.googleInput.text
        skype = self.ids.handlesLayout.ids.skypeInput.text
        xbl = self.ids.handlesLayout.ids.xblInput.text
        psn = self.ids.handlesLayout.ids.psnInput.text
        nintendo = self.ids.handlesLayout.ids.nintendoInput.text
        steam = self.ids.handlesLayout.ids.steamInput.text

        updateTuple = (fb, twitter, reddit, google, skype, xbl, psn, nintendo, steam, uid)
        insertTuple = (uid, fb, twitter, reddit, google, skype, xbl, psn, nintendo, steam)

        cursor.execute('''
            SELECT *
            FROM ContactInfo
            WHERE uid = ?
        ''',(uid,))

        result = cursor.fetchone()

        #check if entry already exists in database, if so, update entry, else insert new entry
        if result:
            cursor.execute('''
                UPDATE ContactInfo
                SET facebook=?, twitter=?, reddit=?, google=?, skype=?, xboxlive=?, psn=?, nintendo=?, steam=?
                WHERE uid=?
            ''', updateTuple)
        else:
            cursor.execute('''
                INSERT INTO ContactInfo
                VALUES (?,?,?,?,?,?,?,?,?,?)
            ''', insertTuple)

        conn.commit()
        conn.close()
        print("Handles Updated!")


class BackButtonGameInfo(Button):
    pass


class GameInfoScreen(Screen):
    def __init__(self, game, **kwargs):
        super(GameInfoScreen, self).__init__(**kwargs)
        consoleAdapter = SimpleListAdapter(data=game.console,
                                           cls=Label)
        genreAdapter = SimpleListAdapter(data=game.genre,
                                         cls=Label)
        nameLabel = Label(text=game.name)
        descriptionLabel1 = Label(text='description')
        descriptionLabel2 = Label(text=game.description)
        genreLabel = Label(text='Genre')
        consoleLabel = Label(text='Console')
        backButton = BackButtonGameInfo(text='Go Back')
        consoleList = ListView(adapter=consoleAdapter)
        genreList = ListView(adapter=genreAdapter)
        self.ids.myLayout.add_widget(nameLabel)
        self.ids.myLayout.add_widget(genreLabel)
        self.ids.myLayout.add_widget(genreList)
        self.ids.myLayout.add_widget(descriptionLabel1)
        self.ids.myLayout.add_widget(descriptionLabel2)
        self.ids.myLayout.add_widget(consoleLabel)
        self.ids.myLayout.add_widget(consoleList)
        self.ids.myLayout.add_widget(backButton)


class Game(SelectableDataItem):
    name = ""
    gameID = 0
    console = []
    genre = []
    text = ""
    description = ""

    '''
    def __init__(self, name, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.name = name
        self.text = name
        self.console = ['Xbox 360', 'PC']
        self.genre = ['FPS', 'Action']
        self.description = "This is a short synposis of the game"
    '''
    def __init__(self, gameTuple, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.name = gameTuple[1]
        self.description = gameTuple[2]
        self.text = self.name
        self.console = ['Not Yet Working']
        self.genre = self.setGenre(gameTuple)


    def setGenre(self, gameTuple):
        index = 3
        indexList = []
        while index < len(gameTuple):
            if gameTuple[index] == 1:
                indexList.append(index)
            index += 1

        genreList = self.convertIndexToGenre(indexList)
        return genreList

    def convertIndexToGenre(self, indexList):
        genreList = []
        for i in indexList:
            if i == 3:
                genre = 'fps'
                genreList.append(genre)
            elif i == 4:
                genre = 'action'
                genreList.append(genre)
            elif i == 5:
                genre = 'adventure'
                genreList.append(genre)
            elif i == 6:
                genre = 'puzzle'
                genreList.append(genre)
            elif i == 7:
                genre = 'racing'
                genreList.append(genre)
            elif i == 8:
                genre = 'simulation'
                genreList.append(genre)
            elif i == 9:
                genre = 'rpg'
                genreList.append(genre)
            elif i == 10:
                genre = 'sports'
                genreList.append(genre)
            elif i == 11:
                genre = 'tps'
                genreList.append(genre)
            elif i == 12:
                genre = 'rts'
                genreList.append(genre)
            elif i == 13:
                genre = 'strategy'
                genreList.append(genre)

        return genreList


# exampleGameData = [Game('Halo 3'), Game('Gears Of War'), Game('Call of Duty 4')]


class GameButton(ListItemButton):
    pass


class ListVariables:

    def __init__(self, data):
        self.lvData = data
        self.argsConverter = lambda row_index, obj: {'text': obj.text,
                                                     'size_hint_y': None,
                                                     'height': 25}
        self.lvAdapter = ListAdapter(data=self.lvData,
                                     args_converter=self.argsConverter,
                                     propagate_selection_to_data=True,
                                     cls=GameButton)
        self.listView = ListView(adapter=self.lvAdapter)


class GameScreen(Screen):

    def __init__(self, data, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.myListVars = ListVariables(data)
        self.list_adapter = self.myListVars.lvAdapter
        self.backButton = Button(text='Go Back', size_hint_y=0.1)
        self.browseButton = Button(text='Browse or Add Game', size_hint_y=0.1)
        self.backButton.bind(on_release=self.goBack)
        self.browseButton.bind(on_release=self.browse)
        self.ids.gsLayout.add_widget(self.myListVars.listView)
        self.ids.gsLayout.add_widget(self.backButton)
        self.ids.gsLayout.add_widget(self.browseButton)

    def goBack(self, obj):
        self.manager.current = 'profilescreen'

    def browse(self, obj):
        self.manager.current = 'browsescreen'

    def displayGame(self, gameButton):
        curGame = self.list_adapter.data[gameButton.index]
        myGameInfoScreen = GameInfoScreen(curGame)
        for screen in self.manager.screens:
            if screen.name == myGameInfoScreen.name:
                self.manager.remove_widget(screen)
        self.manager.add_widget(myGameInfoScreen)
        self.manager.current = myGameInfoScreen.name
        print(self.manager.children)


class ProfileScreen(Screen):
    pass
