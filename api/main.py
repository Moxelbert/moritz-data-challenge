from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile
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
from pydantic import BaseModel, ValidationError


# JWT Config
SECRET_KEY = "blablabla" #your_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI()

# OAuth2PasswordBearer is used to extract the token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# where can the API take requests from?
origins = [
    "http://localhost:3000",  # for local development
    "https://react-app-moritz-360127904619.europe-west3.run.app"
]

class DataItem(BaseModel):
    time_stamp: str
    data: list[float]

# request body model for the login
class LoginRequest(BaseModel):
    username: str
    password: str

# pydantic model for validating JSON file content
class UploadedData(BaseModel):
    timestamp: str
    data: list[float]


# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# GCS bucket details
BUCKET_NAME = 'moritz-eraneos-challenge'

# jwt utility functions
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

def get_current_user(db, login_request: LoginRequest):
    return db.query(User).filter(User.username == login_request.username).first()

# Login route: validates user credentials and returns a jwt
@app.post("/login/")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    print(f'here comes the user: {login_request.username}')
    user = get_current_user(db, login_request)
    #db.query(User).filter(User.username == login_request.username).first()
    if user is None or user.password != login_request.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate jtw token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route that requires the jwt token to access
@app.get("/protected/")
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "You are authorized", "user": payload["sub"]}

# Function to upload a JSON file to GCS
def upload_json_to_gcp(data, file_name, is_file=False):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    
    if is_file:
        # If the data is a file, use upload_from_file
        with open(data, 'rb') as file_data:
            blob.upload_from_file(file_data, content_type='application/json')
    else:
        # If the data is a JSON string, upload it as string content
        blob.upload_from_string(json.dumps(data), content_type='application/json')
    
    return True

# POST route to receive json and upload it to GCS
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

# Function to upload the file directly to GCS
def upload_file_to_gcp(
    file: UploadFile, destination_blob_name: str):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # upload file directly without loading it into memory
    blob.upload_from_file(file.file, content_type=file.content_type)
    return True

@app.post("/upload-json/")
async def upload_large_json(
    file: UploadFile = File(...), 
    token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        upload_file_to_gcp(file, file.filename)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"Request from Origin: {origin}")
    response = await call_next(request)
    print(f"Response Headers: {response.headers}")
    return response