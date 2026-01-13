export interface TopicNote {
  title: string;
  introduction: string;
  sections: {
    heading: string;
    content: string;
  }[];
  definitions: {
    term: string;
    definition: string;
  }[];
  examples: {
    title: string;
    code?: string;
    explanation: string;
  }[];
  diagramDescription?: string;
  summary: string;
  practiceQuestions: {
    question: string;
    type: 'short' | 'long' | 'mcq' | 'numerical' | 'coding';
    options?: string[];
    correctAnswer?: string;
    starterCode?: string;
    solution?: string;
  }[];
}

export interface GeneratedNotes {
  domain: 'School' | 'College' | 'Competitive Exam';
  subLevel?: string;
  topics: string[];
  notes: TopicNote[];
}
