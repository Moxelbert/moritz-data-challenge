from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import json
import datetime
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from pydantic import BaseModel


# JWT Config
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Start FastAPI app
app = FastAPI()

# Database simulation for users (in practice, query your database)
#users_db = {"user1": {"username": "user1", "password": "1900Juenter"}}

# OAuth2PasswordBearer is used to extract the token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Define the allowed origins (you can allow specific domains or all)
origins = [
    "http://localhost:3000",  # React app URL
    "http://localhost:8000",  # FastAPI itself (optional)
    "https://react-app-moritz-360127904619.europe-west3.run.app"
]



class DataItem(BaseModel):
    time_stamp: str
    data: list[float]

# Define the request body model for the login
class LoginRequest(BaseModel):
    username: str
    password: str

# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# JWT utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Login route: Validates user credentials and returns a JWT
@app.post("/login/")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    print(f'here comes the user: {login_request.username}')
    user = db.query(User).filter(User.username == login_request.username).first()
    if user is None or user.password != login_request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Login route: Validates user credentials and returns a JWT
'''@app.post("/login/")
async def login(user: User):
    if user.username not in users_db or users_db[user.username]["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}'''

# Protected route: Requires JWT token to access
@app.get("/protected/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "You are authorized", "user": payload["sub"]}

# GCP Storage Bucket details
BUCKET_NAME = 'moritz-eraneos-challenge'

# Function to upload a JSON file to Google Cloud Storage
def upload_json_to_gcp(json_data, file_name):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(json.dumps(json_data), content_type='application/json')
    return True

# POST route to receive JSON and upload it to GCP
@app.post("/upload/")
async def upload_json(data: DataItem, token: str = Depends(oauth2_scheme)):
    # Validate the token first
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        file_name = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_data = data.dict()
        upload_json_to_gcp(json_data, file_name)
        return {"status": "success", "file_name": file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"Request from Origin: {origin}")
    response = await call_next(request)
    print(f"Response Headers: {response.headers}")
    return response