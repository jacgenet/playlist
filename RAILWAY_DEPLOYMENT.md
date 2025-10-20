# Railway Deployment Guide

## Prerequisites
1. Railway account (sign up at https://railway.app)
2. GitHub repository with your code
3. PostgreSQL database (Railway provides this)

## Step 1: Connect GitHub Repository
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `spinning_playlist` repository

## Step 2: Add PostgreSQL Database
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. Copy the `DATABASE_URL` from the database service

## Step 3: Configure Environment Variables
In your Railway project settings, add these environment variables:

### Required Variables:
```
DATABASE_URL=postgresql://username:password@host:port/database
JWT_SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-password
CORS_ORIGINS=https://your-app-name.railway.app
```

### Optional Variables (for metadata enrichment):
```
ITUNES_API_KEY=your-itunes-api-key
YOUTUBE_API_KEY=your-youtube-api-key
```

### Frontend Variables:
```
REACT_APP_API_URL=https://your-backend-service.railway.app
```

## Step 4: Deploy Backend Service
1. Railway will automatically detect your `railway.json` configuration
2. The backend will deploy using the settings in `railway.json`
3. Railway will use the PORT environment variable automatically

## Step 5: Deploy Frontend (Separate Service)
1. Create a new service in Railway
2. Connect the same GitHub repository
3. Set the root directory to `/` (root of repo)
4. Add these environment variables:
   ```
   REACT_APP_API_URL=https://your-backend-service.railway.app
   ```
5. Railway will build the React app and serve it

## Step 6: Configure Custom Domains (Optional)
1. In each service, go to "Settings" → "Domains"
2. Add custom domains if desired
3. Update CORS_ORIGINS to include your custom domains

## Step 7: Test Deployment
1. Visit your frontend URL
2. Try logging in with your ADMIN_EMAIL and ADMIN_PASSWORD
3. Test creating and publishing playlists
4. Test the public homepage and playlist views

## Troubleshooting

### Database Connection Issues:
- Ensure DATABASE_URL is correctly formatted
- Check that PostgreSQL service is running
- Verify database credentials

### CORS Issues:
- Add your Railway domains to CORS_ORIGINS
- Include both HTTP and HTTPS versions if needed
- Check browser console for CORS errors

### Frontend Not Loading:
- Verify REACT_APP_API_URL points to your backend
- Check that backend is running and accessible
- Look at Railway logs for build errors

### Authentication Issues:
- Ensure JWT_SECRET_KEY is set and consistent
- Check that ADMIN_EMAIL and ADMIN_PASSWORD are set
- Verify backend is accessible from frontend

## Railway CLI (Optional)
Install Railway CLI for easier management:
```bash
npm install -g @railway/cli
railway login
railway link
railway up
```

## Monitoring
- Check Railway dashboard for service health
- Monitor logs in Railway console
- Set up alerts for service downtime
