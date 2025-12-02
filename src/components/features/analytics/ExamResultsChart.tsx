"use client"

import { BarChart3 } from 'lucide-react'

interface ScoreDistribution {
  score_range: string
  count: number
  percentage: number
}

interface ExamResultsChartProps {
  data: ScoreDistribution[]
}

export function ExamResultsChart({ data }: ExamResultsChartProps) {
  const maxCount = Math.max(...data.map(d => d.count))

  const getBarColor = (range: string) => {
    const score = parseInt(range.split('-')[0])
    if (score >= 90) return 'bg-green-500'
    if (score >= 80) return 'bg-blue-500'
    if (score >= 70) return 'bg-yellow-500'
    if (score >= 60) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getBarColorLight = (range: string) => {
    const score = parseInt(range.split('-')[0])
    if (score >= 90) return 'bg-green-100'
    if (score >= 80) return 'bg-blue-100'
    if (score >= 70) return 'bg-yellow-100'
    if (score >= 60) return 'bg-orange-100'
    return 'bg-red-100'
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <BarChart3 className="h-8 w-8 mx-auto mb-2" />
          <p>No score data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Chart */}
      <div className="space-y-2">
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-4">
            {/* Score Range Label */}
            <div className="w-16 text-sm font-medium text-gray-700">
              {item.score_range}%
            </div>

            {/* Bar */}
            <div className="flex-1 relative">
              <div className={`h-8 rounded-lg ${getBarColorLight(item.score_range)} relative overflow-hidden`}>
                <div 
                  className={`h-full rounded-lg ${getBarColor(item.score_range)} transition-all duration-500 ease-out`}
                  style={{ width: `${(item.count / maxCount) * 100}%` }}
                />
                
                {/* Count and Percentage Labels */}
                <div className="absolute inset-0 flex items-center justify-between px-3">
                  <span className="text-sm font-medium text-gray-900">
                    {item.count} students
                  </span>
                  <span className="text-sm font-medium text-gray-700">
                    {item.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="border-t border-gray-200 pt-4">
        <div className="grid grid-cols-5 gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span className="text-gray-600">90-100%</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-gray-600">80-89%</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
            <span className="text-gray-600">70-79%</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-orange-500 rounded"></div>
            <span className="text-gray-600">60-69%</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span className="text-gray-600">Below 60%</span>
          </div>
        </div>
      </div>
    </div>
  )
}