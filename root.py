from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

import sqlite3
import os

import MainMenu
import LoginScreen
import PartyForms
import GroupForms
import FriendList
import ProfileForms

DEFAULT_TEST_USER = 1
dbFile = "temp.db"
Builder.load_file('loginscreen.kv')
Builder.load_file('mainmenu.kv')
# Builder.load_file('partyforms.kv')


class RootManager(ScreenManager):
    curUser = NumericProperty(0)
    dbFile = StringProperty(dbFile)

    def __init__(self, **kwargs):
        super(RootManager, self).__init__(**kwargs)

        # Add all screens for the app
        self.add_widget(LoginScreen.HomeScreen())
        self.add_widget(LoginScreen.LoginScreen(dbFile))
        self.add_widget(LoginScreen.SignupScreen(dbFile))
        self.add_widget(MainMenu.MainScreen())
        # self.add_widget(FriendList.FriendScreen())
        self.add_widget(MainMenu.GroupScreen())
        self.add_widget(MainMenu.PlayNowScreen())
        self.add_widget(ProfileForms.ProfileScreen())
        self.add_widget(PartyForms.InitialForm())
        self.add_widget(PartyForms.StartPartyForm(dbFile))
        self.add_widget(PartyForms.JoinPartyForm(dbFile))
        # self.add_widget(GroupForms.MyGroups())
        self.add_widget(GroupForms.CreateGroup())
        self.add_widget(GroupForms.BrowseGroups())
        self.add_widget(GroupForms.GroupFilter())
        self.add_widget(ProfileForms.GamePrivacyScreen())
        self.add_widget(ProfileForms.PrivacyScreen())
        self.add_widget(ProfileForms.SocialPrivacyScreen())
        self.add_widget(ProfileForms.BrowseScreen())


class RootApp(App):

    # dbConnection
    @staticmethod
    def initDatabase():

        # connect to or create db file
        conn = sqlite3.connect(dbFile)
        cursor = conn.cursor()
        # enable foreign keys
        cursor.execute('PRAGMA foreign_keys = ON;')
        conn.commit()
        # create Login table
        cursor.execute('''
        CREATE TABLE Login (uid integer NOT NULL CONSTRAINT user_id PRIMARY KEY,
                            email text NOT NULL UNIQUE,
                            username text NOT NULL UNIQUE,
                            password text NOT NULL);
        ''')


        cursor.execute('''
        CREATE TABLE Game (game_id integer NOT NULL CONSTRAINT Game_pk PRIMARY KEY,
                           name text NOT NULL UNIQUE,
                           description text NOT NULL,
                           fps boolean NOT NULL DEFAULT 0,
                           action boolean NOT NULL DEFAULT 0,
                           adventure boolean NOT NULL DEFAULT 0,
                           puzzle boolean NOT NULL DEFAULT 0,
                           racing boolean NOT NULL DEFAULT 0,
                           simulation boolean NOT NULL DEFAULT 0,
                           rpg boolean NOT NULL DEFAULT 0,
                           sports boolean NOT NULL DEFAULT 0,
                           tps boolean NOT NULL DEFAULT 0,
                           rts boolean NOT NULL DEFAULT 0,
                           strategy boolean NOT NULL DEFAULT 0);
        ''')

        cursor.execute('''
        CREATE TABLE GameTable (uid integer NOT NULL,
                                game_id integer NOT NULL,
                                CONSTRAINT GameTable_pk PRIMARY KEY (uid,game_id)
                                FOREIGN KEY (uid) REFERENCES Login(uid)
                                FOREIGN KEY (game_id) REFERENCES Game(game_id));
        ''')

        cursor.execute('''
        CREATE TABLE ContactInfo (uid integer NOT NULL CONSTRAINT ContactInfo_pk PRIMARY KEY,
                                  facebook text,
                                  twitter text,
                                  reddit text,
                                  google text,
                                  skype text,
                                  xboxlive text,
                                  psn text,
                                  nintendo text,
                                  steam text,
                                  FOREIGN KEY (uid) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE FriendTable (uid integer NOT NULL,
                                  friend_uid text NOT NULL,
                                  CONSTRAINT FriendTable_pk PRIMARY KEY (uid,friend_uid)
                                  FOREIGN KEY (uid) REFERENCES Login(uid)
                                  FOREIGN KEY (friend_uid) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE Groups (group_id integer NOT NULL CONSTRAINT Groups_pk PRIMARY KEY,
                             temp_group boolean NOT NULL,
                             game_id integer NOT NULL,
                             current_size integer NOT NULL,
                             creator_id integer NOT NULL,
                             expire_time datetime,
                             pub_group boolean NOT NULL,
                             type text,
                             name text,
                             description text,
                             console text NOT NULL,
                             FOREIGN KEY (game_id) REFERENCES Game(game_id)
                             FOREIGN KEY (creator_id) REFERENCES Login(uid) );
        ''')

        cursor.execute('''
        CREATE TABLE BlockList (group_id integer NOT NULL,
                                uid integer NOT NULL,
                                CONSTRAINT BlockList_pk PRIMARY KEY (group_id,uid)
                                FOREIGN KEY (group_id) REFERENCES Groups(group_id)
                                FOREIGN KEY (uid) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE AdminList (group_id integer NOT NULL,
                                uid integer NOT NULL,
                                CONSTRAINT BlockList_pk PRIMARY KEY (group_id,uid)
                                FOREIGN KEY (group_id) REFERENCES Groups(group_id)
                                FOREIGN KEY (uid) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE Privacy (uid integer NOT NULL CONSTRAINT Privacy_pk PRIMARY KEY,
                              facebook boolean,
                              twitter boolean,
                              reddit boolean,
                              google boolean,
                              skype boolean,
                              xboxlive boolean,
                              psn boolean,
                              nintendo boolean,
                              steam boolean,
                              FOREIGN KEY (uid) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE Console (game_id integer NOT NULL CONSTRAINT Console_pk PRIMARY KEY,
                              xbox360 boolean NOT NULL DEFAULT 0,
                              ps3 boolean NOT NULL DEFAULT 0,
                              ps4 boolean NOT NULL DEFAULT 0,
                              xbox1 boolean NOT NULL DEFAULT 0,
                              wii boolean NOT NULL DEFAULT 0,
                              wiiu boolean NOT NULL DEFAULT 0,
                              psp boolean NOT NULL DEFAULT 0,
                              nds boolean NOT NULL DEFAULT 0,
                              pc boolean NOT NULL DEFAULT 0,
                              FOREIGN KEY (game_id) REFERENCES Game(game_id));
        ''')

        cursor.execute('''
        CREATE TABLE GroupTable (uid integer NOT NULL,
                                 group_id integer NOT NULL,
                                 CONSTRAINT GroupTable_pk PRIMARY KEY (uid,group_id)
                                 FOREIGN KEY (uid) REFERENCES Login(uid)
                                 FOREIGN KEY (group_id) REFERENCES Groups(group_id));
        ''')

        cursor.execute('''
        CREATE TABLE Messages (message_id integer NOT NULL CONSTRAINT Messages_pk PRIMARY KEY,
                               sender_id integer NOT NULL,
                               receiver_id integer NOT NULL,
                               message text NOT NULL,
                               FOREIGN KEY (sender_id) REFERENCES Login(uid)
                               FOREIGN KEY (receiver_id) REFERENCES Login(uid));
        ''')

        cursor.execute('''
        CREATE TABLE GroupInvite (invite_id integer NOT NULL CONSTRAINT GroupInvite_pk PRIMARY KEY,
                                  sender_id integer NOT NULL,
                                  receiver_id integer NOT NULL,
                                  group_id integer NOT NULL,
                                  FOREIGN KEY (sender_id) REFERENCES Login(uid)
                                  FOREIGN KEY (receiver_id) REFERENCES Login(uid)
                                  FOREIGN KEY (group_id) REFERENCES Groups(group_id));
        ''')

        conn.commit()
        conn.close()

        print("database initialized!")

    # dbConnection
    @staticmethod
    def populateDB():
        # connect to or create db file
        conn = sqlite3.connect(dbFile)
        cursor = conn.cursor()

        LoginScreen.insertUser("test1@mail.com", "test_user1", "test123", dbFile)
        LoginScreen.insertUser("test2@mail.com", "test_user2", "test123", dbFile)
        LoginScreen.insertUser("test3@mail.com", "test_user3", "test123", dbFile)
        LoginScreen.insertUser("test4@mail.com", "test_user4", "test123", dbFile)
        LoginScreen.insertUser("test5@mail.com", "test_user5", "test123", dbFile)

        cursor.execute('''
        INSERT INTO Game ('name','description','fps','action') VALUES
        ('Halo 3', '3rd game of Halo Franchise', 1, 1);
        ''')

        cursor.execute('''
        INSERT INTO Console ('game_id', 'xbox360') VALUES
        (1,1);
        ''')

        cursor.execute('''
        INSERT INTO Game ('name','description','rts','strategy') VALUES
        ('StarCraft2', 'Sequel to Broodwar', 1, 1);
        ''')

        cursor.execute('''
        INSERT INTO Console ('game_id', 'pc') VALUES
        (2,1);
        ''')

        cursor.execute('''
        INSERT INTO Game ('name','description','rpg') VALUES
        ('Runescape', 'Old rpg', 1);
        ''')

        cursor.execute('''
        INSERT INTO Console ('game_id', 'pc') VALUES
        (3,1);
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,1,1,2,1,'Competitive','Test Group 1', 'This is a description', 'Xbox 360');
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,1,1,2,1,'Casual','Test Group 2', 'This is a description', 'Xbox 360');
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,2,1,1,1,'Competitive','Test Group 3', 'This is a description', 'PC');
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,2,1,1,1,'Casual','Test Group 4', 'This is a description', 'PC');
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,3,1,3,1,'Competitive','Test Group 5', 'This is a description', 'PC');
        ''')

        cursor.execute('''
        INSERT INTO Groups ('temp_group', 'game_id', 'current_size', 'creator_id', 'pub_group', 'type', 'name', 'description', 'console')
        VALUES (0,3,1,3,1,'Casual','Test Group 6', 'This is a description', 'PC');
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (1,2);
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (2,1);
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (1,3);
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (3,1);
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (1,4);
        ''')

        cursor.execute('''
        INSERT INTO FriendTable
        VALUES (4,1);
        ''')

        conn.commit()
        conn.close()

    def build(self):
        # check if .db file exists, if not create it
        if not os.path.isfile(dbFile):
            self.initDatabase()
            self.populateDB()

        r = RootManager()
        self.root = r
        return r

if __name__ == '__main__':
    RootApp().run()
