from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field

import sqlite3
import db
from db import has_user_id

APP_NAME: str = "User & Groups API"
APP_DESCRIPTION: str = "User & Groups API allows you to manage users, groups and their association."
APP_VERSION: str = "1.0.0"

TAG_USERS: str = "Users"
TAG_GROUPS: str = "Groups"
TAG_RELATIONS: str = "Users and Groups Relations"

TAGS_METADATA = [
    dict(
        name = TAG_USERS,
        description = "Operations with Users, DELETE request will effect Relations"
    ),
    dict(
        name = TAG_GROUPS,
        description = "Operations with Groups for Users, DELETE request will effect Relations"
    ),
    dict(
        name = TAG_RELATIONS,
        description = "Operations with Relations between Users and Groups"
    )
]
app = FastAPI(
            title = APP_NAME,
            description = APP_DESCRIPTION,
            version = APP_VERSION,
            openapi_tags = TAGS_METADATA
            )

@app.on_event("startup")
async def startup_event():
    try:
        db.init_db()
    except sqlite3.Error as error:
        raise HTTPException(status_code = 500, detail = f"Database initialization failed: {error}")

class User(BaseModel):
    username:   str         = Field(...,  example = "JDoe")
    first_name: str | None  = Field(None, example = "John")
    last_name:  str | None  = Field(None, example = "Doe")
    email:      str | None  = Field(None, example = "JohnnyDoe@gmail.com")

class UserUpdate(BaseModel):
    user_id:    int         = Field(...,  example = "10")
    username:   str | None  = Field(None, example = "JDoe")
    first_name: str | None  = Field(None, example = "John")
    last_name:  str | None  = Field(None, example = "Doe")
    email:      str | None  = Field(None, example = "JohnnyDoe@gmail.com")

class UserDB(User):
    user_id: int = Field(..., example = "10")

class Group(BaseModel):
    name:        str        = Field(...,  example = "SysAdmin")
    description: str | None = Field(None, example = "Management and maintenance of system infrastructure. Full administrative rights.")

class GroupUpdate(BaseModel):
    group_id:    int        = Field(..., example = "7")
    name:        str | None = Field(None,  example = "SysAdmin")
    description: str | None = Field(None, example = "Management and maintenance of system infrastructure. Full administrative rights.")

class GroupDB(Group):
    group_id: int = Field(..., example = "7")

class Relation(BaseModel):
    user_id:  int = Field(..., example = "10")
    group_id: int = Field(..., example = "7")

class RelationDetailedDB(BaseModel):
    username:   str = Field(..., example = "JDoe")
    group_name: str = Field(..., example = "SysAdmin")
    user_id:    int = Field(..., example = "10")
    group_id:   int = Field(..., example = "7")

@app.get("/users/", tags = [TAG_USERS], response_model = list[UserDB])
async def get_all_users():
    """Returns a list of all users and their information from the database"""

    db_users: list[tuple[int, str, str, str, str]] = db.get_all_users()
    if not db_users:
        raise HTTPException(status_code = 404, detail = "No users found.")

    users_list: list[UserDB] = []
    for user_tuple in db_users:
        user = UserDB(
            user_id     = user_tuple[0],
            username    = user_tuple[1],
            first_name  = user_tuple[2],
            last_name   = user_tuple[3],
            email       = user_tuple[4]
        )
        users_list.append(user)

    return users_list

@app.get("/users/{user_id}", tags = [TAG_USERS], response_model = UserDB)
async def get_user(user_id: int):
    """Returns a specific user with a given UserID and their information from the database"""

    db_user: tuple[int, str, str, str, str] = db.get_user(user_id)

    if not db_user:
        raise HTTPException(status_code = 404, detail = f"User with User ID {user_id} not found.")

    user = UserDB(
        user_id     = db_user[0],
        username    = db_user[1],
        first_name  = db_user[2],
        last_name   = db_user[3],
        email       = db_user[4]
    )

    return user
@app.post("/users/", tags = [TAG_USERS], response_model = UserDB)
async def add_user(user: User = Body(...)):
    """Adds a new user to the database. If successful, will return the new data, including an auto-generated UserID"""

    if db.has_username(user.username):
        raise HTTPException(status_code = 400, detail = f"User with Username {user.username} already exists.")
    if db.has_email(user.email):
        raise HTTPException(status_code = 400, detail = f"User with Email {user.email} already exists.")

    db.add_user(user.username, user.first_name, user.last_name, user.email)

    #Return added data from DB
    db_new_user: tuple[int, str, str, str, str] = db.get_user_via_name(user.username)
    if not db_new_user:
        raise HTTPException(status_code=404, detail=f"Failed to create new user")

    new_user = UserDB(
        user_id     = db_new_user[0],
        username    = db_new_user[1],
        first_name  = db_new_user[2],
        last_name   = db_new_user[3],
        email       = db_new_user[4]
    )

    return new_user

@app.patch("/users/{user_id}", tags = [TAG_USERS], response_model = UserDB)
async def update_user(user_update: UserUpdate):
    """Updates an existing user in the database. If successful, will return the new updated data"""

    if not db.has_user_id(user_update.user_id):
        raise HTTPException(status_code = 404, detail = f"User with User ID {user_update.user_id} not found.")

    columns: list = []
    values: list = []
    if user_update.username != None:
        columns.append("Username = ?")
        values.append(user_update.username)
    if user_update.first_name != None:
        columns.append("FirstName = ?")
        values.append(user_update.first_name)
    if user_update.last_name != None:
        columns.append("LastName = ?")
        values.append(user_update.last_name)
    if user_update.email != None:
        columns.append("Email = ?")
        values.append(user_update.email)

    if len(values) == 0:
        raise HTTPException(status_code = 400, detail = "No update data was provided.")

    values.append(user_update.user_id)
    db.update_user(columns, values)

    db_updated_user: tuple[int, str, str, str, str] = db.get_user(user_update.user_id)
    if not db_updated_user:
        raise HTTPException(status_code=404, detail=f"Failed to update the user with User ID {user_update.user_id}")

    updated_user = UserDB(
        user_id     = db_updated_user[0],
        username    = db_updated_user[1],
        first_name  = db_updated_user[2],
        last_name   = db_updated_user[3],
        email       = db_updated_user[4]
    )

    return updated_user

@app.delete("/users/{user_id}", tags = [TAG_USERS])
async def delete_user(user_id: int):
    """Deletes a specific user with a given UserID from the database"""

    if not db.has_user_id(user_id):
        raise HTTPException(status_code = 404, detail = f"User with User ID {user_id} not found.")

    if db.has_user_relation(user_id):
        db.delete_user_relations(user_id)

    db.delete_user(user_id)
    return {f"User with User ID {user_id} successfully deleted."}

@app.get("/groups/", tags = [TAG_GROUPS], response_model = list[GroupDB])
async def get_all_groups():
    """Returns a list of all groups and their information from the database"""

    db_groups: list[tuple[int, str, str]] = db.get_all_groups()
    if not db_groups:
        raise HTTPException(status_code = 404, detail = "No groups found.")

    groups_list: list[GroupDB] = []
    for group_tuple in db_groups:
        group = GroupDB(
            group_id    = group_tuple[0],
            name        = group_tuple[1],
            description = group_tuple[2]
        )
        groups_list.append(group)

    return groups_list

@app.get("/groups/{group_id}", tags = [TAG_GROUPS], response_model = GroupDB)
async def get_group(group_id: int):
    """Returns a specific group with a given GroupID and its information from the database"""

    db_group: tuple[int, str, str] = db.get_group(group_id)
    if not db_group:
        raise HTTPException(status_code = 404, detail = f"Group with Group ID {group_id} not found.")

    group = GroupDB(
        group_id    = db_group[0],
        name        = db_group[1],
        description = db_group[2]
    )

    return group

@app.post("/groups/", tags = [TAG_GROUPS])
async def add_group(group: Group = Body(...)):
    """Adds a new group to the database. If successful, will return the new data, including an auto-generated GroupID"""

    if db.has_group_name(group.name):
        raise HTTPException(status_code = 400, detail = f"Group with Name {group.name} already exists.")

    db.add_group(group.name, group.description)
    # Return added data from DB
    db_new_group: tuple[int, str, str] = db.get_group_via_name(group.name)
    if not db_new_group:
        raise HTTPException(status_code = 404, detail = f"Failed to create new user")

    new_group = GroupDB(
        group_id    = db_new_group[0],
        name        = db_new_group[1],
        description = db_new_group[2]
    )

    return new_group

@app.patch("/groups/{group_id}", tags = [TAG_GROUPS], response_model = GroupDB)
async def update_group(group_update: GroupUpdate):
    """Updates an existing group in the database. If successful, will return the new updated data"""

    if not db.has_group_id(group_update.group_id):
        raise HTTPException(status_code = 404, detail = f"Group with ID {group_update.group_id} not found.")

    columns: list = []
    values: list = []
    if group_update.name != None: #None or len() > 0? None will make "" pass
        columns.append("Name = ?")
        values.append(group_update.name)
    if group_update.description != None:
        columns.append("Description = ?")
        values.append(group_update.description)

    if len(values) == 0:
        raise HTTPException(status_code = 400, detail = "No update data was provided.")

    values.append(group_update.group_id)
    db.update_group(columns, values)

    db_updated_group: tuple[int, str, str] = db.get_group(group_update.group_id)
    if not db_updated_group:
        raise HTTPException(status_code=404, detail=f"Failed to update new user")

    updated_group = GroupDB(
        group_id    = db_updated_group[0],
        name        = db_updated_group[1],
        description = db_updated_group[2],
    )

    return updated_group


@app.delete("/groups/{group_id}", tags = [TAG_GROUPS])
async def delete_group(group_id: int):
    """Deletes a specific user with a given UserID from the database"""

    if not db.has_group_id(group_id):
        raise HTTPException(status_code = 404, detail = f"Group with ID {group_id} not found.")

    if db.has_group_relation(group_id):
        db.delete_group_relations(group_id)

    db.delete_group(group_id)
    return {f"Group with Group ID {group_id} successfully deleted."}

@app.get("/relations/", tags = [TAG_RELATIONS], response_model = list[RelationDetailedDB])
async def get_all_relations():
    db_relations: list[tuple[str, str, int, int]] = db.get_all_relations()

    if not db_relations:
        raise HTTPException(status_code = 404, detail = "No relations found.")

    relations_list: list[RelationDetailedDB] = []
    for relation_tuple in db_relations:
        relation = RelationDetailedDB(
            username    = relation_tuple[0],
            group_name  = relation_tuple[1],
            user_id     = relation_tuple[2],
            group_id    = relation_tuple[3]
        )
        relations_list.append(relation)

    return relations_list

@app.get("/relations/user/{user_id}", tags = [TAG_RELATIONS], response_model = list[RelationDetailedDB])
async def get_user_relations(user_id: int):
    db_relations: list[tuple[str, str, int, int]] = db.get_user_relations(user_id)

    if not db_relations:
        raise HTTPException(status_code = 404, detail = f"No relations found for user with User ID {user_id}.")

    relations_list: list[RelationDetailedDB] = []
    for relation_tuple in db_relations:
        relation = RelationDetailedDB(
            username    = relation_tuple[0],
            group_name  = relation_tuple[1],
            user_id     = relation_tuple[2],
            group_id    = relation_tuple[3]
        )
        relations_list.append(relation)

    return relations_list

@app.get("/relations/group/{group_id}", tags = [TAG_RELATIONS], response_model = list[RelationDetailedDB])
async def get_user_relations(group_id: int):
    db_relations: list[tuple[str, str, int, int]] = db.get_group_relations(group_id)

    if not db_relations:
        raise HTTPException(status_code = 404, detail = f"No relations found for group with Group ID {user_id}.")

    relations_list: list[RelationDetailedDB] = []
    for relation_tuple in db_relations:
        relation = RelationDetailedDB(
            username    = relation_tuple[0],
            group_name  = relation_tuple[1],
            user_id     = relation_tuple[2],
            group_id    = relation_tuple[3]
        )
        relations_list.append(relation)

    return relations_list

@app.post("/relations/", tags = [TAG_RELATIONS], response_model = Relation)
async def add_relation(relation: Relation = Body(...)):
    """Adds a new user and group relation to the database. If successful, will return the new data"""

    if db.has_relation(relation.user_id, relation.group_id):
        raise HTTPException(status_code = 400, detail = "Relation between User and Group already exists")

    if not db.has_user_id(relation.user_id):
        raise HTTPException(status_code = 404, detail = f"User with ID {relation.user_id} not found.")

    if not db.has_group_id(relation.group_id):
        raise HTTPException(status_code = 404, detail = f"Group with ID {relation.group_id} not found.")

    db.add_relation(relation.user_id, relation.group_id)

    db_new_relation: tuple[int, int] = db.get_relation(relation.user_id, relation.group_id)
    if not db_new_relation:
        raise HTTPException(status_code=404, detail=f"Failed to create new relation")

    new_relation = Relation(
        user_id  = db_new_relation[0],
        group_id = db_new_relation[1]
    )

    return new_relation
@app.delete("/relations/", tags = [TAG_RELATIONS])
async def delete_relation(relation: Relation = Body(...)):
    """Deletes a specific user with a given UserID and GroupID from the database"""

    if not db.has_relation(relation.user_id, relation.group_id):
        raise HTTPException(status_code = 404, detail = "Relation between User and Group not found")

    db.delete_relation(relation.user_id, relation.group_id)
    return {f"Relation with User ID {relation.user_id} and Group ID {relation.group_id} successfully deleted."}

@app.delete("/relations/user/{user_id}", tags = [TAG_RELATIONS])
async def delete_user_relations(user_id: int):
    """Deletes all relations with a given UserID from the database"""

    if not db.has_user_relation(user_id):
        raise HTTPException(status_code = 404, detail = f"No relations found for User ID {user_id}.")

    db.delete_user_relations(user_id)
    return {f"All relations with User ID {user_id} successfully deleted."}

@app.delete("/relations/group/{group_id}", tags = [TAG_RELATIONS])
async def delete_group_relations(group_id: int):
    """Deletes all relations with a given GroupIP from the database"""

    if not db.has_group_relation(group_id):
        raise HTTPException(status_code = 404, detail = f"No relations found for Group ID {group_id}.")

    db.delete_group_relations(group_id)
    return {f"All relations with Group ID {group_id} successfully deleted."}