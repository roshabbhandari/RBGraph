from fastapi import FastAPI
from fastapi.middleware.cores import CORSMiddleware


app = FastAPI(
  title = "RBGraph",
  description = "plain-English technical diagram generator",
   version = "0.1.0",
)


app.add_middleware(
  CORSMiddeware,
  allow_origins = ["*"],
  allow_crendetials = True,
  allow_methods = ["*"],
  allow_headers = ["*"],
)





@app.get("/")
def root():
  return{
    "name":"RBGraph",
    "version":"0.1.0",
    "status":"running",
    "message":"RBGraph API is running",
  }





@app.get("/health")
def health():
  return{
    "status":"healthy"
  }

