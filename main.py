import os
from dotenv import load_dotenv

import pymongo
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


#connect stuff

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]

#makes the beatiful beatiful app
coom = FastAPI()


#user basemodel, all fields are optional cuz lowk easier
class User(BaseModel):
    username: str = None
    email: str = None
    password: str = None


#Register an user
@coom.post("/register")
def register(user: User):

    userExists = db.users.find_one({"username": user.username})

    if userExists:
        return {"message": "user already exists"}
    else:
        db.users.insert_one({"username": user.username, "email": user.email, "password": user.password})
        return {"message": "user created"}



#Login an user, should return token in the future 
#IMPORTANT TO CHANGE THIS LATER
@coom.post("/login")
def login(user: User):
    dbUser = db.users.find_one({"username": user.username})
    print(dbUser)

    if dbUser:
        if user.password == dbUser["password"]:
            dbUser["_id"] = None
            return dbUser
        else:
            return {"login": False}
    else:
        return {"login": False}




def main():
    uvicorn.run(coom, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
    


