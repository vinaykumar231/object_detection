from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.models import MediaUpload, DetectionResults, DetectedObjects 
from app.routes import detection_router  
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(detection_router, prefix="/detection")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8003, reload=True, host="0.0.0.0")
