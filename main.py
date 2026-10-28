import os
import bcrypt
from dotenv import load_dotenv

import pymongo
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr


#connect stuff

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]

#makes the beatiful beatiful app
coom = FastAPI()


#hash passwords stuff
#hashed password all fancy
def hashPassword(password: str):
    passwordBytes = password.encode("utf-8")

    #echale sal brooo q este eso ahi aletoriecito
    sal = bcrypt.gensalt()

    return bcrypt.hashpw(passwordBytes,sal)

#true or false
def verifyPassword(password, hashed):
    passwordBytes = password.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashed)



#user basemodel
class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=12, max_length=64)

#just username + pass for login
class loginUser(BaseModel):
    username: str
    password: str


#Register an user
@coom.post("/register")
def register(user: User):

    userExists = db.users.find_one({"username": user.username})

    if userExists:
        return {"message": "user already exists"}
    else:
        db.users.insert_one({"username": user.username, "email": user.email, "password": hashPassword(user.password)})
        return {"message": "user created"}



#Login an user, should return token in the future 
#IMPORTANT TO CHANGE THIS LATER
@coom.post("/login")
def login(user: loginUser):
    dbUser = db.users.find_one({"username": user.username})

    if dbUser:
        if verifyPassword(user.password, dbUser["password"]):
            return {"username": dbUser["username"],
                    "email": dbUser["email"]}
        else:
            return {"login": False}
    else:
        return {"login": False}






#this runs the whole program u dumbass
def main():
    uvicorn.run(coom, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
    


