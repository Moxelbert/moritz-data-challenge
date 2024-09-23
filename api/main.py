import json
import datetime
import os

from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIKey
from google.cloud import storage
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
from typing import List

from database import get_db
from models import User


# JWT Config
SECRET_KEY = os.getenv('API_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI(    
    title="Moritz API",
    description="This is a detailed description of my API.",
    version="1.0")

# OAuth2PasswordBearer is used to extract the token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# where can the API take requests from?
origins = [
    "http://localhost:3000",  # for local development
    "https://react-app-moritz-360127904619.europe-west3.run.app"
]

# define the expected format of the incoming JSONs data to be verified by Pydantic
class DataItem(BaseModel):
    time_stamp: str
    data: list[float]

# request body model for the login
class LoginRequest(BaseModel):
    username: str
    password: str

# Add CORS middleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("origin")
    print(f"Request from Origin: {origin}")
    response = await call_next(request)
    print(f"Response Headers: {response.headers}")
    return response

# GCS bucket details
BUCKET_NAME = 'moritz-eraneos-challenge'

@app.get("/")
def read_root():
    return {"message": "Hello World"}

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
def upload_json_string_to_gcp(data, file_name, is_file=False):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(json.dumps(data), content_type='application/json')
    return True

# POST route to receive json and upload it to GCS
@app.post("/upload/")
async def upload_json_from_string(data: DataItem, token: str = Depends(oauth2_scheme)):
    # Validate the token first
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        file_name = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_data = data.dict()
        upload_json_string_to_gcp(json_data, file_name)
        return {"status": "success", "file_name": file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Function to upload the file directly to GCS
def upload_json_file_to_gcp(
    file: UploadFile, destination_blob_name: str):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    # upload file directly without loading it into memory
    blob.upload_from_file(file.file, content_type=file.content_type)
    return True

@app.post("/upload-json/", summary="Upload JSON File", tags=["File Upload"])
async def upload_large_json(
    file: UploadFile = File(...), 
    token: str = Depends(oauth2_scheme)):
    """
    ### Description:
    This endpoint allows authenticated users to upload a **JSON file**. The file will be uploaded to **Google Cloud Storage** and processed on the backend.

    ### Authorization:
    - This endpoint requires a **Bearer token** for authorization.
    - The token must be passed in the `Authorization` header like so: `Bearer <your-token>`.

    ### Parameters:
    - **file**: The JSON file that needs to be uploaded. The file should be sent using `multipart/form-data`.

    ### Request Format:
    - Content Type: `multipart/form-data`
    - Example Request Body:
      ```bash
      curl -X 'POST' \\
        'https://your-api-endpoint/upload-json/' \\
        -H 'Authorization: Bearer <your-token>' \\
        -F 'file=@path-to-your-json-file.json'
      ```

    ### Responses:
    - **200 OK**: File uploaded successfully.
    - **401 Unauthorized**: Invalid or missing token.
    - **500 Internal Server Error**: An error occurred during the file upload.

    ### Example Response (Success):
    ```json
    {
      "status": "success",
      "filename": "uploaded_filename.json"
    }
    ```

    ### Example Response (Error):
    ```json
    {
      "detail": "Invalid or expired token"
    }
    ```
    """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        upload_json_file_to_gcp(file, file.filename)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))