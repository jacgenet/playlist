import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Save, Upload, Plus, Trash2, ExternalLink, Music } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

function PlaylistEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isNew = id === 'new';
  
  const [playlist, setPlaylist] = useState({
    title: '',
    description: '',
    class_date: '',
    is_published: false
  });
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Configure axios for this component
    // In production (Railway), the frontend is served by the same backend, so use relative URLs
    // In development, use the explicit localhost URL
    const isProduction = window.location.hostname !== 'localhost';
    const apiUrl = isProduction ? '' : (process.env.REACT_APP_API_URL || 'http://localhost:8000');
    axios.defaults.baseURL = apiUrl;
    
    if (!isNew) {
      fetchPlaylist();
    } else {
      // Set default date from URL params
      const dateParam = searchParams.get('date');
      if (dateParam) {
        setPlaylist(prev => ({
          ...prev,
          class_date: dateParam
        }));
      }
    }
  }, [id, isNew, searchParams]);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get(`/api/playlists/${id}`);
      setPlaylist(response.data);
      setTracks(response.data.tracks || []);
    } catch (error) {
      console.error('Error fetching playlist:', error);
      setError('Failed to load playlist');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');

    try {
      if (isNew) {
        const response = await axios.post('/api/playlists/', playlist);
        navigate(`/playlist/${response.data.id}`);
      } else {
        await axios.put(`/api/playlists/${id}`, playlist);
      }
    } catch (error) {
      console.error('Save error:', error.response?.data);
      const errorDetail = error.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        // Handle validation errors
        setError(errorDetail.map(err => err.msg).join(', '));
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Failed to save playlist');
      }
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    setSaving(true);
    setError('');

    try {
      await axios.put(`/api/playlists/${id}`, {
        ...playlist,
        is_published: !playlist.is_published
      });
      setPlaylist(prev => ({ ...prev, is_published: !prev.is_published }));
    } catch (error) {
      console.error('Publish error:', error.response?.data);
      const errorDetail = error.response?.data?.detail;
      if (Array.isArray(errorDetail)) {
        // Handle validation errors
        setError(errorDetail.map(err => err.msg).join(', '));
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Failed to update playlist');
      }
    } finally {
      setSaving(false);
    }
  };

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (playlist.class_date) {
        formData.append('class_date', playlist.class_date);
      }

      const response = await axios.post('/api/playlists/import-xml', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        navigate(`/playlist/${response.data.playlist_id}`);
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to import XML');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
      'application/x-plist': ['.plist'],
      'text/x-plist': ['.plist']
    },
    multiple: false
  });

  const addTrack = () => {
    const newTrack = {
      position: tracks.length + 1,
      title: '',
      artist: '',
      album: '',
      duration: null,
      bpm: null,
      genre: '',
      notes: ''
    };
    setTracks([...tracks, newTrack]);
  };

  const updateTrack = (index, field, value) => {
    const updatedTracks = [...tracks];
    updatedTracks[index] = { ...updatedTracks[index], [field]: value };
    setTracks(updatedTracks);
  };

  const removeTrack = (index) => {
    const updatedTracks = tracks.filter((_, i) => i !== index);
    // Reorder positions
    updatedTracks.forEach((track, i) => {
      track.position = i + 1;
    });
    setTracks(updatedTracks);
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isNew ? 'New Playlist' : 'Edit Playlist'}
          </h1>
          <p className="text-gray-600">
            {isNew ? 'Create a new playlist' : 'Edit your playlist details and tracks'}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary inline-flex items-center"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save'}
          </button>
          {!isNew && (
            <button
              onClick={handlePublish}
              disabled={saving}
              className={`inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                playlist.is_published
                  ? 'bg-gray-600 hover:bg-gray-700 text-white'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {playlist.is_published ? 'Unpublish' : 'Publish'}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Playlist Details */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Playlist Details</h3>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label className="form-label">Title</label>
            <input
              type="text"
              className="form-input"
              value={playlist.title}
              onChange={(e) => setPlaylist(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter playlist title"
            />
          </div>
          
          <div>
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={3}
              value={playlist.description}
              onChange={(e) => setPlaylist(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter playlist description"
            />
          </div>
          
          <div>
            <label className="form-label">Class Date & Time</label>
            <input
              type="datetime-local"
              className="form-input"
              value={playlist.class_date}
              onChange={(e) => setPlaylist(prev => ({ ...prev, class_date: e.target.value }))}
            />
          </div>
        </div>
      </div>

      {/* File Import */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Import Playlist</h3>
        </div>
        <div className="card-body">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-600">
              {isDragActive
                ? 'Drop the file here...'
                : 'Drag & drop a playlist file here, or click to select'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Supports XML files from DJ software and iTunes Library files (.plist)
            </p>
          </div>
          {uploading && (
            <div className="mt-4 text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600 mt-2">Importing tracks...</p>
            </div>
          )}
        </div>
      </div>

      {/* Tracks */}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">Tracks</h3>
          <button
            onClick={addTrack}
            className="btn-secondary inline-flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Track
          </button>
        </div>
        <div className="card-body">
          {tracks.length === 0 ? (
            <div className="text-center py-8">
              <Music className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No tracks</h3>
              <p className="mt-1 text-sm text-gray-500">
                Add tracks manually or import from XML.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {tracks.map((track, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="font-medium text-gray-900">Track {track.position}</h4>
                    <button
                      onClick={() => removeTrack(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">Title</label>
                      <input
                        type="text"
                        className="form-input"
                        value={track.title}
                        onChange={(e) => updateTrack(index, 'title', e.target.value)}
                        placeholder="Track title"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">Artist</label>
                      <input
                        type="text"
                        className="form-input"
                        value={track.artist}
                        onChange={(e) => updateTrack(index, 'artist', e.target.value)}
                        placeholder="Artist name"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">Album</label>
                      <input
                        type="text"
                        className="form-input"
                        value={track.album}
                        onChange={(e) => updateTrack(index, 'album', e.target.value)}
                        placeholder="Album name"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">Duration (seconds)</label>
                      <input
                        type="number"
                        className="form-input"
                        value={track.duration || ''}
                        onChange={(e) => updateTrack(index, 'duration', parseFloat(e.target.value) || null)}
                        placeholder="Duration in seconds"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">BPM</label>
                      <input
                        type="number"
                        className="form-input"
                        value={track.bpm || ''}
                        onChange={(e) => updateTrack(index, 'bpm', parseInt(e.target.value) || null)}
                        placeholder="Beats per minute"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">Genre</label>
                      <input
                        type="text"
                        className="form-input"
                        value={track.genre}
                        onChange={(e) => updateTrack(index, 'genre', e.target.value)}
                        placeholder="Genre"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <label className="form-label">Notes</label>
                    <textarea
                      className="form-input"
                      rows={2}
                      value={track.notes}
                      onChange={(e) => updateTrack(index, 'notes', e.target.value)}
                      placeholder="Additional notes"
                    />
                  </div>
                  
                  {/* External Links */}
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="form-label">Apple Music URL</label>
                      <input
                        type="url"
                        className="form-input"
                        value={track.apple_music_url || ''}
                        onChange={(e) => updateTrack(index, 'apple_music_url', e.target.value)}
                        placeholder="Apple Music link"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">YouTube URL</label>
                      <input
                        type="url"
                        className="form-input"
                        value={track.youtube_url || ''}
                        onChange={(e) => updateTrack(index, 'youtube_url', e.target.value)}
                        placeholder="YouTube link"
                      />
                    </div>
                    
                    <div>
                      <label className="form-label">Spotify URL</label>
                      <input
                        type="url"
                        className="form-input"
                        value={track.spotify_url || ''}
                        onChange={(e) => updateTrack(index, 'spotify_url', e.target.value)}
                        placeholder="Spotify link"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PlaylistEditor;
