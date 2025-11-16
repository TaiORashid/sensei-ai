"use client";

import Sidebar from "@/components/Dashboard/Sidebar";
import PDFViewer from "@/components/Dashboard/PDFViewer";
import Explanation from "@/components/Dashboard/Explanation";
import Quiz from "@/components/Dashboard/Quiz";
import { useState, useEffect } from "react";
import {
  loadDashboardData,
  findSubtopicById,
  getSubtopicExplanation,
  getSubtopicQuestions,
  convertQuestionToQuizFormat,
  type DashboardData,
  type Topic,
} from "@/utils/dashboardData";

interface QuestionStackItem {
  questionId: string;
  question: string;
  answers: Array<{ id: string; text: string; isCorrect: boolean; explanation: string }>;
}

export default function DashboardPage() {
  const [pdfFile, setPdfFile] = useState<File | string | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [selectedSubtopicId, setSelectedSubtopicId] = useState<string | null>(null);
  const [pdfPageNumber, setPdfPageNumber] = useState<number | undefined>(undefined);
  const [explanationText, setExplanationText] = useState<string>("");
  const [questionStack, setQuestionStack] = useState<QuestionStackItem[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [questionsComplete, setQuestionsComplete] = useState<boolean>(false);

  // Load PDF file
  useEffect(() => {
    const storedFile = sessionStorage.getItem("uploadedPDF");
    if (storedFile) {
      setPdfFile(storedFile);
    }
  }, []);

  // Load JSON data
  useEffect(() => {
    loadDashboardData().then((data) => {
      if (data) {
        setDashboardData(data);
        // Set default to first topic's first subtopic
        if (data.structure.topics.length > 0 && data.structure.topics[0].subtopics.length > 0) {
          const firstSubtopic = data.structure.topics[0].subtopics[0];
          setSelectedSubtopicId(firstSubtopic.id);
        }
      }
    });
  }, []);

  // Update question stack when subtopic changes
  useEffect(() => {
    if (!dashboardData || !selectedSubtopicId) return;

    // Get questions for the subtopic (falls back to parent topic if subtopic-specific doesn't exist)
    const questions = getSubtopicQuestions(dashboardData, selectedSubtopicId);
    
    if (questions.length > 0) {
      // Convert all questions to the stack format
      const stack = questions.map((q) => convertQuestionToQuizFormat(q));
      setQuestionStack(stack);
      setCurrentQuestionIndex(0);
      setQuestionsComplete(false);
      
      // Reset explanation to topic explanation initially
      const explanation = getSubtopicExplanation(dashboardData, selectedSubtopicId);
      setExplanationText(explanation || "No explanation available.");
    } else {
      setQuestionStack([]);
      setCurrentQuestionIndex(0);
      setQuestionsComplete(false);
      setExplanationText("No questions available for this subtopic.");
    }
  }, [dashboardData, selectedSubtopicId]);

  // Get subtopics with page references for sidebar
  const topicsWithPageRefs: Topic[] = dashboardData
    ? dashboardData.structure.topics.map((topic) => ({
        ...topic,
        subtopics: topic.subtopics.map((subtopic) => ({
          id: subtopic.id,
          title: subtopic.title,
          page_reference: subtopic.page_reference,
        })),
      }))
    : [];

  const handleAnswerSelect = (explanation: string) => {
    setExplanationText(explanation);
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questionStack.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      // Reset explanation to topic explanation for new question
      if (dashboardData && selectedSubtopicId) {
        const explanation = getSubtopicExplanation(dashboardData, selectedSubtopicId);
        setExplanationText(explanation || "No explanation available.");
      }
    } else {
      // All questions answered
      setQuestionsComplete(true);
      setExplanationText("All questions have been answered!");
    }
  };

  // Get main topic and topics from data
  const mainTopic = dashboardData?.structure.document_title || "Trees";
  const topics: Topic[] = dashboardData?.structure.topics || [];

  const handleSubtopicClick = (subtopicId: string, pageReference?: number) => {
    setSelectedSubtopicId(subtopicId);
    // Navigate to the page reference in PDF
    if (pageReference && pageReference > 0) {
      setPdfPageNumber(pageReference);
    }
  };

  return (
    <div className="h-screen bg-black flex overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        mainTopic={mainTopic}
        topics={topicsWithPageRefs}
        onSubtopicClick={handleSubtopicClick}
        selectedSubtopicId={selectedSubtopicId}
      />

      {/* Main Content - split into two halves */}
      <div className="flex-1 ml-64 flex gap-6 p-6">
        {/* Left half - PDF Viewer */}
        <div className="w-1/2 h-full">
          <PDFViewer file={pdfFile} pageNumber={pdfPageNumber} />
        </div>

        {/* Right half - Explanation and Quiz stacked */}
        <div className="w-1/2 h-full flex flex-col gap-6">
          {/* Explanation Container - top half */}
          <div className="h-1/2">
            <Explanation text={explanationText} />
          </div>

          {/* Quiz Container - bottom half */}
          <div className="h-1/2">
            {questionStack.length > 0 && currentQuestionIndex < questionStack.length ? (
              <Quiz
                key={`${selectedSubtopicId}-${currentQuestionIndex}`}
                question={questionStack[currentQuestionIndex].question}
                answers={questionStack[currentQuestionIndex].answers}
                onAnswerSelect={handleAnswerSelect}
                onNext={handleNextQuestion}
                isComplete={false}
              />
            ) : questionsComplete ? (
              <Quiz
                question=""
                answers={[]}
                isComplete={true}
              />
            ) : (
              <div className="w-full h-full bg-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-center">
                <p className="text-gray-400 dm-sans-button">No questions available for this subtopic.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
