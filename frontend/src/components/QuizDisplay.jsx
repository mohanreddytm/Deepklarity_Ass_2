export default function QuizDisplay({ quiz }) {
  if (!quiz) return null
  return (
    <div className="space-y-4">
      {quiz.title && <h2 className="text-2xl font-semibold">{quiz.title}</h2>}
      {quiz.summary && (
        <div>
          <h3 className="font-semibold mb-1">Summary</h3>
          <p className="text-gray-700">{quiz.summary}</p>
        </div>
      )}

      {Array.isArray(quiz.quiz) && quiz.quiz.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold">Questions</h3>
          {quiz.quiz.map((q, idx) => (
            <div key={idx} className="border rounded p-3">
              <div className="font-medium">Q{idx + 1}. {q.question}</div>
              {Array.isArray(q.options) && (
                <ul className="list-disc list-inside text-gray-800 mt-1">
                  {q.options.map((opt, i) => (
                    <li key={i}>{opt}</li>
                  ))}
                </ul>
              )}
              <div className="mt-2 text-green-700"><span className="font-semibold">Answer:</span> {q.answer}</div>
              {q.explanation && (
                <div className="text-gray-700"><span className="font-semibold">Explanation:</span> {q.explanation}</div>
              )}
              {q.difficulty && (
                <div className="text-sm text-gray-500 mt-1">Difficulty: {q.difficulty}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {Array.isArray(quiz.related_topics) && quiz.related_topics.length > 0 && (
        <div>
          <h3 className="font-semibold">Related Topics</h3>
          <div className="flex flex-wrap gap-2 mt-1">
            {quiz.related_topics.map((t, i) => (
              <span key={i} className="px-2 py-1 text-sm bg-gray-100 rounded border">{t}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

