import { useState } from 'react'
import { api } from '../services/api'
import QuizDisplay from './QuizDisplay'

export default function GenerateQuizTab() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setQuiz(null)
    try {
      const res = await api.post('/generate_quiz', { url })
      setQuiz(res)
    } catch (err) {
      setError(err?.message || 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste Wikipedia URL"
          className="flex-1 border rounded px-3 py-2"
          required
        />
        <button type="submit" disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60">
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </form>

      {error && <div className="text-red-600">{error}</div>}
      {loading && <div className="text-gray-600">Processing the article, please wait...</div>}
      {!loading && quiz && <QuizDisplay quiz={quiz} />}
    </div>
  )
}

