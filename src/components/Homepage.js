import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Calendar, Music, Clock, BarChart3, Plus } from 'lucide-react';

function Homepage() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Configure axios for this component
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    axios.defaults.baseURL = apiUrl;
    
    fetchPublishedPlaylists();
  }, []);

  const fetchPublishedPlaylists = async () => {
    try {
      const response = await axios.get('/api/playlists/');
      // Filter only published playlists
      const publishedPlaylists = response.data.filter(playlist => playlist.is_published);
      setPlaylists(publishedPlaylists);
    } catch (error) {
      console.error('Error fetching playlists:', error);
    } finally {
      setLoading(false);
    }
  };

  const generatePlaylistImage = (playlist) => {
    // Create a simple gradient based on playlist title hash
    const colors = [
      'from-purple-500 to-pink-500',
      'from-blue-500 to-cyan-500', 
      'from-green-500 to-emerald-500',
      'from-orange-500 to-red-500',
      'from-indigo-500 to-purple-500',
      'from-pink-500 to-rose-500',
      'from-teal-500 to-blue-500',
      'from-yellow-500 to-orange-500'
    ];
    
    // Simple hash function to get consistent color for same title
    let hash = 0;
    for (let i = 0; i < playlist.title.length; i++) {
      hash = ((hash << 5) - hash + playlist.title.charCodeAt(i)) & 0xffffffff;
    }
    const colorIndex = Math.abs(hash) % colors.length;
    
    return colors[colorIndex];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handlePlaylistClick = (playlistId) => {
    navigate(`/public/playlist/${playlistId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="px-6 py-8">
        <h1 className="text-4xl font-bold mb-2">Welcome to Spin Playlist Manager</h1>
        <p className="text-gray-400 text-lg">Discover and enjoy curated spin playlists</p>
        
        {/* Navigation Links */}
        <div className="mt-6 flex flex-wrap gap-4">
          <button
            onClick={() => navigate('/calendar')}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <Calendar className="h-5 w-5 mr-2" />
            Calendar
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
          >
            <BarChart3 className="h-5 w-5 mr-2" />
            Dashboard
          </button>
          <button
            onClick={() => navigate('/playlist/new')}
            className="flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            New Playlist
          </button>
        </div>
      </div>

      {/* Playlist Grid */}
      <div className="px-6 pb-24">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {playlists.map((playlist) => (
            <div
              key={playlist.id}
              onClick={() => handlePlaylistClick(playlist.id)}
              className="bg-gray-800 rounded-lg p-4 cursor-pointer hover:bg-gray-700 transition-colors group"
            >
              {/* Playlist Image */}
              <div className="relative mb-4">
                <div className={`w-full h-48 rounded-lg bg-gradient-to-br ${generatePlaylistImage(playlist)} flex items-center justify-center shadow-lg`}>
                  <Music className="h-16 w-16 text-white opacity-80" />
                </div>
                {/* Play button overlay */}
                <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="bg-green-500 rounded-full p-3 hover:bg-green-400 transition-colors">
                    <svg className="w-6 h-6 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              </div>

              {/* Playlist Info */}
              <div className="space-y-1">
                <h3 className="font-bold text-lg text-white truncate group-hover:text-green-400 transition-colors">
                  {playlist.title}
                </h3>
                <div className="flex items-center text-gray-400 text-sm">
                  <Calendar className="h-4 w-4 mr-1" />
                  <span>{formatDate(playlist.class_date)}</span>
                </div>
                {playlist.description && (
                  <p className="text-gray-400 text-sm truncate">
                    {playlist.description}
                  </p>
                )}
                <div className="flex items-center text-gray-400 text-sm">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>{playlist.tracks?.length || 0} tracks</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {playlists.length === 0 && (
          <div className="text-center py-12">
            <Music className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No published playlists yet</h3>
            <p className="text-gray-500">Check back later for new spin playlists!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Homepage;
