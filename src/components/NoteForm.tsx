'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Sparkles, Loader2, BookOpen, GraduationCap, Trophy } from 'lucide-react';
import { generateNotes } from '@/lib/actions';
import { GeneratedNotes } from '@/types';
import { toast } from 'sonner';
import { useAuth } from '@/lib/auth-context';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface NoteFormProps {
  onGenerated: (notes: GeneratedNotes) => void;
}

type Domain = 'School' | 'College' | 'Competitive Exam';

const SCHOOL_CLASSES = [
  'Class 6', 'Class 7', 'Class 8', 'Class 9', 'Class 10', 'Class 11', 'Class 12'
];

const COLLEGE_SEMESTERS = [
  'Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 
  'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8'
];

const COMPETITIVE_EXAMS = [
  'NEET', 'JEE-Mains', 'JEE-Advanced', 'GATE', 'UPSC', 'CAT', 'CLAT', 'GRE', 'GMAT', 'SAT', 'IELTS', 'TOEFL', 'NDA', 'CDS', 'SSC CGL'
];

export default function NoteForm({ onGenerated }: NoteFormProps) {
  const { user } = useAuth();
  const [topics, setTopics] = useState('');
  const [domain, setDomain] = useState<Domain>('School');
  const [subLevel, setSubLevel] = useState<string>('Class 10');
  const [loading, setLoading] = useState(false);

  const handleDomainChange = (value: Domain) => {
    setDomain(value);
    if (value === 'School') setSubLevel('Class 10');
    else if (value === 'College') setSubLevel('Semester 1');
    else if (value === 'Competitive Exam') setSubLevel('NEET');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topics.trim()) {
      toast.error('Please enter at least one topic');
      return;
    }

    setLoading(true);
    try {
      const result = await generateNotes(topics, domain, subLevel, user?.id);
      if (result.success && result.data) {
        onGenerated(result.data);
        toast.success('Notes generated successfully!');
      } else {
        toast.error(result.error || 'Failed to generate notes');
      }
    } catch (error) {
      toast.error('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6 mb-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <Label className="text-base font-semibold text-zinc-950">Select Level</Label>
          <RadioGroup
            value={domain}
            onValueChange={(value) => handleDomainChange(value as Domain)}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className={`flex items-center space-x-3 p-3 rounded-xl border transition-all cursor-pointer ${domain === 'School' ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-200' : 'bg-gray-50/50 hover:bg-gray-50'}`} onClick={() => handleDomainChange('School')}>
              <RadioGroupItem value="School" id="school" className="sr-only" />
              <BookOpen className={`h-5 w-5 ${domain === 'School' ? 'text-indigo-600' : 'text-gray-400'}`} />
              <Label htmlFor="school" className="cursor-pointer font-medium">School</Label>
            </div>
            <div className={`flex items-center space-x-3 p-3 rounded-xl border transition-all cursor-pointer ${domain === 'College' ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-200' : 'bg-gray-50/50 hover:bg-gray-50'}`} onClick={() => handleDomainChange('College')}>
              <RadioGroupItem value="College" id="college" className="sr-only" />
              <GraduationCap className={`h-5 w-5 ${domain === 'College' ? 'text-indigo-600' : 'text-gray-400'}`} />
              <Label htmlFor="college" className="cursor-pointer font-medium">College</Label>
            </div>
            <div className={`flex items-center space-x-3 p-3 rounded-xl border transition-all cursor-pointer ${domain === 'Competitive Exam' ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-200' : 'bg-gray-50/50 hover:bg-gray-50'}`} onClick={() => handleDomainChange('Competitive Exam')}>
              <RadioGroupItem value="Competitive Exam" id="competitive" className="sr-only" />
              <Trophy className={`h-5 w-5 ${domain === 'Competitive Exam' ? 'text-indigo-600' : 'text-gray-400'}`} />
              <Label htmlFor="competitive" className="cursor-pointer font-medium">Competitive</Label>
            </div>
          </RadioGroup>
        </div>

        <div className="space-y-3 animate-in fade-in slide-in-from-top-2 duration-300">
          <Label className="text-sm font-medium text-gray-700">
            {domain === 'School' ? 'Select Class' : domain === 'College' ? 'Select Semester' : 'Select Exam'}
          </Label>
          <Select value={subLevel} onValueChange={setSubLevel}>
            <SelectTrigger className="w-full bg-gray-50/50">
              <SelectValue placeholder={`Select ${domain === 'School' ? 'Class' : domain === 'College' ? 'Semester' : 'Exam'}`} />
            </SelectTrigger>
            <SelectContent>
              {domain === 'School' && SCHOOL_CLASSES.map((cls) => (
                <SelectItem key={cls} value={cls}>{cls}</SelectItem>
              ))}
              {domain === 'College' && COLLEGE_SEMESTERS.map((sem) => (
                <SelectItem key={sem} value={sem}>{sem}</SelectItem>
              ))}
              {domain === 'Competitive Exam' && COMPETITIVE_EXAMS.map((exam) => (
                <SelectItem key={exam} value={exam}>{exam}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="topics" className="text-base font-semibold">
            Enter Topics
          </Label>
          <Textarea
            id="topics"
            placeholder="e.g. Photosynthesis, Respiration, Cell Division"
            className="min-h-[120px] resize-none text-base bg-gray-50/50 focus:bg-white transition-colors"
            value={topics}
            onChange={(e) => setTopics(e.target.value)}
          />
          <p className="text-sm text-gray-500">
            Separate multiple topics with commas
          </p>
        </div>

        <Button 
          type="submit" 
          className="w-full h-12 text-lg font-semibold bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md shadow-indigo-200"
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Generating {subLevel} Notes...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-5 w-5" />
              Generate Study Notes
            </>
          )}
        </Button>
      </form>
    </div>
  );
}
