"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Target, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  HelpCircle,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react'

interface QuestionAnalytics {
  question_id: string
  question_text: string
  correct_rate: number
  average_time_seconds: number
  difficulty_level: 'easy' | 'medium' | 'hard'
  common_wrong_answers: string[]
}

interface QuestionAnalysisProps {
  questions: QuestionAnalytics[]
  totalAttempts: number
}

export function QuestionAnalysis({ questions, totalAttempts }: QuestionAnalysisProps) {
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('difficulty_desc')

  // Filter and sort questions
  const filteredQuestions = questions
    .filter(question => difficultyFilter === 'all' || question.difficulty_level === difficultyFilter)
    .sort((a, b) => {
      switch (sortBy) {
        case 'correct_rate_asc':
          return a.correct_rate - b.correct_rate
        case 'correct_rate_desc':
          return b.correct_rate - a.correct_rate
        case 'time_asc':
          return a.average_time_seconds - b.average_time_seconds
        case 'time_desc':
          return b.average_time_seconds - a.average_time_seconds
        case 'difficulty_asc':
          const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 }
          return difficultyOrder[a.difficulty_level] - difficultyOrder[b.difficulty_level]
        case 'difficulty_desc':
          const difficultyOrderDesc = { 'easy': 3, 'medium': 2, 'hard': 1 }
          return difficultyOrderDesc[a.difficulty_level] - difficultyOrderDesc[b.difficulty_level]
        default:
          return b.correct_rate - a.correct_rate
      }
    })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'hard':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-600'
    }
  }

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return <TrendingDown className="h-4 w-4" />
      case 'medium':
        return <Minus className="h-4 w-4" />
      case 'hard':
        return <TrendingUp className="h-4 w-4" />
      default:
        return <HelpCircle className="h-4 w-4" />
    }
  }

  const getPerformanceColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600'
    if (rate >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPerformanceIcon = (rate: number) => {
    if (rate >= 80) return <CheckCircle2 className="h-4 w-4 text-green-500" />
    if (rate >= 60) return <Clock className="h-4 w-4 text-yellow-500" />
    return <AlertTriangle className="h-4 w-4 text-red-500" />
  }

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  // Calculate statistics
  const stats = {
    totalQuestions: questions.length,
    avgCorrectRate: questions.length > 0 ? questions.reduce((sum, q) => sum + q.correct_rate, 0) / questions.length : 0,
    avgTime: questions.length > 0 ? questions.reduce((sum, q) => sum + q.average_time_seconds, 0) / questions.length : 0,
    easyQuestions: questions.filter(q => q.difficulty_level === 'easy').length,
    mediumQuestions: questions.filter(q => q.difficulty_level === 'medium').length,
    hardQuestions: questions.filter(q => q.difficulty_level === 'hard').length,
    problematicQuestions: questions.filter(q => q.correct_rate < 50).length
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <HelpCircle className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-blue-600">Total Questions</p>
                <p className="text-2xl font-bold text-blue-900">{stats.totalQuestions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-green-600">Avg Correct Rate</p>
                <p className="text-2xl font-bold text-green-900">{stats.avgCorrectRate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-orange-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-orange-600">Avg Time</p>
                <p className="text-2xl font-bold text-orange-900">{formatTime(Math.round(stats.avgTime))}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-sm text-red-600">Problematic</p>
                <p className="text-2xl font-bold text-red-900">{stats.problematicQuestions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Difficulty Distribution */}
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-gray-900">Difficulty Distribution</CardTitle>
          <CardDescription>Breakdown of questions by difficulty level</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <TrendingDown className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-900">Easy</span>
              </div>
              <p className="text-2xl font-bold text-green-900">{stats.easyQuestions}</p>
              <p className="text-sm text-green-600">
                {stats.totalQuestions > 0 ? ((stats.easyQuestions / stats.totalQuestions) * 100).toFixed(1) : 0}%
              </p>
            </div>

            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Minus className="h-5 w-5 text-yellow-600" />
                <span className="font-medium text-yellow-900">Medium</span>
              </div>
              <p className="text-2xl font-bold text-yellow-900">{stats.mediumQuestions}</p>
              <p className="text-sm text-yellow-600">
                {stats.totalQuestions > 0 ? ((stats.mediumQuestions / stats.totalQuestions) * 100).toFixed(1) : 0}%
              </p>
            </div>

            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <TrendingUp className="h-5 w-5 text-red-600" />
                <span className="font-medium text-red-900">Hard</span>
              </div>
              <p className="text-2xl font-bold text-red-900">{stats.hardQuestions}</p>
              <p className="text-sm text-red-600">
                {stats.totalQuestions > 0 ? ((stats.hardQuestions / stats.totalQuestions) * 100).toFixed(1) : 0}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Question Details */}
      <Card className="bg-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-gray-900">Question Performance Analysis</CardTitle>
              <CardDescription>Detailed breakdown of individual question performance</CardDescription>
            </div>

            <div className="flex items-center space-x-3">
              <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Filter difficulty" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="all">All Difficulties</SelectItem>
                  <SelectItem value="easy">Easy</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="hard">Hard</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="correct_rate_desc">Highest Success Rate</SelectItem>
                  <SelectItem value="correct_rate_asc">Lowest Success Rate</SelectItem>
                  <SelectItem value="time_desc">Most Time Consuming</SelectItem>
                  <SelectItem value="time_asc">Least Time Consuming</SelectItem>
                  <SelectItem value="difficulty_desc">Hardest First</SelectItem>
                  <SelectItem value="difficulty_asc">Easiest First</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="space-y-4">
            {filteredQuestions.map((question, index) => (
              <div key={question.question_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="font-medium text-gray-900">Question {index + 1}</span>
                      <Badge variant="secondary" className={getDifficultyColor(question.difficulty_level)}>
                        {getDifficultyIcon(question.difficulty_level)}
                        <span className="ml-1 capitalize">{question.difficulty_level}</span>
                      </Badge>
                      {getPerformanceIcon(question.correct_rate)}
                    </div>
                    <p className="text-gray-700 text-sm mb-3 leading-relaxed">
                      {question.question_text.length > 200 
                        ? `${question.question_text.substring(0, 200)}...`
                        : question.question_text}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {/* Success Rate */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Success Rate</span>
                      <span className={`text-sm font-bold ${getPerformanceColor(question.correct_rate)}`}>
                        {question.correct_rate.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={question.correct_rate} className="h-2" />
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round((question.correct_rate / 100) * totalAttempts)} of {totalAttempts} correct
                    </p>
                  </div>

                  {/* Average Time */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Average Time</span>
                      <span className="text-sm font-bold text-gray-900">
                        {formatTime(question.average_time_seconds)}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-orange-500 h-2 rounded-full" 
                          style={{ width: `${Math.min(100, (question.average_time_seconds / 180) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {question.average_time_seconds > 120 ? 'Above average' : 'Below average'}
                    </p>
                  </div>

                  {/* Common Wrong Answers */}
                  <div>
                    <span className="text-sm font-medium text-gray-600 block mb-2">Common Wrong Answers</span>
                    {question.common_wrong_answers.length > 0 ? (
                      <div className="space-y-1">
                        {question.common_wrong_answers.slice(0, 2).map((answer, idx) => (
                          <div key={idx} className="text-xs bg-red-50 text-red-700 px-2 py-1 rounded">
                            {answer.length > 30 ? `${answer.substring(0, 30)}...` : answer}
                          </div>
                        ))}
                        {question.common_wrong_answers.length > 2 && (
                          <p className="text-xs text-gray-500">
                            +{question.common_wrong_answers.length - 2} more
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-500">No common patterns</p>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {filteredQuestions.length === 0 && (
              <div className="text-center py-8">
                <HelpCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Questions Found</h3>
                <p className="text-gray-600">
                  Try adjusting your difficulty filter to see more results.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}