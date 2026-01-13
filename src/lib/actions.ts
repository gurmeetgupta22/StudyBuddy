'use server';

import { GoogleGenerativeAI } from '@google/generative-ai';
import { supabase } from './supabase';
import { GeneratedNotes, TopicNote } from '@/types';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function generateNotes(
  topics: string, 
  domain: 'School' | 'College' | 'Competitive Exam', 
  subLevel?: string,
  userId?: string
) {
  try {
    const topicList = topics.split(',').map((t) => t.trim()).filter((t) => t.length > 0);
    
    if (topicList.length === 0) {
      throw new Error('Please enter at least one topic');
    }

    const model = genAI.getGenerativeModel({ 
      model: "gemini-flash-latest",
      generationConfig: {
        responseMimeType: "application/json",
      }
    });

    const levelContext = subLevel ? `${domain} (${subLevel})` : domain;

    const prompt = `
      You are an elite academic textbook author and expert educator. Your task is to generate perfect, comprehensive, book-like study notes for ${levelContext} level students.
      
      The notes must follow these high-quality standards:
      - Academic Rigor: Use precise, professional language appropriate for the ${levelContext} level.
      - Logical Structure: Each topic should flow naturally from foundational concepts to complex applications.
      - Visual Clarity: Use clear headings and organized sections.
      - Pedagogical Value: Include deep explanations, not just surface-level facts.
      
For each of these topics: ${topicList.join(', ')}, generate:
1. Title: A formal, textbook-style chapter title.
2. Introduction: A broad overview and the "Why this matters" context.
3. Structured Sections: Deep-dive headings and subheadings. Content should be detailed, clear, and comprehensive.
4. Key Definitions: Crucial terminology with exact academic definitions.
5. Step-by-Step Explanations: Complex processes broken down into logical sequences.
6. Examples: Provide AT LEAST 5 high-quality, illustrative examples for each topic. 
- Each example must have a descriptive 'title'.
- CONTEXTUAL CONTENT: ONLY provide 'code' snippets if the topic is programming/CS. ONLY provide 'formula' or LaTeX if the topic is Math/Science.
- For Humanities (History, Literature, etc.), provide descriptive real-world scenarios or historical case studies as examples INSTEAD of code/formulas.
- Each example MUST have a detailed 'explanation' that bridges theory and practice.
7. Diagram Description: A detailed, clear description of what a professional diagram for this topic should illustrate.
8. Summary: A "Takeaway" section summarizing core concepts.
9. Practice Questions: Generate a diverse set of AT LEAST 8 practice questions including:
- Multiple Choice Questions (MCQs): Include 'options' and 'correctAnswer'.
- Coding Practice/Problem Solving: ONLY for CS/Math/Science topics. For others, provide 'Critical Thinking' or 'Analytical' questions instead.
- Short/Long Answer Questions: For conceptual understanding.


      The output MUST be a JSON object matching this TypeScript interface:
      interface TopicNote {
        title: string;
        introduction: string;
        sections: { heading: string; content: string; }[];
        definitions: { term: string; definition: string; }[];
        examples: { title: string; code?: string; explanation: string; }[];
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
      interface Response {
        notes: TopicNote[];
      }

      Context for ${domain} level:
      - School: Focus on clarity, foundational principles, and engaging pedagogical tone. Tailor depth to ${subLevel || 'the specified grade'}.
      - College: Focus on technical depth, theoretical frameworks, formal analysis, and advanced problem-solving techniques. Tailor to ${subLevel || 'university level'}.
      - Competitive Exam: Focus on high-yield concepts, exam-specific patterns, shortcuts (if applicable), and rigorous problem-solving typical of ${subLevel || 'competitive exams'}.
    `;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    const parsedData = JSON.parse(text) as { notes: TopicNote[] };
    
    const generatedNotes: GeneratedNotes = {
      domain,
      subLevel,
      topics: topicList,
      notes: parsedData.notes,
    };

    // Save to Supabase
    const insertData: any = {
      domain: subLevel ? `${domain} - ${subLevel}` : domain,
      topics: topics,
      content: generatedNotes,
    };

    if (userId) {
      insertData.user_id = userId;
    }

    const { data, error } = await supabase
      .from('notes')
      .insert([insertData])
      .select()
      .single();

    if (error) {
      console.error('Error saving to Supabase:', error);
    }

    return { success: true, data: generatedNotes, id: data?.id };
  } catch (error: any) {
    console.error('Generation error:', error);
    return { success: false, error: error.message || 'Failed to generate notes' };
  }
}

export async function getHistory(userId?: string) {
  try {
    let query = supabase
      .from('notes')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10);

    if (userId) {
      query = query.eq('user_id', userId);
    } else {
      query = query.is('user_id', null);
    }

    const { data, error } = await query;

    if (error) throw error;
    return { success: true, data };
  } catch (error: any) {
    console.error('History fetch error:', error);
    return { success: false, error: error.message };
  }
}

export async function getNoteById(id: string) {
  try {
    const { data, error } = await supabase
      .from('notes')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;
    return { success: true, data };
  } catch (error: any) {
    console.error('Fetch error:', error);
    return { success: false, error: error.message };
  }
}
