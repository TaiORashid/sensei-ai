// Types for the JSON structure
export interface Subtopic {
  id: string;
  title: string;
  page_reference: number;
  char_start: number;
  char_end: number;
}

export interface Topic {
  id: string;
  title: string;
  subtopics: Subtopic[];
  page_range: number[];
}

export interface Choice {
  choice_id: string;
  text: string;
  is_correct: boolean;
  explanation: string;
}

export interface Question {
  question_id: string;
  question_text: string;
  choices: Choice[];
  topic_id: string;
  difficulty: string;
  page_reference: number;
}

export interface TopicExplanation {
  topic_id: string;
  topic_title: string;
  explanation: string;
  prerequisite_concepts: string[];
  next_steps: string[];
  related_topics: string[];
}

export interface DashboardData {
  structure: {
    topics: Topic[];
    document_title: string;
  };
  explanations: {
    overarching_explanation: string;
    topic_explanations: TopicExplanation[];
  };
  quiz: {
    questions: Question[];
  };
}

// Load and parse the JSON data
export async function loadDashboardData(): Promise<DashboardData | null> {
  try {
    const response = await fetch('/DSAoutputEX.json');
    if (!response.ok) {
      console.error('Failed to load dashboard data');
      return null;
    }
    const data = await response.json();
    return data.data as DashboardData;
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    return null;
  }
}

// Find topic by ID
export function findTopicById(data: DashboardData, topicId: string): Topic | undefined {
  return data.structure.topics.find((topic) => topic.id === topicId);
}

// Find subtopic by ID
export function findSubtopicById(data: DashboardData, subtopicId: string): { topic: Topic; subtopic: Subtopic } | undefined {
  for (const topic of data.structure.topics) {
    const subtopic = topic.subtopics.find((sub) => sub.id === subtopicId);
    if (subtopic) {
      return { topic, subtopic };
    }
  }
  return undefined;
}

// Get explanation for a topic
export function getTopicExplanation(data: DashboardData, topicId: string): string | null {
  const explanation = data.explanations.topic_explanations.find(
    (exp) => exp.topic_id === topicId
  );
  return explanation?.explanation || null;
}

// Get explanation for a subtopic (currently falls back to parent topic)
export function getSubtopicExplanation(data: DashboardData, subtopicId: string): string | null {
  const result = findSubtopicById(data, subtopicId);
  if (!result) return null;
  
  // Try to find subtopic-specific explanation first (if it exists in future)
  // For now, fall back to parent topic explanation
  return getTopicExplanation(data, result.topic.id);
}

// Get questions for a topic
export function getTopicQuestions(data: DashboardData, topicId: string): Question[] {
  return data.quiz.questions.filter((q) => q.topic_id === topicId);
}

// Get questions for a subtopic (currently falls back to parent topic)
export function getSubtopicQuestions(data: DashboardData, subtopicId: string): Question[] {
  const result = findSubtopicById(data, subtopicId);
  if (!result) return [];
  
  // Try to find subtopic-specific questions first (if they exist in future)
  // For now, fall back to parent topic questions
  return getTopicQuestions(data, result.topic.id);
}

// Convert question format for Quiz component
export function convertQuestionToQuizFormat(question: Question) {
  return {
    questionId: question.question_id,
    question: question.question_text,
    answers: question.choices.map((choice) => ({
      id: choice.choice_id,
      text: choice.text,
      isCorrect: choice.is_correct,
      explanation: choice.explanation,
    })),
  };
}

