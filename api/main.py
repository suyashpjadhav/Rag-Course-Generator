from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="PDF Chunking & Querying API")

# ✅ Add CORS middleware BEFORE including router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific origins like ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include your API routes
app.include_router(router, prefix="/api")
