import React, { useState, useCallback } from 'react';
import { Calendar as BigCalendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Plus, Music } from 'lucide-react';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const localizer = momentLocalizer(moment);

function Calendar() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchEvents = useCallback(async () => {
    try {
      const response = await axios.get('/api/calendar/events');
      const calendarEvents = response.data.map(event => ({
        id: event.id,
        title: event.title,
        start: new Date(event.start),
        end: new Date(event.end),
        resource: {
          isPublished: event.is_published,
          tracksCount: event.tracks_count
        }
      }));
      setEvents(calendarEvents);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleSelectSlot = ({ start, end }) => {
    // Create new playlist for selected date/time
    const startDate = moment(start).format('YYYY-MM-DDTHH:mm:ss');
    navigate(`/playlist/new?date=${startDate}`);
  };

  const handleSelectEvent = (event) => {
    // Navigate to edit playlist
    navigate(`/playlist/${event.id}`);
  };

  const eventStyleGetter = (event) => {
    const isPublished = event.resource?.isPublished;
    return {
      style: {
        backgroundColor: isPublished ? '#10b981' : '#3b82f6',
        borderRadius: '4px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block'
      }
    };
  };

  const CustomEvent = ({ event }) => (
    <div className="flex items-center">
      <Music className="h-3 w-3 mr-1" />
      <span className="text-xs font-medium truncate">{event.title}</span>
      {event.resource?.tracksCount > 0 && (
        <span className="ml-1 text-xs opacity-75">
          ({event.resource.tracksCount})
        </span>
      )}
    </div>
  );

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
          <h1 className="text-2xl font-bold text-gray-900">Calendar</h1>
          <p className="text-gray-600">Manage your class schedule and playlists</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => navigate('/playlist/new')}
            className="btn-primary inline-flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Playlist
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center space-x-6 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
          <span>Draft Playlist</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
          <span>Published Playlist</span>
        </div>
      </div>

      {/* Calendar */}
      <div className="card">
        <div className="card-body p-0">
          <BigCalendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ height: 600 }}
            onSelectSlot={handleSelectSlot}
            onSelectEvent={handleSelectEvent}
            selectable
            eventPropGetter={eventStyleGetter}
            components={{
              event: CustomEvent
            }}
            views={['month', 'week', 'day']}
            defaultView="month"
            step={30}
            timeslots={2}
            min={new Date(2024, 0, 1, 5, 0)} // 5 AM
            max={new Date(2024, 0, 1, 23, 0)} // 11 PM
            formats={{
              timeGutterFormat: 'HH:mm',
              eventTimeRangeFormat: ({ start, end }) =>
                `${moment(start).format('HH:mm')} - ${moment(end).format('HH:mm')}`
            }}
          />
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">How to use the calendar:</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Click on any empty time slot to create a new playlist for that date/time</li>
          <li>• Click on existing events to edit playlists</li>
          <li>• Green events are published playlists, blue events are drafts</li>
          <li>• The number in parentheses shows the track count</li>
        </ul>
      </div>
    </div>
  );
}

export default Calendar;
