# Spin Playlist Manager - Installation Guide

This guide provides detailed instructions for installing and setting up the Spin Playlist Manager application on various platforms and environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Development Setup](#development-setup)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Platform-Specific Guides](#platform-specific-guides)

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet connection for API integrations

### Required Software

#### For Development Setup:
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **PostgreSQL 13+** ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))

#### For Docker Setup:
- **Docker** ([Download](https://www.docker.com/get-started))
- **Docker Compose** (included with Docker Desktop)

## Quick Start (Docker)

The fastest way to get started is using Docker Compose:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd spinning_playlist
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit the environment file
nano .env
```

Update the following variables in `.env`:
```env
# Database (Docker will handle this automatically)
DATABASE_URL=postgresql://postgres:password@db:5432/spin_playlist

# Security (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# YouTube API (optional but recommended)
YOUTUBE_API_KEY=your-youtube-api-key-here

# Environment
ENVIRONMENT=development
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps
```

### 4. Create Admin Account

```bash
# Wait for services to be ready (about 30 seconds)
sleep 30

# Create admin account
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "password": "your-secure-password"
     }'
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 6. Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data!)
docker-compose down -v
```

## Development Setup

For active development with hot reloading:

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd spinning_playlist
```

### 2. Set Up Python Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Node.js Frontend

```bash
# Install Node.js dependencies
npm install
```

### 4. Set Up Database

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL (if not already installed)
# macOS with Homebrew:
brew install postgresql
brew services start postgresql

# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb spin_playlist

# Create user (optional)
sudo -u postgres createuser --interactive
```

#### Option B: Docker Database Only

```bash
# Start only the database
docker-compose up -d db

# Wait for database to be ready
sleep 10
```

### 5. Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit environment file
nano .env
```

For local development, use:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/spin_playlist

# Security
SECRET_KEY=development-secret-key-not-for-production

# YouTube API (optional)
YOUTUBE_API_KEY=your-youtube-api-key

# Environment
ENVIRONMENT=development
```

### 6. Initialize Database

```bash
# Navigate to backend directory
cd backend

# Create database tables
python -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"
```

### 7. Start Development Servers

#### Terminal 1 - Backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend:
```bash
npm start
```

### 8. Create Admin Account

```bash
# In a new terminal
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@example.com",
       "password": "your-secure-password"
     }'
```

### 9. Access the Application

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Production Deployment

### Heroku Deployment

#### 1. Prepare for Heroku

```bash
# Install Heroku CLI
# macOS:
brew tap heroku/brew && brew install heroku
# Ubuntu:
sudo snap install --classic heroku

# Login to Heroku
heroku login
```

#### 2. Create Heroku App

```bash
# Create new app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev
```

#### 3. Configure Environment Variables

```bash
# Set environment variables
heroku config:set SECRET_KEY="your-super-secret-production-key"
heroku config:set YOUTUBE_API_KEY="your-youtube-api-key"
heroku config:set ENVIRONMENT="production"

# Check configuration
heroku config
```

#### 4. Deploy

```bash
# Deploy to Heroku
git push heroku main

# Create admin account
heroku run python -c "
import requests
response = requests.post('https://your-app-name.herokuapp.com/api/auth/register', 
                        json={'email': 'admin@example.com', 'password': 'your-password'})
print('Admin account created:', response.status_code)
"
```

### Render Deployment

#### 1. Connect Repository

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository

#### 2. Configure Service

- **Name**: `spin-playlist-manager`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

#### 3. Set Environment Variables

In the Render dashboard:
- `SECRET_KEY`: Your production secret key
- `YOUTUBE_API_KEY`: Your YouTube API key
- `ENVIRONMENT`: `production`
- `DATABASE_URL`: (Auto-generated by Render)

#### 4. Deploy

Click "Create Web Service" and wait for deployment.

### AWS/GCP Deployment

#### Using Docker

```bash
# Build production image
docker build -t spin-playlist-manager .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="your-postgresql-url" \
  -e SECRET_KEY="your-secret-key" \
  -e YOUTUBE_API_KEY="your-youtube-key" \
  -e ENVIRONMENT="production" \
  spin-playlist-manager
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `sqlite:///./spin_playlist.db` |
| `SECRET_KEY` | JWT secret key | Yes | None |
| `YOUTUBE_API_KEY` | YouTube Data API key | No | None |
| `ENVIRONMENT` | Environment (development/production) | No | `development` |

### Database Configuration

#### PostgreSQL Connection String Format:
```
postgresql://username:password@host:port/database_name
```

#### Examples:
- **Local**: `postgresql://postgres:password@localhost:5432/spin_playlist`
- **Heroku**: `postgresql://user:pass@host:5432/dbname` (auto-generated)
- **Docker**: `postgresql://postgres:password@db:5432/spin_playlist`

### API Keys Setup

#### YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Restrict the key to YouTube Data API v3
6. Add the key to your environment variables

#### iTunes/Apple Music API

No API key required - uses public iTunes Search API.

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
# macOS:
brew services list | grep postgresql

# Ubuntu:
sudo systemctl status postgresql

# Start PostgreSQL if not running
# macOS:
brew services start postgresql

# Ubuntu:
sudo systemctl start postgresql
```

#### 2. Port Already in Use

**Error**: `Address already in use`

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
```

#### 3. Node.js Dependencies Issues

**Error**: `npm ERR! peer dep missing`

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Python Dependencies Issues

**Error**: `ModuleNotFoundError`

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 5. Docker Issues

**Error**: `docker-compose: command not found`

**Solutions**:
```bash
# Install Docker Compose
# macOS/Windows: Install Docker Desktop
# Linux:
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Logs and Debugging

#### View Application Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Heroku logs
heroku logs --tail

# Render logs
# Check in Render dashboard under "Logs" tab
```

#### Debug Mode

```bash
# Enable debug mode in development
export ENVIRONMENT=development
export DEBUG=true

# Start with debug logging
uvicorn main:app --reload --log-level debug
```

## Platform-Specific Guides

### macOS Installation

#### Using Homebrew

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 node postgresql git

# Start PostgreSQL
brew services start postgresql

# Create database
createdb spin_playlist
```

### Ubuntu/Debian Installation

```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm postgresql postgresql-contrib git

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres createdb spin_playlist
```

### Windows Installation

#### Using Chocolatey

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python nodejs postgresql git

# Start PostgreSQL service
net start postgresql-x64-13
```

#### Manual Installation

1. Download and install [Python 3.11+](https://www.python.org/downloads/windows/)
2. Download and install [Node.js 18+](https://nodejs.org/en/download/)
3. Download and install [PostgreSQL](https://www.postgresql.org/download/windows/)
4. Download and install [Git](https://git-scm.com/download/win)

### Docker on Different Platforms

#### Linux

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
```

#### Windows

1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and restart
3. Enable WSL 2 integration if using WSL

#### macOS

1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Ensure Docker is running (whale icon in menu bar)

## Next Steps

After successful installation:

1. **Create your first playlist** by logging into the admin dashboard
2. **Import an XML playlist** to test the import functionality
3. **Publish a playlist** and share the public URL
4. **Configure YouTube API** for enhanced metadata enrichment
5. **Set up monitoring** for production deployments

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review application logs
3. Ensure all prerequisites are met
4. Verify environment variables are set correctly
5. Check database connectivity

For additional help, create an issue in the project repository with:
- Your operating system
- Installation method used
- Error messages
- Steps to reproduce the issue
