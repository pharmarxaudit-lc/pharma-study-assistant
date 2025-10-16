// API Service for Pharmacy Exam Prep
// Handles all HTTP requests to the Flask backend

const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:5001'

// Type definitions
export interface SessionConfig {
  file_id: string
  session_type: 'study' | 'practice' | 'mock'
  num_questions: number
  topic_filter?: string[]
  difficulty_filter?: 'basic' | 'intermediate' | 'advanced'
  prioritize_weak?: boolean
}

export interface Question {
  id: number
  topic_name: string
  difficulty: 'basic' | 'intermediate' | 'advanced'
  question_type: 'single_answer' | 'choose_all'
  question_text: string
  options: {
    [key: string]: string
  }
  correct_answer: string
  explanation: string
  key_terms: {
    [key: string]: string
  }
  regulatory_context?: string
}

export interface SessionStartResponse {
  session_id: number
  file_id: string
  session_type: string
  total_questions: number
  current_question_number: number
  first_question: Question
}

export interface AnswerResponse {
  is_correct: boolean
  correct_answer: string
  explanation: string
  key_terms: {
    [key: string]: string
  }
  regulatory_context?: string
  current_question_number: number
  total_questions: number
  next_question?: Question
  session_complete: boolean
}

export interface SessionResults {
  session_id: number
  session_type: string
  score: number
  total: number
  percentage: number
  duration_seconds: number
  topic_breakdown: Array<{
    topic: string
    correct: number
    total: number
    percentage: number
  }>
  attempts: Array<{
    question_id: number
    topic_name: string
    difficulty: string
    question_text: string
    options: { [key: string]: string }
    selected_answer: string
    correct_answer: string
    is_correct: boolean
    explanation: string
    time_spent_seconds: number
  }>
}

export interface QuestionStats {
  total: number
  by_topic: Array<{
    topic_name: string
    count: number
  }>
  by_difficulty: Array<{
    difficulty: string
    count: number
  }>
  by_type: Array<{
    question_type: string
    count: number
  }>
}

// API Functions
export const api = {
  // Start a new study session
  async startSession(config: SessionConfig): Promise<SessionStartResponse> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to start session')
    }

    return response.json()
  },

  // Submit an answer
  async submitAnswer(
    sessionId: number,
    questionId: number,
    selectedAnswer: string
  ): Promise<AnswerResponse> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question_id: questionId,
        selected_answer: selectedAnswer,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to submit answer')
    }

    return response.json()
  },

  // Get session results
  async getSessionResults(sessionId: number): Promise<SessionResults> {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/results`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to get session results')
    }

    return response.json()
  },

  // Get question statistics for a file
  async getQuestionStats(fileId: string): Promise<QuestionStats> {
    const response = await fetch(`${API_BASE_URL}/api/questions/${fileId}/stats`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to get question stats')
    }

    return response.json()
  },

  // Get session history
  async getSessionHistory(limit: number = 10) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/history?limit=${limit}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to get session history')
    }

    return response.json()
  },
}
