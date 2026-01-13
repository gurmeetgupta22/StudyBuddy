'use client';

import { useState } from 'react';
import { GeneratedNotes, TopicNote } from '@/types';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { Download, FileText, File as FilePdf, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';
import jsPDF from 'jspdf';
import { toast } from 'sonner';

interface NoteDisplayProps {
  data: GeneratedNotes;
}

export default function NoteDisplay({ data }: NoteDisplayProps) {
  const [showSolutions, setShowSolutions] = useState<{ [key: string]: boolean }>({});

  const toggleSolution = (chapterIndex: number, questionIndex: number) => {
    const key = `${chapterIndex}-${questionIndex}`;
    setShowSolutions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const downloadTxt = () => {
    let content = `STUDY NOTES - ${data.domain.toUpperCase()} LEVEL\n`;
    content += `Topics: ${data.topics.join(', ')}\n\n`;
    content += `========================================\n\n`;

    data.notes.forEach((note, index) => {
      content += `CHAPTER ${index + 1}: ${note.title.toUpperCase()}\n\n`;
      content += `INTRODUCTION\n${note.introduction}\n\n`;
      
      content += `KEY DEFINITIONS\n`;
      note.definitions.forEach(d => {
        content += `- ${d.term}: ${d.definition}\n`;
      });
      content += `\n`;

      note.sections.forEach(s => {
        content += `${s.heading.toUpperCase()}\n${s.content}\n\n`;
      });

      content += `EXAMPLES & EXPLANATIONS\n`;
      note.examples.forEach((e, i) => {
        content += `Example ${i + 1}: ${e.title}\n`;
        if (e.code) {
          content += `CODE:\n${e.code}\n\n`;
        }
        content += `EXPLANATION: ${e.explanation}\n\n`;
      });

      if (note.diagramDescription) {
        content += `DIAGRAM DESCRIPTION\n${note.diagramDescription}\n\n`;
      }

      content += `SUMMARY\n${note.summary}\n\n`;

      content += `PRACTICE QUESTIONS\n`;
      note.practiceQuestions.forEach((q, qIndex) => {
        content += `${qIndex + 1}. [${q.type.toUpperCase()}] ${q.question}\n`;
        if (q.options) {
          q.options.forEach((opt, optIdx) => {
            content += `   ${String.fromCharCode(65 + optIdx)}) ${opt}\n`;
          });
        }
        if (q.correctAnswer) content += `   Correct Answer: ${q.correctAnswer}\n`;
        if (q.starterCode) content += `   Starter Code:\n${q.starterCode}\n`;
        if (q.solution) content += `   Solution:\n${q.solution}\n`;
        content += `\n`;
      });
      content += `\n----------------------------------------\n\n`;
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Study_Notes_${data.topics[0].replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('TXT downloaded successfully');
  };

  const downloadPdf = () => {
    const doc = new jsPDF();
    let y = 20;
    const margin = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    const maxWidth = pageWidth - margin * 2;

    const addText = (text: string, fontSize: number = 10, isBold: boolean = false) => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');
      const lines = doc.splitTextToSize(text, maxWidth);
      
      if (y + lines.length * (fontSize / 2) > 280) {
        doc.addPage();
        y = 20;
      }
      
      doc.text(lines, margin, y);
      y += lines.length * (fontSize / 2) + 5;
    };

    // Title Page
    doc.setFontSize(22);
    doc.setFont('helvetica', 'bold');
    doc.text('STUDY BUDDY', pageWidth / 2, 100, { align: 'center' });
    doc.setFontSize(16);
    doc.text(`${data.domain.toUpperCase()} LEVEL NOTES`, pageWidth / 2, 115, { align: 'center' });
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text(`Topics: ${data.topics.join(', ')}`, pageWidth / 2, 130, { align: 'center' });
    
    doc.addPage();
    y = 20;

    data.notes.forEach((note, index) => {
      addText(`Chapter ${index + 1}: ${note.title}`, 18, true);
      addText('Introduction', 14, true);
      addText(note.introduction, 11);

      addText('Key Definitions', 14, true);
      note.definitions.forEach(d => {
        addText(`${d.term}: ${d.definition}`, 10);
      });

      note.sections.forEach(s => {
        addText(s.heading, 14, true);
        addText(s.content, 11);
      });

      addText('Examples & Explanations', 14, true);
      note.examples.forEach((e, i) => {
        addText(`Example ${i + 1}: ${e.title}`, 11, true);
        if (e.code) {
          addText('Code:', 10, true);
          addText(e.code, 9);
        }
        addText('Explanation:', 10, true);
        addText(e.explanation, 10);
      });

      if (note.diagramDescription) {
        addText('Diagram Description', 14, true);
        addText(note.diagramDescription, 10);
      }

      addText('Summary', 14, true);
      addText(note.summary, 11);

      addText('Practice Questions', 14, true);
      note.practiceQuestions.forEach((q, qIndex) => {
        addText(`${qIndex + 1}. [${q.type.toUpperCase()}] ${q.question}`, 10);
        if (q.options) {
          q.options.forEach((opt, optIdx) => {
            addText(`   ${String.fromCharCode(65 + optIdx)}) ${opt}`, 9);
          });
        }
      });

      if (index < data.notes.length - 1) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save(`Study_Notes_${data.topics[0].replace(/\s+/g, '_')}.pdf`);
    toast.success('PDF downloaded successfully');
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-indigo-50 p-4 rounded-xl border border-indigo-100">
          <div>
            <h2 className="text-xl font-bold text-indigo-900">Generated Notes</h2>
            <p className="text-indigo-600 font-medium">
              {data.domain}{data.subLevel ? ` (${data.subLevel})` : ''} Level • {data.notes.length} Topics
            </p>
          </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={downloadTxt} className="bg-white">
            <FileText className="mr-2 h-4 w-4" />
            TXT
          </Button>
          <Button variant="outline" size="sm" onClick={downloadPdf} className="bg-white">
            <FilePdf className="mr-2 h-4 w-4" />
            PDF
          </Button>
        </div>
      </div>

      <Accordion type="single" collapsible className="w-full space-y-4">
        {data.notes.map((note, index) => (
          <AccordionItem 
            key={index} 
            value={`item-${index}`}
            className="border rounded-xl bg-white px-4 overflow-hidden shadow-sm"
          >
            <AccordionTrigger className="hover:no-underline py-4">
              <span className="text-lg font-bold text-left">{note.title}</span>
            </AccordionTrigger>
            <AccordionContent className="pb-6 pt-2 space-y-6 text-gray-700 leading-relaxed">
              <section>
                <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-2">Introduction</h3>
                <p>{note.introduction}</p>
              </section>

              <section className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-2">Key Definitions</h3>
                <dl className="space-y-2">
                  {note.definitions.map((d, i) => (
                    <div key={i}>
                      <dt className="font-bold text-gray-900">{d.term}</dt>
                      <dd>{d.definition}</dd>
                    </div>
                  ))}
                </dl>
              </section>

              {note.sections.map((s, i) => (
                <section key={i}>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{s.heading}</h3>
                  <p>{s.content}</p>
                </section>
              ))}

              <section>
                <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-4">Examples & Explanations</h3>
                <div className="space-y-6">
                  {note.examples.map((e, i) => (
                    <div key={i} className="space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-900">{e.title || `Example ${i + 1}`}</span>
                        <div className="h-px flex-grow bg-gray-100"></div>
                      </div>
                      {e.code && (
                        <div className="relative group">
                          <pre className="relative bg-gray-900 text-indigo-100 p-4 rounded-lg overflow-x-auto font-mono text-sm shadow-inner">
                            <code>{e.code}</code>
                          </pre>
                        </div>
                      )}
                      <div className="text-gray-700 bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
                        <p className="italic leading-relaxed">
                          <span className="font-bold text-indigo-600 not-italic mr-2">Explanation:</span>
                          {e.explanation}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {note.diagramDescription && (
                <section className="border-l-4 border-indigo-200 pl-4 py-1 italic text-gray-600">
                  <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-2 not-italic">Visual Aid Description</h3>
                  <p>{note.diagramDescription}</p>
                </section>
              )}

              <section className="bg-indigo-50/50 p-4 rounded-lg border border-indigo-100">
                <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-2">Summary</h3>
                <p className="font-medium">{note.summary}</p>
              </section>

              <section>
                <h3 className="text-indigo-600 font-bold uppercase text-xs tracking-wider mb-4 border-b pb-2">Practice Questions</h3>
                <div className="space-y-6">
                  {note.practiceQuestions.map((q, qIndex) => {
                    const isSolutionVisible = showSolutions[`${index}-${qIndex}`];
                    return (
                      <div key={qIndex} className="bg-white border rounded-xl p-5 space-y-4 shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start gap-3">
                          <div className="flex gap-3">
                            <span className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold shadow-sm">
                              {qIndex + 1}
                            </span>
                            <div>
                              <p className="font-bold text-gray-900 text-lg">{q.question}</p>
                              <div className="inline-block px-2 py-0.5 mt-1 rounded bg-indigo-100 text-indigo-700 text-[10px] font-bold uppercase tracking-wider">
                                {q.type}
                              </div>
                            </div>
                          </div>
                        </div>

                        {q.type === 'mcq' && q.options && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-11">
                            {q.options.map((opt, optIdx) => (
                              <div key={optIdx} className="flex items-center p-3 rounded-lg border border-gray-200 bg-gray-50 text-gray-700 hover:border-indigo-300 transition-colors">
                                <span className="w-6 h-6 rounded-full bg-white border border-gray-300 flex items-center justify-center text-xs font-bold mr-3 text-gray-500">
                                  {String.fromCharCode(65 + optIdx)}
                                </span>
                                <span className="font-medium">{opt}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {q.type === 'coding' && q.starterCode && (
                          <div className="pl-11">
                            <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Starter Code</h4>
                            <pre className="bg-gray-800 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto">
                              <code>{q.starterCode}</code>
                            </pre>
                          </div>
                        )}

                        <div className="pl-11 pt-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => toggleSolution(index, qIndex)}
                            className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 p-0 h-auto font-bold flex items-center"
                          >
                            {isSolutionVisible ? (
                              <><ChevronUp className="w-4 h-4 mr-1" /> Hide Solution</>
                            ) : (
                              <><ChevronDown className="w-4 h-4 mr-1" /> View Solution</>
                            )}
                          </Button>
                          
                          {isSolutionVisible && (
                            <div className="mt-4 p-4 rounded-lg bg-emerald-50 border border-emerald-100 animate-in slide-in-from-top-2 duration-300">
                              <div className="flex items-center gap-2 mb-2">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">Solution</span>
                              </div>
                              <div className="text-gray-800 leading-relaxed">
                                {q.type === 'mcq' && q.correctAnswer && (
                                  <p className="font-bold text-lg mb-2 text-emerald-800">Correct Option: {q.correctAnswer}</p>
                                )}
                                {q.solution ? (
                                  q.type === 'coding' ? (
                                    <pre className="bg-gray-900 text-white p-3 rounded border border-emerald-200 text-xs font-mono mt-2 overflow-x-auto">
                                      <code>{q.solution}</code>
                                    </pre>
                                  ) : (
                                    <p>{q.solution}</p>
                                  )
                                ) : (
                                  <p>Solution details not provided in the generated content.</p>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
