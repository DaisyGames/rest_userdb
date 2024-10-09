import sqlite3
from sqlite3 import Connection, Cursor

con: Connection = sqlite3.connect(':memory:')
cur: Cursor = con.cursor()

def init_db() -> None:
    #Init in-memory DB
    con.execute("PRAGMA foreign_keys = ON")

    cur.execute("""
        CREATE TABLE Users (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT NOT NULL,
            FirstName TEXT,
            LastName TEXT,
            Email TEXT NOT NULL
            )
        """)

    cur.execute("""
        CREATE TABLE UserGroups (
            GroupID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Description TEXT
            )
    """)

    cur.execute("""
        CREATE TABLE Relations (
            UserID INTEGER,
            GroupID INTEGER,
            PRIMARY KEY (UserID, GroupID),
            FOREIGN KEY (UserID) REFERENCES Users(UserID),
            FOREIGN KEY (GroupID) REFERENCES UserGroups(GroupID)
            )
    """)

    #Fake data for quick testing
    #Users
    # cur.execute("""
    # INSERT INTO Users (Username, FirstName, LastName, Email)
    # VALUES ("LMuoz", "Leon", "Muoz", "lmuuz@gmail.com")
    # """)
    #
    # cur.execute("""
    #     INSERT INTO Users (Username, FirstName, LastName, Email)
    #     VALUES ("MSkeldon", "Mona", "Skeldon", "mskelly@gmail.com")
    # """)
    #
    # cur.execute("""
    #     INSERT INTO Users (Username, FirstName, LastName, Email)
    #     VALUES ("TTyler", "Tracy", "Tyler", "teetee@hotmail.com")
    # """)
    #
    # cur.execute("""
    #     INSERT INTO Users (Username, FirstName, LastName, Email)
    #     VALUES ("GDyxon", "George", "Dyxon", "GDXN@hotmail.com")
    #     """)
    # #Groups
    # cur.execute("""
    #     INSERT INTO UserGroups (Name, Description)
    #     VALUES ("Admin", "Administrative group, has all rights")
    # """)
    #
    # cur.execute("""
    #     INSERT INTO UserGroups (Name, Description)
    #     VALUES ("CC0", "Call Center Passive")
    # """)
    # cur.execute("""
    #     INSERT INTO UserGroups (Name, Description)
    #     VALUES ("CC1", "Call Center Active")
    # """)
    # #Relations
    # cur.execute("""
    # INSERT INTO Relations (UserID, GroupID)
    # VALUES (1, 1)
    # """)
    #
    # cur.execute("""
    # INSERT INTO Relations (UserID, GroupID)
    # VALUES (2, 2)
    # """)
    #
    # cur.execute("""
    # INSERT INTO Relations (UserID, GroupID)
    # VALUES (3, 3)
    # """)
    #
    # cur.execute("""
    #     INSERT INTO Relations (UserID, GroupID)
    #     VALUES (4, 2)
    # """)
    #
    # cur.execute("""
    #     INSERT INTO Relations (UserID, GroupID)
    #     VALUES (4, 3)
    # """)

#User functions
def get_all_users() -> list[tuple[int, str, str, str, str]]:
    cur.execute("SELECT UserID, Username, FirstName, LastName, Email FROM Users")
    return cur.fetchall()

def get_user(user_id: int) -> tuple[int, str, str, str, str]:
    cur.execute("SELECT UserID, Username, FirstName, LastName, Email FROM Users WHERE UserID = ?", (user_id,))
    return cur.fetchone()

def get_user_via_name(username: str) -> tuple[int, str, str, str, str]:
    cur.execute("SELECT UserID, Username, FirstName, LastName, Email FROM Users WHERE Username = ?", (username,))
    return cur.fetchone()

def has_user_id(user_id: int) -> bool:
    cur.execute("SELECT UserID FROM Users WHERE UserID = ?", (user_id,))
    return cur.fetchone() != None

def has_username(username: str) -> bool:
    cur.execute("SELECT UserID FROM Users WHERE Username = ?", (username,))
    return cur.fetchone() != None

def has_email(email: str) -> bool:
    cur.execute("SELECT UserID FROM Users WHERE Email = ?", (email,))
    return cur.fetchone() != None

def add_user(username: str, first_name: str, last_name: str, email: str) -> None:
    cur.execute("""
    INSERT INTO Users (Username, FirstName, LastName, Email)
    VALUES (?, ?, ?, ?)
    """, (username, first_name, last_name, email))
    con.commit()

def update_user(columns: list, values: list) -> None:
    query: str =  f"UPDATE Users SET {', '.join(columns)} WHERE UserID = ?"
    cur.execute(query, values)
    con.commit()

def delete_user(user_id: int) -> None:
    cur.execute("DELETE FROM Users WHERE UserID = ?", (user_id,))
    con.commit()

#Group funcs
def get_all_groups() -> list[tuple[int, str, str]]:
    cur.execute("SELECT GroupID, Name, Description FROM UserGroups")
    return cur.fetchall()

def get_group(group_id: int) -> tuple[int, str, str]:
    cur.execute("SELECT GroupID, Name, Description FROM UserGroups WHERE GroupID = ?", (group_id,))
    return cur.fetchone()

def get_group_via_name(name: str) -> tuple[int, str, str]:
    cur.execute("SELECT GroupID, Name, Description FROM UserGroups WHERE Name = ?", (name,))
    return cur.fetchone()

def has_group_name(name: str) -> bool:
    cur.execute("SELECT GroupID FROM UserGroups WHERE Name = ?", (name,))
    return cur.fetchone() != None

def has_group_id(group_id: int) -> bool:
    cur.execute("SELECT GroupID FROM UserGroups WHERE GroupID = ?", (group_id,))
    return cur.fetchone() != None

def add_group(name: str, description: str) -> None:
    cur.execute("""
    INSERT INTO UserGroups (Name, Description)
    VALUES (?, ?)
    """, (name, description))
    con.commit()

def update_group(columns: list, values: list):
    query: str =  f"UPDATE UserGroups SET {', '.join(columns)} WHERE GroupID = ?"
    cur.execute(query, values)
    con.commit()

def delete_group(group_id: int) -> None:
    cur.execute("DELETE FROM UserGroups WHERE GroupID = ?",  (group_id,))
    con.commit()

#Relation funcs
def get_all_relations() -> list[tuple[str, str, int, int]]:
    cur.execute("""
                SELECT Users.Username, UserGroups.Name ,Relations.UserID, Relations.GroupID
                FROM Relations
                JOIN Users      ON Relations.UserID = Users.UserID
                JOIN UserGroups ON Relations.GroupID = UserGroups.GroupID
                """)
    return cur.fetchall()

def get_user_relations(user_id: int) -> list[tuple[str, str, int, int]]:
    cur.execute("""
                SELECT Users.Username, UserGroups.Name ,Relations.UserID, Relations.GroupID
                FROM Relations
                JOIN Users      ON Relations.UserID = Users.UserID
                JOIN UserGroups ON Relations.GroupID = UserGroups.GroupID
                WHERE Relations.UserID = ?
                """, (user_id,))
    return cur.fetchall()

def get_group_relations(group_id: int) -> list[tuple[str, str, int, int]]:
    cur.execute("""
                SELECT Users.Username, UserGroups.Name ,Relations.UserID, Relations.GroupID
                FROM Relations
                JOIN Users      ON Relations.UserID = Users.UserID
                JOIN UserGroups ON Relations.GroupID = UserGroups.GroupID
                WHERE Relations.GroupID = ?
                """, (group_id,))
    return cur.fetchall()

def get_relation(user_id: int, group_id: int) -> tuple[int, int]:
    cur.execute("""
                SELECT UserID, GroupID
                FROM Relations
                WHERE UserID = ? AND GroupID = ?
                """, (user_id, group_id))
    return cur.fetchone()

def has_relation(user_id: int, group_id: int) -> bool:
    cur.execute("SELECT UserID FROM Relations WHERE UserID = ? AND GroupID = ?", (user_id, group_id))
    return cur.fetchone() != None

def has_user_relation(user_id: int) -> bool:
    cur.execute("SELECT UserID FROM Relations WHERE UserID = ?", (user_id,))
    return cur.fetchone() != None

def has_group_relation(group_id: int) -> bool:
    cur.execute("SELECT GroupID FROM Relations WHERE GroupID = ?", (group_id,))
    return cur.fetchone() != None

def add_relation(user_id: int, group_id: int) -> None:
    cur.execute("""
        INSERT INTO Relations (UserID, GroupID)
        VALUES (?, ?)
        """, (user_id, group_id))
    con.commit()

def delete_relation(user_id: int, group_id: int) -> None:
    cur.execute("DELETE FROM Relations WHERE UserID = ? AND GroupID = ?", (user_id, group_id))
    con.commit()

def delete_user_relations(user_id: int) -> None:
    cur.execute("DELETE FROM Relations WHERE UserID = ?", (user_id,))
    con.commit()

def delete_group_relations(group_id: int) -> None:
    cur.execute("DELETE FROM Relations WHERE GroupID = ?", (group_id,))
    con.commit()