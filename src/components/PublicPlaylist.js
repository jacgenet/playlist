import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Music, Clock, Zap, Share2, ExternalLink, Calendar } from 'lucide-react';

function PublicPlaylist() {
  const { id } = useParams();
  const [playlist, setPlaylist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Configure axios for this component
    // In production (Railway), the frontend is served by the same backend, so use relative URLs
    // In development, use the explicit localhost URL
    const isProduction = window.location.hostname !== 'localhost';
    const apiUrl = isProduction ? '' : (process.env.REACT_APP_API_URL || 'http://localhost:8000');
    axios.defaults.baseURL = apiUrl;
    
    fetchPlaylist();
  }, [id]);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get(`/api/playlists/public/${id}`);
      setPlaylist(response.data);
    } catch (error) {
      console.error('Error fetching public playlist:', error);
      setError('Playlist not found or not published');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const sharePlaylist = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: playlist.title,
          text: `Check out this spin playlist: ${playlist.title}`,
          url: window.location.href
        });
      } catch (error) {
        // Fallback to clipboard
        copyToClipboard();
      }
    } else {
      copyToClipboard();
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      alert('Link copied to clipboard!');
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !playlist) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Music className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Playlist not found</h3>
          <p className="mt-1 text-sm text-gray-500">
            This playlist may not exist or may not be published yet.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{playlist.title}</h1>
              {playlist.description && (
                <p className="mt-2 text-lg text-gray-600">{playlist.description}</p>
              )}
              <div className="mt-4 flex items-center text-sm text-gray-500">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(playlist.class_date)}
              </div>
            </div>
            <button
              onClick={sharePlaylist}
              className="btn-primary inline-flex items-center"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Music className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Tracks</p>
                <p className="text-2xl font-semibold text-gray-900">{playlist.tracks.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Duration</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatDuration(
                    playlist.tracks.reduce((sum, track) => sum + (track.duration || 0), 0)
                  )}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg BPM</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {playlist.tracks.length > 0
                    ? Math.round(
                        playlist.tracks
                          .filter(t => t.bpm)
                          .reduce((sum, track) => sum + track.bpm, 0) /
                        playlist.tracks.filter(t => t.bpm).length
                      ) || 'N/A'
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Track List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Track List</h2>
          </div>
          <div className="divide-y divide-gray-200">
            {playlist.tracks.map((track, index) => (
              <div key={track.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">{track.position}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {track.title}
                      </h3>
                      <p className="text-sm text-gray-500 truncate">
                        {track.artist}
                        {track.album && ` • ${track.album}`}
                      </p>
                      {track.notes && (
                        <p className="text-sm text-gray-600 mt-1">{track.notes}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right text-sm text-gray-500">
                      {track.duration && (
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {formatDuration(track.duration)}
                        </div>
                      )}
                      {track.bpm && (
                        <div className="flex items-center mt-1">
                          <Zap className="h-4 w-4 mr-1" />
                          {track.bpm} BPM
                        </div>
                      )}
                    </div>
                    
                    <div className="flex space-x-2">
                      {track.apple_music_url && (
                        <a
                          href={track.apple_music_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Apple Music
                        </a>
                      )}
                      {track.youtube_url && (
                        <a
                          href={track.youtube_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          YouTube
                        </a>
                      )}
                      {track.spotify_url && (
                        <a
                          href={track.spotify_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 hover:bg-green-200 transition-colors"
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Spotify
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Powered by Spin Playlist Manager</p>
        </div>
      </div>
    </div>
  );
}

export default PublicPlaylist;
