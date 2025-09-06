'use client'

import { useQuery } from '@tanstack/react-query'
import { Activity, TrendingUp, AlertTriangle, Coins } from 'lucide-react'

// API client
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchHealthStatus() {
  const response = await fetch(`${API_URL}/healthz`)
  if (!response.ok) {
    throw new Error('Failed to fetch health status')
  }
  return response.json()
}

async function fetchTopNarratives() {
  const response = await fetch(`${API_URL}/narratives/top?window=1h&limit=10`)
  if (!response.ok) {
    throw new Error('Failed to fetch narratives')
  }
  return response.json()
}

export default function Dashboard() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealthStatus,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const { data: narratives, isLoading: narrativesLoading } = useQuery({
    queryKey: ['narratives', 'top'],
    queryFn: fetchTopNarratives,
    refetchInterval: 60000, // Refetch every minute
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 Solana Narrative Scanner
          </h1>
          <p className="text-gray-600">
            Track emerging narratives and discover meme coin opportunities in real-time
          </p>
        </div>

        {/* System Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatusCard
            title="System Health"
            value={health?.status || 'checking...'}
            icon={<Activity className="h-6 w-6" />}
            status={health?.status === 'healthy' ? 'good' : 'warning'}
            loading={healthLoading}
          />
          <StatusCard
            title="Active Narratives"
            value={narratives?.total_count || 0}
            icon={<TrendingUp className="h-6 w-6" />}
            status="good"
            loading={narrativesLoading}
          />
          <StatusCard
            title="Alerts Today"
            value="0"
            icon={<AlertTriangle className="h-6 w-6" />}
            status="good"
            loading={false}
          />
          <StatusCard
            title="Tokens Launched"
            value="0"
            icon={<Coins className="h-6 w-6" />}
            status="good"
            loading={false}
          />
        </div>

        {/* Top Narratives */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            🔥 Top Narratives (1 hour)
          </h2>
          {narrativesLoading ? (
            <div className="text-gray-500">Loading narratives...</div>
          ) : narratives?.narratives?.length > 0 ? (
            <div className="space-y-4">
              {narratives.narratives.map((narrative: any, index: number) => (
                <NarrativeCard key={narrative.id} narrative={narrative} rank={index + 1} />
              ))}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-8">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No narratives detected yet. The system is scanning for emerging trends...</p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ActionCard
            title="Coin Studio"
            description="Generate coin ideas from trending narratives"
            buttonText="Open Studio"
            onClick={() => console.log('Open Coin Studio')}
          />
          <ActionCard
            title="Alert Settings"
            description="Configure narrative spike alerts"
            buttonText="Set Alerts"
            onClick={() => console.log('Set Alerts')}
          />
          <ActionCard
            title="Launched Tokens"
            description="Monitor deployed tokens performance"
            buttonText="View Tokens"
            onClick={() => console.log('View Tokens')}
          />
        </div>
      </div>
    </div>
  )
}

interface StatusCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  status: 'good' | 'warning' | 'error'
  loading: boolean
}

function StatusCard({ title, value, icon, status, loading }: StatusCardProps) {
  const statusColors = {
    good: 'text-green-600 bg-green-50',
    warning: 'text-yellow-600 bg-yellow-50',
    error: 'text-red-600 bg-red-50'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`${statusColors[status]} p-2 rounded-lg`}>
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">
            {loading ? '...' : value}
          </p>
        </div>
      </div>
    </div>
  )
}

interface NarrativeCardProps {
  narrative: any
  rank: number
}

function NarrativeCard({ narrative, rank }: NarrativeCardProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm font-medium">
            #{rank}
          </span>
          <h3 className="font-semibold text-gray-900">{narrative.label}</h3>
        </div>
        <div className="flex space-x-2">
          <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
            VS: {narrative.scores?.VS?.toFixed(2) || 'N/A'}
          </span>
          {narrative.scores?.LRS && (
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
              LRS: {narrative.scores.LRS.toFixed(2)}
            </span>
          )}
        </div>
      </div>
      <div className="mt-2 flex space-x-4 text-sm text-gray-600">
        <span>📈 {narrative.stats?.mentions || 0} mentions</span>
        <span>📊 {((narrative.stats?.growth_rate || 0) * 100).toFixed(1)}% growth</span>
        <span>💭 {((narrative.stats?.sentiment || 0) * 100).toFixed(0)}% sentiment</span>
      </div>
    </div>
  )
}

interface ActionCardProps {
  title: string
  description: string
  buttonText: string
  onClick: () => void
}

function ActionCard({ title, description, buttonText, onClick }: ActionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <button
        onClick={onClick}
        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors"
      >
        {buttonText}
      </button>
    </div>
  )
}