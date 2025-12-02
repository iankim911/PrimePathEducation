"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, Clock, BookOpen, Award, Home } from 'lucide-react'

interface ExamCompletedScreenProps {
  studentName: string
  examTitle: string
  sessionId: string
}

export function ExamCompletedScreen({ studentName, examTitle, sessionId }: ExamCompletedScreenProps) {
  const [submissionTime] = useState(new Date())
  const [showConfetti, setShowConfetti] = useState(true)

  useEffect(() => {
    // Hide confetti after animation
    const timer = setTimeout(() => {
      setShowConfetti(false)
    }, 3000)

    return () => clearTimeout(timer)
  }, [])

  const formatSubmissionTime = (date: Date) => {
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      {/* Confetti effect */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-10">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-ping"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: '1s'
              }}
            >
              <div className={`w-2 h-2 rounded-full ${
                ['bg-green-400', 'bg-blue-400', 'bg-yellow-400', 'bg-red-400', 'bg-purple-400'][Math.floor(Math.random() * 5)]
              }`} />
            </div>
          ))}
        </div>
      )}

      <div className="w-full max-w-2xl">
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="text-center pb-6">
            <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle2 className="h-12 w-12 text-green-600" />
            </div>
            
            <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
              Exam Completed Successfully!
            </CardTitle>
            
            <CardDescription className="text-lg text-gray-600">
              Congratulations {studentName}, you have successfully submitted your exam.
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Exam Details */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <BookOpen className="h-6 w-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">Exam Details</h3>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Exam Title:</span>
                  <span className="font-medium text-gray-900">{examTitle}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Session ID:</span>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    {sessionId.slice(-8)}
                  </Badge>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Submitted:</span>
                  <div className="flex items-center space-x-2 text-gray-900">
                    <Clock className="h-4 w-4" />
                    <span className="font-medium">{formatSubmissionTime(submissionTime)}</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Status:</span>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Submitted
                  </Badge>
                </div>
              </div>
            </div>

            {/* Results Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-3">
                <Award className="h-6 w-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">Results</h3>
              </div>
              
              <p className="text-gray-700 leading-relaxed">
                Your exam has been successfully submitted and recorded. Results will be available 
                once your teacher has reviewed and graded your responses. You will be notified 
                when your results are ready.
              </p>
            </div>

            {/* Next Steps */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">What's Next?</h3>
              
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                  <span>Your teacher will review and grade your responses</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                  <span>Results will be available in your student portal</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                  <span>You may receive feedback on your performance</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                  <span>Contact your teacher if you have any questions</span>
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 pt-4">
              <Button
                onClick={() => window.close()}
                variant="outline"
                className="flex-1 h-12 text-lg"
              >
                <Home className="h-5 w-5 mr-2" />
                Close Window
              </Button>
              
              <Button
                onClick={() => window.print()}
                variant="outline"
                className="flex-1 h-12 text-lg"
              >
                Print Receipt
              </Button>
            </div>

            {/* Footer Message */}
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-gray-500 text-sm">
                Thank you for completing your exam. Good luck with your results!
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Technical Info */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Submission ID: {sessionId} • {submissionTime.toISOString()}
          </p>
        </div>
      </div>
    </div>
  )
}