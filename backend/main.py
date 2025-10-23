from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base
from auth import get_current_admin
from routers import auth, playlists, tracks, calendar

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create initial admin user if it doesn't exist
def create_initial_admin():
    from sqlalchemy.orm import Session
    from models import Admin
    from auth import get_password_hash, get_admin_by_email
    
    db = Session(bind=engine)
    try:
        # Check if admin already exists
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        existing_admin = get_admin_by_email(db, admin_email)
        
        if not existing_admin:
            # Create initial admin
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            hashed_password = get_password_hash(admin_password)
            
            admin = Admin(
                email=admin_email,
                hashed_password=hashed_password
            )
            db.add(admin)
            db.commit()
            print(f"Created initial admin user: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

# Create initial admin user
create_initial_admin()

app = FastAPI(
    title="Spin Playlist Manager",
    description="Calendar-first playlist publishing for spin instructors",
    version="1.0.0"
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,https://playlist-production-3535.up.railway.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint FIRST (before catch-all route)
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Spin Playlist Manager API is running"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(playlists.router, prefix="/api/playlists", tags=["playlists"])
app.include_router(tracks.router, prefix="/api/tracks", tags=["tracks"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])

# Serve static files (React build) - LAST to avoid intercepting API routes
if os.path.exists("./frontend/build"):
    app.mount("/static", StaticFiles(directory="./frontend/build/static"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Serve React app for all non-API routes
        if not full_path.startswith("api/"):
            return FileResponse("./frontend/build/index.html")
        else:
            raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
