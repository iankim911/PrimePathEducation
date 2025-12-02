"use client"

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar,
  Users,
  Target,
  Clock,
  BarChart3
} from 'lucide-react'

interface TrendData {
  date: string
  attempts: number
  average_score: number
  completion_rate: number
}

interface PerformanceTrendsProps {
  trends: TrendData[]
  examTitle: string
}

export function PerformanceTrends({ trends, examTitle }: PerformanceTrendsProps) {
  const [viewMode, setViewMode] = useState<string>('score')
  const [timeRange, setTimeRange] = useState<string>('30')

  // Filter trends by time range
  const filteredTrends = trends.filter(trend => {
    if (timeRange === 'all') return true
    const trendDate = new Date(trend.date)
    const cutoffDate = new Date()
    cutoffDate.setDate(cutoffDate.getDate() - parseInt(timeRange))
    return trendDate >= cutoffDate
  }).slice(-20) // Show last 20 data points for clarity

  const getMetricValue = (trend: TrendData, metric: string) => {
    switch (metric) {
      case 'score':
        return trend.average_score
      case 'completion':
        return trend.completion_rate
      case 'attempts':
        return trend.attempts
      default:
        return trend.average_score
    }
  }

  const getMetricLabel = (metric: string) => {
    switch (metric) {
      case 'score':
        return 'Average Score'
      case 'completion':
        return 'Completion Rate'
      case 'attempts':
        return 'Number of Attempts'
      default:
        return 'Average Score'
    }
  }

  const getMetricUnit = (metric: string) => {
    switch (metric) {
      case 'score':
      case 'completion':
        return '%'
      case 'attempts':
        return ''
      default:
        return '%'
    }
  }

  const getMetricColor = (metric: string) => {
    switch (metric) {
      case 'score':
        return 'bg-blue-500'
      case 'completion':
        return 'bg-green-500'
      case 'attempts':
        return 'bg-purple-500'
      default:
        return 'bg-blue-500'
    }
  }

  // Calculate trend statistics
  const calculateTrend = (data: number[]) => {
    if (data.length < 2) return { direction: 'stable', percentage: 0 }
    
    const first = data[0]
    const last = data[data.length - 1]
    const percentage = ((last - first) / first) * 100
    
    if (percentage > 5) return { direction: 'up', percentage }
    if (percentage < -5) return { direction: 'down', percentage }
    return { direction: 'stable', percentage }
  }

  const scoreData = filteredTrends.map(t => t.average_score)
  const completionData = filteredTrends.map(t => t.completion_rate)
  const attemptsData = filteredTrends.map(t => t.attempts)

  const scoreTrend = calculateTrend(scoreData)
  const completionTrend = calculateTrend(completionData)
  const attemptsTrend = calculateTrend(attemptsData)

  const maxValue = Math.max(...filteredTrends.map(t => getMetricValue(t, viewMode)))
  const minValue = Math.min(...filteredTrends.map(t => getMetricValue(t, viewMode)))

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-500" />
      default:
        return <BarChart3 className="h-4 w-4 text-gray-500" />
    }
  }

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (!trends || trends.length === 0) {
    return (
      <div className="space-y-6">
        <Card className="bg-white">
          <CardContent className="p-8 text-center">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Trend Data Available</h3>
            <p className="text-gray-600">
              Performance trends will appear here once students start completing exams over time.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Trend Summary */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Average Score Trend</p>
                <p className="text-2xl font-bold text-blue-900">
                  {scoreData.length > 0 ? scoreData[scoreData.length - 1].toFixed(1) : 0}%
                </p>
              </div>
              <div className="text-right">
                {getTrendIcon(scoreTrend.direction)}
                <p className={`text-sm font-medium ${getTrendColor(scoreTrend.direction)}`}>
                  {Math.abs(scoreTrend.percentage).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600">Completion Rate Trend</p>
                <p className="text-2xl font-bold text-green-900">
                  {completionData.length > 0 ? completionData[completionData.length - 1].toFixed(1) : 0}%
                </p>
              </div>
              <div className="text-right">
                {getTrendIcon(completionTrend.direction)}
                <p className={`text-sm font-medium ${getTrendColor(completionTrend.direction)}`}>
                  {Math.abs(completionTrend.percentage).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600">Attempts Trend</p>
                <p className="text-2xl font-bold text-purple-900">
                  {attemptsData.length > 0 ? attemptsData[attemptsData.length - 1] : 0}
                </p>
              </div>
              <div className="text-right">
                {getTrendIcon(attemptsTrend.direction)}
                <p className={`text-sm font-medium ${getTrendColor(attemptsTrend.direction)}`}>
                  {Math.abs(attemptsTrend.percentage).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Chart */}
      <Card className="bg-white">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-gray-900">Performance Trends Over Time</CardTitle>
              <CardDescription>Track exam performance patterns and improvements</CardDescription>
            </div>

            <div className="flex items-center space-x-3">
              <Select value={viewMode} onValueChange={setViewMode}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select metric" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="score">Average Score</SelectItem>
                  <SelectItem value="completion">Completion Rate</SelectItem>
                  <SelectItem value="attempts">Number of Attempts</SelectItem>
                </SelectContent>
              </Select>

              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Time range" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 90 days</SelectItem>
                  <SelectItem value="all">All time</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">
            {/* Chart Header */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded ${getMetricColor(viewMode)}`}></div>
                <span className="font-medium text-gray-900">{getMetricLabel(viewMode)}</span>
              </div>
              <div className="text-sm text-gray-600">
                Max: {maxValue.toFixed(1)}{getMetricUnit(viewMode)} • Min: {minValue.toFixed(1)}{getMetricUnit(viewMode)}
              </div>
            </div>

            {/* Simple Line Chart */}
            <div className="relative h-64 bg-gray-50 rounded-lg p-4">
              <div className="h-full flex items-end space-x-2 overflow-x-auto">
                {filteredTrends.map((trend, index) => {
                  const value = getMetricValue(trend, viewMode)
                  const height = ((value - minValue) / (maxValue - minValue || 1)) * 100
                  
                  return (
                    <div key={index} className="flex-1 min-w-8 flex flex-col items-center group">
                      <div className="relative mb-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                          {value.toFixed(1)}{getMetricUnit(viewMode)}
                          <br />
                          {new Date(trend.date).toLocaleDateString()}
                        </div>
                      </div>
                      <div 
                        className={`w-full ${getMetricColor(viewMode)} rounded-t transition-all hover:opacity-75`}
                        style={{ height: `${height}%`, minHeight: '4px' }}
                      ></div>
                      <div className="text-xs text-gray-500 mt-2 transform rotate-45 origin-left">
                        {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Data Table */}
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 mb-3">Recent Data Points</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-medium text-gray-700">Date</th>
                      <th className="text-left py-2 px-3 font-medium text-gray-700">Attempts</th>
                      <th className="text-left py-2 px-3 font-medium text-gray-700">Avg Score</th>
                      <th className="text-left py-2 px-3 font-medium text-gray-700">Completion Rate</th>
                      <th className="text-left py-2 px-3 font-medium text-gray-700">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTrends.slice(-10).reverse().map((trend, index) => {
                      const prevTrend = filteredTrends[filteredTrends.length - index - 2]
                      const scoreChange = prevTrend ? trend.average_score - prevTrend.average_score : 0
                      
                      return (
                        <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <div className="flex items-center space-x-2">
                              <Calendar className="h-4 w-4 text-gray-400" />
                              <span>{new Date(trend.date).toLocaleDateString()}</span>
                            </div>
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex items-center space-x-2">
                              <Users className="h-4 w-4 text-blue-400" />
                              <span>{trend.attempts}</span>
                            </div>
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex items-center space-x-2">
                              <Target className="h-4 w-4 text-green-400" />
                              <span>{trend.average_score.toFixed(1)}%</span>
                            </div>
                          </td>
                          <td className="py-2 px-3">
                            <div className="flex items-center space-x-2">
                              <Clock className="h-4 w-4 text-purple-400" />
                              <span>{trend.completion_rate.toFixed(1)}%</span>
                            </div>
                          </td>
                          <td className="py-2 px-3">
                            {scoreChange !== 0 && (
                              <Badge variant="secondary" className={scoreChange > 0 ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                                {scoreChange > 0 ? '+' : ''}{scoreChange.toFixed(1)}%
                              </Badge>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}