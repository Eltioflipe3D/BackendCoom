import os
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

import pymongo
import uvicorn
from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from bson.objectid import ObjectId

import jwt


# Load environment variables first
load_dotenv()

#CONSTANTS
JWT_SECRET = os.getenv("JWT_SECRET")


class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=12, max_length=64)

#just username + pass for login
class loginUser(BaseModel):
    username: str
    password: str


#connect stuff

client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]

#makes the beatiful beatiful app
coom = FastAPI()
bearer = HTTPBearer()

#hash passwords stuff
#hashed password all fancy
def hashPassword(password: str) -> bytes:
    passwordBytes = password.encode("utf-8")

    #echale sal brooo q este eso ahi aletoriecito
    sal = bcrypt.gensalt()

    return bcrypt.hashpw(passwordBytes,sal)

#true or false
def verifyPassword(password: str, hashed: bytes) -> bool:
    passwordBytes = password.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashed)


#DEPENDS -> asks for token and then gives the sweet sweet whole user
def getCurrentUser(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        decoded = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid or expired token")

    user = db.users.find_one({"_id": ObjectId(decoded["_id"])})
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user




#Register an user
@coom.post("/register")
def register(user: User):

    userExists = db.users.find_one({"username": user.username})

    if userExists:
        return {"message": "user already exists"}
    else:
        db.users.insert_one(
            {
                "username": user.username,
                "email": user.email,
                "password": hashPassword(user.password),

                #Various stats and stuff, add here for greatness

                "winCount": 0,
                "monsterKills": 0,
                "bossKills": 0,
                "collectablesFound": [],
                "bestTime": 0,
                "deaths": 0,
                "dateJoined": datetime.now(),

                #current save file
                "saveLevel": "",
                "saveCurrentHealth": 0,
                "saveMaxHealth": 0,
                "saveWeapons": [],
                "saveUpgrades": [],


            }
        )
        return {"message": "user created"}


#Login an user - returns JWT token
@coom.post("/login")
def login(user: loginUser):
    token = None
    dbUser = db.users.find_one({"username": user.username})

    if dbUser:
        if verifyPassword(user.password, dbUser["password"]):
            # Create JWT token
            token = jwt.encode({
                "_id": str(dbUser["_id"])
            }, JWT_SECRET, algorithm="HS256")

    return {"token": token}


#get current user info
#Requires token
@coom.get("/me")
def me(dbUser: dict = Depends(getCurrentUser)):
    return {
        "username": dbUser["username"],
        "email": dbUser["email"],
        "profilePic": dbUser.get("profilePic"),
        "winCount": dbUser.get("winCount"),
        "monsterKills": dbUser.get("monsterKills"),
        "bossKills": dbUser.get("bossKills"),
        "collectablesFound": dbUser.get("collectablesFound"),
        "bestTime": dbUser.get("bestTime"),
        "deaths": dbUser.get("deaths"),
        "dateJoined": dbUser.get("dateJoined"),
        "saveLevel": dbUser.get("saveLevel"),
        "saveCurrentHealth": dbUser.get("saveCurrentHealth"),
        "saveMaxHealth": dbUser.get("saveMaxHealth"),
        "saveWeapons": dbUser.get("saveWeapons"),
        "saveUpgrades": dbUser.get("saveUpgrades"),
    }




#Change (or set) a user's profile pic
#Requires token
@coom.post("/pfp")
async def changePfp(
    file: UploadFile,
    dbUser: dict = Depends(getCurrentUser)
):
    image = await file.read()

    # Create the profilepics directory if it doesn't exist
    os.makedirs("profilepics", exist_ok=True)

    # Get file extension from uploaded file
    filename = os.path.join("profilepics", f"{dbUser['username']}_pfp.png")

    # Remove existing file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, "wb") as f:
        f.write(image)

    db.users.find_one_and_update({"_id": dbUser["_id"]}, {"$set": {"profilePic": filename}})
    return {"message": "profile picture updated"}

    



#get an user pfp
@coom.get("/pfp/{username}")
async def getPfp(username: str):
    dbUser = db.users.find_one({"username": username})

    if dbUser and dbUser.get("profilePic") and os.path.exists(dbUser["profilePic"]):
        return FileResponse(dbUser["profilePic"])
    else:
        return {"message": "user not found or has no pfp"}


#patch a single field, great for updating values and adding new ones, amazing shi ngl
#Requires token
@coom.patch("/me/updatefield")
def updateUserInfo(fieldName: str, fieldValue: str, dbUser: dict = Depends(getCurrentUser)):
    db.users.find_one_and_update({"_id": dbUser["_id"]}, {"$set": {fieldName: fieldValue}})
    return {"message": True}



#deprecated, cuz no checking if field exists is easier and more fun
#patch a single field, great for updating values
#Requires token
#@coom.patch("/me/updatefield")
#def updateUserInfo(fieldName: str, fieldValue: str, dbUser: dict = Depends(getCurrentUser)):
    user = db.users.find_one({"_id": dbUser["_id"]})
    if fieldName in user:
        db.users.find_one_and_update({"_id": dbUser["_id"]}, {"$set": {fieldName: fieldValue}})
        return {"message": True}
    else:
        return {"message": False}



#get rankings
#time in seconds
@coom.get("/rankings/{num_rankings}")
def getRankings(num_rankings: int):
    rankings = db.rankings.find().sort("bestTime", 1).limit(num_rankings)
    rankings_list = []
    for ranking in rankings:
        ranking_dict = {
            "username": ranking["username"],
            "bestTime": ranking["bestTime"],
            "difficulty": ranking["difficulty"],
        }
        rankings_list.append(ranking_dict)
    return rankings_list


#post new ranking
#time in seconds
#Requires token
@coom.post("/rankings")
def postRanking(time: int, difficulty: str, dbUser: dict = Depends(getCurrentUser)):
    db.rankings.insert_one({
        "username": dbUser["username"],
        "bestTime": time,
        "difficulty": difficulty,
    })
    return {"message": True}





#this runs the whole program
def main():
    uvicorn.run(coom, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
    


