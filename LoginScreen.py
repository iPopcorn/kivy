from kivy.uix.screenmanager import Screen
from kivy.app import App

from hashlib import sha256

import sqlite3
import re

import GroupForms
import ProfileForms
import FriendList


# This is an example of how to get the root widget of the app
def getRoot():
    myApp = App.get_running_app()
    print(myApp.root)

    return myApp.root

# dbConnection
def insertUser(email, username, password, dbFile):
    hasher = sha256()
    hasher.update(password.encode('utf-8'))
    hashedPW = str(hasher.digest())

    conn = sqlite3.connect(dbFile)
    cursor = conn.cursor()
    myTuple = (email, username, hashedPW)

    cursor.execute('''
            INSERT INTO Login (email,username,password)
            VALUES (?,?,?)''', myTuple)

    conn.commit()
    conn.close()


def setFile(file):
        matchObj = re.match(r'.+\.db', file)
        if matchObj is not None:
            print("dbFile set correctly")
            return file
        else:
            print("Incorrect file format")


class HomeScreen(Screen):
    pass


class LoginScreen(Screen):
    def __init__(self, dbFile, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.dbFile = setFile(dbFile)
        self.loginCounter = 0

    # submitLoginDetails is the callback for the 'submitLogin' button on the LoginScreen class.
    # this function initializes the 'mygroups' screen
    # dbConnection
    # TODO: make counter persistent between launches, only timer should reset them
    def submitLoginDetails(self):
        self.loginCounter += 1
        appRoot = App.get_running_app().root
        if self.loginCounter <= 3:
            hasher = sha256()
            username = self.ids.loginText.text
            password = self.ids.passwordText.text
            hasher.update(password.encode('utf-8'))
            hashedPW = str(hasher.digest())
            conn = sqlite3.connect(self.dbFile)
            cursor = conn.cursor()
            myTuple = (username,)

            cursor.execute('''
            SELECT uid, password
            FROM Login
            WHERE username=?
            ''', myTuple)

            result = cursor.fetchone()
            if result:
                if result[1] == hashedPW:
                    print("PASSWORD VALIDATED")
                    self.manager.current = 'mainscreen'
                    appRoot.curUser = result[0]
                    # print("result[0]: " + str(result[0]) + " appRoot.curUser: " + str(appRoot.curUser))
                    groupList = GroupForms.createGroupListFromDB()
                    gameList = ProfileForms.createGameListFromDB()
                    friendList = FriendList.createFriendListFromDB()
                    for screen in self.manager.screens:
                        if screen.name == 'mygroups':
                            self.manager.remove_widget(screen)
                    self.manager.add_widget(FriendList.FriendScreen(friendList))
                    self.manager.add_widget(ProfileForms.GameScreen(gameList))
                    self.manager.add_widget(GroupForms.MyGroups(groupList))
                    self.manager.add_widget(ProfileForms.HandleScreen())
                else:
                    # TODO: setup timer to reset attempts
                    print("INVALID PASSWORD")
            else:
                print("No user found with that name")
        else:
            print("TOO MANY LOGIN ATTEMPTS")


class SignupScreen(Screen):

    def __init__(self, dbFile, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.dbFile = setFile(dbFile)

    """
    submitSignupDetails() is the callback for the signup button.

    dbConnection
    """
    def submitSignupDetails(self):
        hasher = sha256()

        emailField = self.ids.emailText
        usernameField = self.ids.userText
        passwordField = self.ids.signupPasswordText

        hasher.update(passwordField.text.encode('utf-8'))
        hashedPW = str(hasher.digest())

        conn = sqlite3.connect(self.dbFile)
        cursor = conn.cursor()

        myTuple = (emailField.text, usernameField.text, hashedPW)

        cursor.execute('''
        INSERT INTO Login (email,username,password)
        VALUES (?,?,?)''', myTuple)

        conn.commit()
        conn.close()
        # self.manager.current = 'loginscreen'
        self.manager.current = 'homescreen'
        # loginFile = open('login.txt', 'w')
        # loginFile.write(("%s\n%s\n%s\n")%(emailField.text,usernameField.text,passwordField.text))
