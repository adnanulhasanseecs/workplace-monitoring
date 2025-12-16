/**
 * Dashboard page component.
 */
import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

interface Camera {
  id: number;
  name: string;
  status: string;
  location?: string;
}

interface Event {
  id: number;
  event_type: string;
  event_code: string;
  severity: string;
  confidence: number;
  timestamp: string;
}

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    };
  };

  const loadData = async () => {
    try {
      const [camerasRes, eventsRes] = await Promise.all([
        fetch(`${API_BASE}/cameras`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE}/events?limit=10`, { headers: getAuthHeaders() }),
      ]);

      if (!camerasRes.ok || !eventsRes.ok) {
        throw new Error('Failed to load data');
      }

      const camerasData = await camerasRes.json();
      const eventsData = await eventsRes.json();

      setCameras(camerasData);
      setEvents(eventsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Cameras ({cameras.length})
            </h2>
            <div className="space-y-2">
              {cameras.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">No cameras configured</p>
              ) : (
                cameras.map((camera) => (
                  <div key={camera.id} className="flex justify-between items-center">
                    <span className="text-gray-900 dark:text-white">{camera.name}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      camera.status === 'active' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                      {camera.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Recent Events ({events.length})
            </h2>
            <div className="space-y-2">
              {events.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">No events detected</p>
              ) : (
                events.map((event) => (
                  <div key={event.id} className="flex justify-between items-center">
                    <div>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {event.event_code}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {(event.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="flex gap-4">
            <a
              href="/cameras"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Manage Cameras
            </a>
            <a
              href="/events"
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              View Events
            </a>
            <a
              href="/rules"
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Configure Rules
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

