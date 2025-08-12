import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, Play, Clock, CheckCircle, XCircle, Download, Video, Share2 } from 'lucide-react'

interface Generation {
  id: string
  topic: string
  niche: string
  status: string
  created_at: string
  completed_at?: string
  failed_at?: string
  error?: string
  script?: string
  description?: string
  aspect_ratios?: string[]
  social_platforms?: string[]
  video_files?: {
    '16:9'?: string
    '9:16'?: string
    '1:1'?: string
  }
  social_uploads?: {
    youtube?: { status: string; url?: string; message?: string }
    tiktok?: { status: string; url?: string; message?: string }
    facebook?: { status: string; url?: string; message?: string }
    instagram?: { status: string; url?: string; message?: string }
  }
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const niches = [
  'Business Failures & Scandals',
  'True Crime',
  'Historical Events',
  'Science & Technology',
  'Nature & Wildlife',
  'Sports & Athletes',
  'Art & Culture',
  'Mystery & Unexplained',
  'Health & Medicine',
  'Space & Astronomy',
  'Ancient Civilizations',
  'War & Military History',
  'Economics & Finance',
  'Psychology & Human Behavior',
  'Environmental Issues',
  'Innovation & Inventions',
  'Music & Entertainment',
  'Food & Culinary History',
  'Transportation & Travel',
  'Architecture & Engineering',
  'Politics & Government',
  'Social Movements',
  'Disasters & Catastrophes',
  'Conspiracy Theories',
  'Biographies & Life Stories',
  'Religion & Spirituality',
  'Education & Learning',
  'Fashion & Lifestyle',
  'Gaming & Digital Culture',
  'Artificial Intelligence & Future Tech'
]

const aspectRatios = [
  { value: '16:9', label: 'Landscape (16:9) - YouTube, Facebook' },
  { value: '9:16', label: 'Portrait (9:16) - TikTok, Instagram Stories' },
  { value: '1:1', label: 'Square (1:1) - Instagram Posts' }
]

const socialPlatforms = [
  { value: 'youtube', label: 'YouTube' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'instagram', label: 'Instagram' }
]

function App() {
  const [topic, setTopic] = useState('')
  const [selectedNiche, setSelectedNiche] = useState('')
  const [selectedAspectRatios, setSelectedAspectRatios] = useState<string[]>(['16:9'])
  const [selectedSocialPlatforms, setSelectedSocialPlatforms] = useState<string[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [generations, setGenerations] = useState<Generation[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    fetchGenerations()
    const interval = setInterval(fetchGenerations, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchGenerations = async () => {
    try {
      const response = await fetch(`${API_URL}/api/generations`)
      const data = await response.json()
      setGenerations(data.generations || [])
    } catch (err) {
      console.error('Failed to fetch generations:', err)
    }
  }

  const handleGenerate = async () => {
    if (!topic.trim() || !selectedNiche) {
      setError('Please enter a topic and select a niche')
      return
    }

    if (selectedAspectRatios.length === 0) {
      setError('Please select at least one aspect ratio')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const response = await fetch(`${API_URL}/api/generate-video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          niche: selectedNiche,
          aspect_ratios: selectedAspectRatios,
          social_platforms: selectedSocialPlatforms,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to start video generation')
      }

      setTopic('')
      setSelectedNiche('')
      setSelectedAspectRatios(['16:9'])
      setSelectedSocialPlatforms([])
      fetchGenerations()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start video generation')
    } finally {
      setIsGenerating(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'generating':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      generating: 'default',
      completed: 'default',
      failed: 'destructive'
    } as const

    return (
      <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
        {status}
      </Badge>
    )
  }

  const handleAspectRatioChange = (ratio: string, checked: boolean) => {
    if (checked) {
      setSelectedAspectRatios([...selectedAspectRatios, ratio])
    } else {
      setSelectedAspectRatios(selectedAspectRatios.filter(r => r !== ratio))
    }
  }

  const handleSocialPlatformChange = (platform: string, checked: boolean) => {
    if (checked) {
      setSelectedSocialPlatforms([...selectedSocialPlatforms, platform])
    } else {
      setSelectedSocialPlatforms(selectedSocialPlatforms.filter(p => p !== platform))
    }
  }

  const getVideoDownloadButtons = (generation: Generation) => {
    if (!generation.video_files) return null

    return (
      <div className="flex flex-wrap gap-2 mt-2">
        {Object.entries(generation.video_files).map(([format, filePath]) => {
          if (!filePath) return null
          
          const formatLabel = format === '16:9' ? 'Landscape' : 
                             format === '9:16' ? 'Portrait' : 'Square'
          
          return (
            <Button
              key={format}
              variant="outline"
              size="sm"
              onClick={() => {
                const downloadUrl = `${API_URL}/api/download-video/${generation.id}/${format.replace(':', 'x')}`
                window.open(downloadUrl, '_blank')
              }}
              className="flex items-center gap-1"
            >
              <Video className="h-3 w-3" />
              {formatLabel} ({format})
            </Button>
          )
        })}
      </div>
    )
  }

  const getSocialUploadStatus = (generation: Generation) => {
    if (!generation.social_uploads) return null

    return (
      <div className="mt-2">
        <p className="text-xs font-medium text-gray-600 mb-1">Social Media Status:</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(generation.social_uploads).map(([platform, result]) => (
            <div key={platform} className="flex items-center gap-1">
              <Badge 
                variant={result.status === 'success' ? 'default' : 
                        result.status === 'pending' ? 'secondary' : 'destructive'}
                className="text-xs"
              >
                {platform}: {result.status}
              </Badge>
              {result.url && (
                <a 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:text-blue-700"
                >
                  <Share2 className="h-3 w-3" />
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">DocuGen AI</h1>
          <p className="text-lg text-gray-600">AI-powered documentary video generation platform</p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-5 w-5" />
              Generate Documentary
            </CardTitle>
            <CardDescription>
              Enter a topic and select a niche to generate an AI-powered documentary video
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
                Topic
              </label>
              <Input
                id="topic"
                placeholder="e.g., The Rise and Fall of Theranos"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={isGenerating}
              />
            </div>

            <div>
              <label htmlFor="niche" className="block text-sm font-medium text-gray-700 mb-1">
                Niche
              </label>
              <Select value={selectedNiche} onValueChange={setSelectedNiche} disabled={isGenerating}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a niche" />
                </SelectTrigger>
                <SelectContent>
                  {niches.map((niche) => (
                    <SelectItem key={niche} value={niche}>
                      {niche}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Formats
              </label>
              <div className="space-y-2">
                {aspectRatios.map((ratio) => (
                  <div key={ratio.value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`ratio-${ratio.value}`}
                      checked={selectedAspectRatios.includes(ratio.value)}
                      onChange={(e) => handleAspectRatioChange(ratio.value, e.target.checked)}
                      disabled={isGenerating}
                      className="rounded border-gray-300"
                    />
                    <label htmlFor={`ratio-${ratio.value}`} className="text-sm text-gray-700">
                      {ratio.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Auto-Post to Social Media (Optional)
              </label>
              <div className="space-y-2">
                {socialPlatforms.map((platform) => (
                  <div key={platform.value} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`platform-${platform.value}`}
                      checked={selectedSocialPlatforms.includes(platform.value)}
                      onChange={(e) => handleSocialPlatformChange(platform.value, e.target.checked)}
                      disabled={isGenerating}
                      className="rounded border-gray-300"
                    />
                    <label htmlFor={`platform-${platform.value}`} className="text-sm text-gray-700">
                      {platform.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
                {error}
              </div>
            )}

            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !topic.trim() || !selectedNiche || selectedAspectRatios.length === 0}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Documentary...
                </>
              ) : (
                'Generate Documentary'
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Generations</CardTitle>
            <CardDescription>
              Your documentary generation history
            </CardDescription>
          </CardHeader>
          <CardContent>
            {generations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No generations yet. Create your first documentary above!
              </div>
            ) : (
              <div className="space-y-4">
                {generations.map((generation) => (
                  <div
                    key={generation.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getStatusIcon(generation.status)}
                          <h3 className="font-semibold text-gray-900">{generation.topic}</h3>
                          {getStatusBadge(generation.status)}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Niche: {generation.niche}</p>
                        <p className="text-xs text-gray-500">
                          Created: {new Date(generation.created_at).toLocaleString()}
                        </p>
                        {generation.completed_at && (
                          <p className="text-xs text-gray-500">
                            Completed: {new Date(generation.completed_at).toLocaleString()}
                          </p>
                        )}
                        {generation.error && (
                          <p className="text-xs text-red-600 mt-1">
                            Error: {generation.error}
                          </p>
                        )}
                        {generation.description && (
                          <p className="text-sm text-gray-700 mt-2 italic">
                            "{generation.description}"
                          </p>
                        )}
                        {generation.status === 'completed' && getVideoDownloadButtons(generation)}
                        {generation.status === 'completed' && getSocialUploadStatus(generation)}
                      </div>
                      {generation.status === 'completed' && (
                        <div className="ml-4 space-y-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const downloadUrl = `${API_URL}/api/download/${generation.id}`
                              window.open(downloadUrl, '_blank')
                            }}
                            className="flex items-center gap-2"
                          >
                            <Download className="h-4 w-4" />
                            Download Audio
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
