import { useEffect, useState } from 'react'
import { api } from '../services/api'
import QuizDisplay from './QuizDisplay'

export default function HistoryTab() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/history')
        setItems(res)
      } catch (err) {
        setError(err?.message || 'Failed to fetch history')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const openDetails = async (id) => {
    setSelected({ loading: true })
    try {
      const quiz = await api.get(`/quiz/${id}`)
      setSelected({ quiz })
    } catch (err) {
      setSelected({ error: err?.message || 'Failed to load quiz' })
    }
  }

  return (
    <div>
      {loading && <div className="text-gray-600">Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="min-w-full border">
            <thead className="bg-gray-100">
              <tr>
                <th className="text-left p-2 border">ID</th>
                <th className="text-left p-2 border">Title</th>
                <th className="text-left p-2 border">URL</th>
                <th className="text-left p-2 border">Date</th>
                <th className="text-left p-2 border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(row => (
                <tr key={row.id} className="border-t">
                  <td className="p-2 border">{row.id}</td>
                  <td className="p-2 border">{row.title}</td>
                  <td className="p-2 border text-blue-700 underline"><a href={row.url} target="_blank" rel="noreferrer">Link</a></td>
                  <td className="p-2 border">{new Date(row.created_at).toLocaleString()}</td>
                  <td className="p-2 border">
                    <button onClick={() => openDetails(row.id)} className="px-3 py-1 rounded border bg-white hover:bg-gray-50">Details</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white rounded border max-w-3xl w-full max-h-[80vh] overflow-auto p-4 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Quiz Details</h3>
              <button onClick={() => setSelected(null)} className="px-3 py-1 rounded bg-gray-100 border">Close</button>
            </div>

            {selected.loading && <div>Loading...</div>}
            {selected.error && <div className="text-red-600">{selected.error}</div>}
            {selected.quiz && <QuizDisplay quiz={selected.quiz} />}
          </div>
        </div>
      )}
    </div>
  )
}

