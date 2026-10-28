import os
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

load_dotenv()

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
        db.users.insert_one({"username": user.username, "email": user.email, "password": hashPassword(user.password)})
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



#Change (or set) a user's profile pic
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
        return {"message": "user not found"}

#get current user info
@coom.get("/me")
def me(dbUser: dict = Depends(getCurrentUser)):
    return {"username": dbUser["username"], "email": dbUser["email"]}




#this runs the whole program
def main():
    uvicorn.run(coom, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
    


