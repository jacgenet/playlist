# Spin Playlist Manager

A calendar-first playlist publishing platform for spin instructors. Upload XML playlists, enrich track metadata, and publish shareable public pages for class attendees.

## Features

- **Calendar-First Design**: Create and manage playlists tied to specific class dates/times
- **XML Import**: Upload playlists from DJ software and playlist managers
- **Metadata Enrichment**: Automatic Apple Music and YouTube link discovery
- **Public Sharing**: Generate shareable URLs for published playlists
- **Mobile-First UI**: Responsive design optimized for all devices
- **Admin Dashboard**: Complete playlist management interface

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with Tailwind CSS
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **APIs**: iTunes/Apple Music, YouTube Data API

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spinning_playlist
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   npm install
   ```

5. **Set up the database**
   ```bash
   # Create PostgreSQL database
   createdb spin_playlist
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

6. **Start the backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

7. **Start the frontend** (in a new terminal)
   ```bash
   npm start
   ```

8. **Create admin account**
   ```bash
   # Use the API to create an admin account
   curl -X POST "http://localhost:8000/api/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email": "admin@example.com", "password": "your-password"}'
   ```

### Docker Setup

1. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Create admin account**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email": "admin@example.com", "password": "your-password"}'
   ```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `YOUTUBE_API_KEY`: YouTube Data API key (optional)
- `ENVIRONMENT`: Environment (development/production)

### API Keys

1. **YouTube Data API** (optional)
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create credentials and add to `YOUTUBE_API_KEY`

## Usage

### Admin Workflow

1. **Login** to the admin dashboard
2. **Create playlist** from calendar or manually
3. **Import XML** or add tracks manually
4. **Edit tracks** and enrich metadata
5. **Publish** to generate public URL
6. **Share** the public URL with class attendees

### Public Access

- Published playlists are accessible at `/public/playlist/{id}`
- Mobile-optimized interface
- Direct links to Apple Music, YouTube, and Spotify
- Social sharing capabilities

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create admin account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Playlists
- `GET /api/playlists/` - List playlists
- `POST /api/playlists/` - Create playlist
- `GET /api/playlists/{id}` - Get playlist
- `PUT /api/playlists/{id}` - Update playlist
- `DELETE /api/playlists/{id}` - Delete playlist
- `POST /api/playlists/import-xml` - Import XML
- `GET /api/playlists/public/{id}` - Public playlist view

### Calendar
- `GET /api/calendar/events` - Get calendar events
- `GET /api/calendar/month/{year}/{month}` - Get month events
- `GET /api/calendar/day/{year}/{month}/{day}` - Get day events

### Tracks
- `GET /api/tracks/playlist/{id}` - Get playlist tracks
- `POST /api/tracks/playlist/{id}` - Add track
- `PUT /api/tracks/{id}` - Update track
- `DELETE /api/tracks/{id}` - Delete track

## Deployment

### Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set DATABASE_URL=postgresql://...
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set YOUTUBE_API_KEY=your-api-key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Render

1. **Connect repository** to Render
2. **Set environment variables** in dashboard
3. **Deploy** automatically on push

### AWS/GCP

Use the provided Dockerfile for containerized deployment.

## Development

### Project Structure

```
spinning_playlist/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── xml_parser.py        # XML import functionality
│   ├── metadata_enrichment.py # API integrations
│   └── routers/             # API routes
├── src/
│   ├── components/          # React components
│   ├── contexts/            # React contexts
│   └── App.js               # Main app component
├── public/                  # Static assets
├── requirements.txt         # Python dependencies
├── package.json             # Node dependencies
└── Dockerfile              # Production container
```

### Adding Features

1. **Backend**: Add routes in `routers/`, models in `models.py`
2. **Frontend**: Add components in `src/components/`
3. **Database**: Update models and run migrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

## Roadmap

- [ ] Multi-instructor support
- [ ] Advanced analytics
- [ ] Playlist templates
- [ ] Mobile app
- [ ] Integration with fitness platforms
- [ ] Advanced metadata enrichment
- [ ] Playlist collaboration features
