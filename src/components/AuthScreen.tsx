'use client';

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Loader2, BookOpen } from 'lucide-react';

export default function AuthScreen() {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailAuth = async (type: 'login' | 'register') => {
    if (!email || !password) {
      toast.error('Please enter both email and password');
      return;
    }

    setIsLoading(true);
    try {
      if (type === 'register') {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        
        if (data.session) {
          toast.success('Registration successful! You are now logged in.');
        } else {
          // Since we added a trigger to auto-confirm, a session should be created.
          // If not, we try to sign in immediately.
          const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
            email,
            password,
          });

          if (signInError) throw signInError;
          if (signInData.session) {
            toast.success('Registration successful! You are now logged in.');
          }
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        toast.success('Logged in successfully!');
      }
    } catch (error: any) {
      toast.error(error.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f8f9fc] px-4 py-12">
      <div className="w-full max-w-md space-y-8 bg-white p-8 rounded-3xl shadow-2xl shadow-indigo-100/50 border border-gray-100">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center p-3 bg-indigo-100 rounded-2xl mb-2">
            <BookOpen className="h-10 w-10 text-indigo-600" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">
            Study <span className="text-indigo-600">Buddy</span>
          </h1>
          <p className="text-gray-500">
            Sign in to start generating and saving your study notes.
          </p>
        </div>

        <div className="space-y-6">
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8 p-1 bg-gray-100/50 rounded-xl">
              <TabsTrigger value="login" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Login</TabsTrigger>
              <TabsTrigger value="register" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Register</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email-login">Email</Label>
                <Input
                  id="email-login"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="rounded-xl border-gray-200 focus:ring-indigo-500 bg-gray-50/30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password-login">Password</Label>
                <Input
                  id="password-login"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="rounded-xl border-gray-200 focus:ring-indigo-500 bg-gray-50/30"
                />
              </div>
              <Button 
                className="w-full bg-indigo-600 hover:bg-indigo-700 h-12 rounded-xl text-lg font-semibold transition-all shadow-lg shadow-indigo-200 mt-2" 
                onClick={() => handleEmailAuth('login')}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : 'Sign In'}
              </Button>
            </TabsContent>

            <TabsContent value="register" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email-register">Email</Label>
                <Input
                  id="email-register"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="rounded-xl border-gray-200 focus:ring-indigo-500 bg-gray-50/30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password-register">Password</Label>
                <Input
                  id="password-register"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="rounded-xl border-gray-200 focus:ring-indigo-500 bg-gray-50/30"
                />
              </div>
              <Button 
                className="w-full bg-indigo-600 hover:bg-indigo-700 h-12 rounded-xl text-lg font-semibold transition-all shadow-lg shadow-indigo-200 mt-2" 
                onClick={() => handleEmailAuth('register')}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : 'Create Account'}
              </Button>
            </TabsContent>
          </Tabs>
        </div>
        
        <p className="text-center text-xs text-gray-400 mt-6 font-medium">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
