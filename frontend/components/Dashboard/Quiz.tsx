"use client";

import { useState, useEffect } from "react";

interface Answer {
  id: string;
  text: string;
  isCorrect: boolean;
  explanation: string;
}

interface QuizProps {
  question: string;
  answers: Answer[];
  onAnswerSelect?: (explanation: string) => void;
  onNext?: () => void;
  isComplete?: boolean;
}

export default function Quiz({ question, answers, onAnswerSelect, onNext, isComplete }: QuizProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [correctAnswerId, setCorrectAnswerId] = useState<string | null>(null);
  const [selectedExplanation, setSelectedExplanation] = useState<string | null>(null);

  // Reset when question changes
  useEffect(() => {
    setSelectedAnswer(null);
    setCorrectAnswerId(null);
    setSelectedExplanation(null);
  }, [question]);

  const handleAnswerClick = (answerId: string, isCorrect: boolean, explanation: string) => {
    if (selectedAnswer) return; // Prevent multiple selections

    setSelectedAnswer(answerId);
    setSelectedExplanation(explanation);
    
    if (isCorrect) {
      setCorrectAnswerId(answerId);
    } else {
      // Find the correct answer
      const correct = answers.find((a) => a.isCorrect);
      if (correct) {
        setCorrectAnswerId(correct.id);
      }
    }

    // Notify parent of the selected explanation
    if (onAnswerSelect) {
      onAnswerSelect(explanation);
    }
  };

  const handleNext = () => {
    if (selectedAnswer && onNext) {
      onNext();
    }
  };

  const getButtonStyle = (answer: Answer) => {
    if (!selectedAnswer) {
      return "bg-gray-800 text-white border-2 border-gray-600 hover:border-gray-500";
    }

    // Correct answer always shows green
    if (answer.isCorrect) {
      return "bg-green-600 text-white border-2 border-green-600";
    }

    // All incorrect answers show red
    return "bg-red-500 text-black border-2 border-red-500";
  };

  if (isComplete) {
    return (
      <div className="w-full h-full bg-gray-800 rounded-xl p-6 shadow-lg flex items-center justify-center">
        <p className="text-white text-2xl dm-sans-button font-bold">All questions answered!</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-gray-800 rounded-xl p-6 shadow-lg overflow-y-auto flex flex-col">
      <div className="flex-1">
        <h3 className="text-xl font-bold mb-4 text-white dm-sans-button">Question</h3>
        <p className="text-gray-300 mb-6 leading-relaxed dm-sans-button font-normal">
          {question || "No question available."}
        </p>
        <div className="space-y-3 mb-6">
          {answers.map((answer) => (
            <button
              key={answer.id}
              onClick={() => handleAnswerClick(answer.id, answer.isCorrect, answer.explanation)}
              disabled={!!selectedAnswer}
              className={`w-full text-left px-6 py-4 rounded-lg transition-all duration-200 dm-sans-button font-medium ${getButtonStyle(answer)} ${
                selectedAnswer ? "cursor-default" : "cursor-pointer hover:shadow-md"
              }`}
            >
              {answer.text}
            </button>
          ))}
        </div>
      </div>
      
      {/* Next Button */}
      <button
        onClick={handleNext}
        disabled={!selectedAnswer}
        className={`w-full px-6 py-4 rounded-lg transition-all duration-200 dm-sans-button font-medium ${
          selectedAnswer
            ? "bg-white text-black hover:bg-gray-100 cursor-pointer"
            : "bg-gray-600 text-gray-400 cursor-not-allowed"
        }`}
      >
        Next
      </button>
    </div>
  );
}

