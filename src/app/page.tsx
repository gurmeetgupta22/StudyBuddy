'use client';

import { useState } from 'react';
import Navbar from '@/components/Navbar';
import NoteForm from '@/components/NoteForm';
import NoteDisplay from '@/components/NoteDisplay';
import HistoryList from '@/components/HistoryList';
import AuthScreen from '@/components/AuthScreen';
import { useAuth } from '@/lib/auth-context';
import { GeneratedNotes } from '@/types';
import { BookOpen, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function Home() {
  const { user, isLoading } = useAuth();
  const [generatedNotes, setGeneratedNotes] = useState<GeneratedNotes | null>(null);
  const [refreshHistory, setRefreshHistory] = useState(0);

  const handleGenerated = (notes: GeneratedNotes) => {
    setGeneratedNotes(notes);
    setRefreshHistory(prev => prev + 1);
  };

  const handleSelectHistory = (notes: GeneratedNotes) => {
    setGeneratedNotes(notes);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8f9fc]">
        <Loader2 className="h-8 w-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  return (
    <div className="min-h-screen bg-[#f8f9fc] text-gray-900 font-sans">
      <Navbar />
      
      <main className="max-w-3xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {!generatedNotes ? (
          <div className="space-y-8 animate-in fade-in slide-in-from-top-4 duration-700">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center p-3 bg-indigo-100 rounded-2xl mb-2">
                <BookOpen className="h-8 w-8 text-indigo-600" />
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
                Your Personal <span className="text-indigo-600">Study Buddy</span>
              </h1>
              <p className="text-xl text-gray-500 max-w-2xl mx-auto">
                Generate high-quality, book-style study notes for school or college in seconds.
              </p>
            </div>

            <NoteForm onGenerated={handleGenerated} />
            
            <HistoryList onSelect={handleSelectHistory} refreshTrigger={refreshHistory} />
          </div>
        ) : (
          <div className="space-y-8">
            <Button 
              variant="ghost" 
              onClick={() => setGeneratedNotes(null)}
              className="group text-gray-500 hover:text-indigo-600 pl-0 transition-colors"
            >
              <ArrowLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
              Back to Generator
            </Button>
            
            <NoteDisplay data={generatedNotes} />
          </div>
        )}
      </main>

      <footer className="mt-auto py-12 border-t bg-white">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-400 font-medium">
            &copy; {new Date().getFullYear()} Study Buddy AI. Designed for students, by students.
          </p>
        </div>
      </footer>
    </div>
  );
}
