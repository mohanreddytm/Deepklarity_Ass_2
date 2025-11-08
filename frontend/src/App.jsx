import { useState } from 'react'
import GenerateQuizTab from './components/GenerateQuizTab.jsx'
import HistoryTab from './components/HistoryTab.jsx'

export default function App() {
  const [active, setActive] = useState('generate')

  return (
    <div className="max-w-5xl mx-auto p-4">
      <header className="my-6">
        <h1 className="text-3xl font-bold">AI Wiki Quiz Generator</h1>
        <p className="text-gray-600">Generate quizzes from Wikipedia using AI</p>
      </header>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActive('generate')}
          className={`px-4 py-2 rounded border ${active==='generate' ? 'bg-blue-600 text-white' : 'bg-white hover:bg-gray-50'}`}
        >
          Generate Quiz
        </button>
        <button
          onClick={() => setActive('history')}
          className={`px-4 py-2 rounded border ${active==='history' ? 'bg-blue-600 text-white' : 'bg-white hover:bg-gray-50'}`}
        >
          Past Quizzes
        </button>
      </div>

      <main className="bg-white border rounded p-4">
        {active === 'generate' ? <GenerateQuizTab /> : <HistoryTab />}
      </main>
    </div>
  )
}

