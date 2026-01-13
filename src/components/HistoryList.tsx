'use client';

import { useEffect, useState } from 'react';
import { getHistory } from '@/lib/actions';
import { GeneratedNotes } from '@/types';
import { History, Clock, ChevronRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '@/lib/auth-context';

interface HistoryListProps {
  onSelect: (notes: GeneratedNotes) => void;
  refreshTrigger: number;
}

export default function HistoryList({ onSelect, refreshTrigger }: HistoryListProps) {
  const { user } = useAuth();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      const result = await getHistory(user?.id);
      if (result.success && result.data) {
        setHistory(result.data);
      }
      setLoading(false);
    }
    fetchHistory();
  }, [refreshTrigger, user?.id]);

  if (loading) return null;
  if (history.length === 0) return null;

  return (
    <div className="mt-12 space-y-4">
      <div className="flex items-center gap-2 text-gray-900 font-bold px-1">
        <History className="h-5 w-5 text-indigo-600" />
        <h2 className="text-lg">{user ? 'Your Recent Notes' : 'Community Recent Notes'}</h2>
      </div>
      <div className="grid gap-3">
        {history.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelect(item.content)}
            className="flex items-center justify-between p-4 bg-white border rounded-xl hover:border-indigo-300 hover:shadow-sm transition-all text-left group"
          >
            <div className="space-y-1">
              <h3 className="font-bold text-gray-900 truncate max-w-[200px] sm:max-w-md">
                {item.topics}
              </h3>
              <div className="flex items-center gap-3 text-xs text-gray-500 font-medium">
                <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-600 capitalize">
                  {item.domain}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </span>
              </div>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-indigo-600 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
}
