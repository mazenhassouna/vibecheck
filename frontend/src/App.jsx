import { useState, useEffect } from 'react'
import UploadPage from './components/UploadPage'
import WaitingRoom from './components/WaitingRoom'
import ResultsPage from './components/ResultsPage'
import HomePage from './components/HomePage'
import { getSessionStatus, getResult } from './api'

function App() {
  const [page, setPage] = useState('home') // home, upload, waiting, results
  const [sessionCode, setSessionCode] = useState(null)
  const [person, setPerson] = useState(null) // 'a' or 'b'
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Poll for session status when waiting
  useEffect(() => {
    if (page !== 'waiting' || !sessionCode) return

    const pollInterval = setInterval(async () => {
      try {
        const status = await getSessionStatus(sessionCode)
        
        if (status.result_ready) {
          const resultData = await getResult(sessionCode)
          setResult(resultData)
          setPage('results')
        }
      } catch (err) {
        console.error('Polling error:', err)
        if (err.message.includes('not found') || err.message.includes('expired')) {
          setError('Session expired. Please start over.')
          setPage('home')
        }
      }
    }, 2000) // Poll every 2 seconds

    return () => clearInterval(pollInterval)
  }, [page, sessionCode])

  const handleSessionCreated = (code, personType) => {
    setSessionCode(code)
    setPerson(personType)
    setPage('upload')
  }

  const handleJoinSession = (code) => {
    setSessionCode(code)
    setPerson('b')
    setPage('upload')
  }

  const handleUploadComplete = (resultData) => {
    if (resultData) {
      setResult(resultData)
      setPage('results')
    } else {
      setPage('waiting')
    }
  }

  const handleStartOver = () => {
    setSessionCode(null)
    setPerson(null)
    setResult(null)
    setError(null)
    setPage('home')
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Vibe Check
          </h1>
          <p className="text-white/70">
            Discover what you have in common
          </p>
        </header>

        {/* Error message */}
        {error && (
          <div className="card p-4 mb-6 bg-red-500/20 border-red-500/50 text-center">
            <p className="text-red-200">{error}</p>
            <button 
              onClick={handleStartOver}
              className="mt-2 text-white underline"
            >
              Start Over
            </button>
          </div>
        )}

        {/* Page content */}
        {page === 'home' && (
          <HomePage 
            onCreateSession={handleSessionCreated}
            onJoinSession={handleJoinSession}
          />
        )}

        {page === 'upload' && (
          <UploadPage 
            sessionCode={sessionCode}
            person={person}
            onComplete={handleUploadComplete}
            onBack={handleStartOver}
          />
        )}

        {page === 'waiting' && (
          <WaitingRoom 
            sessionCode={sessionCode}
            person={person}
          />
        )}

        {page === 'results' && result && (
          <ResultsPage 
            result={result}
            onStartOver={handleStartOver}
          />
        )}

        {/* Footer */}
        <footer className="text-center mt-12 text-white/50 text-sm">
          <p>Your privacy matters. We only analyze what you choose to share.</p>
        </footer>
      </div>
    </div>
  )
}

export default App
