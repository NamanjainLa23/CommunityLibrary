import { useEffect, useState } from 'react'

function App() {
  const [status, setStatus] = useState('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus('backend unreachable'))
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white rounded-xl shadow p-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800">📚 BookLender</h1>
        <p className="mt-2 text-gray-500">
          Backend status: <span className="font-mono">{status}</span>
        </p>
      </div>
    </div>
  )
}

export default App