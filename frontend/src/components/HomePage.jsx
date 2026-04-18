import { useState } from 'react'
import { createSession, getSessionStatus } from '../api'

export default function HomePage({ onCreateSession, onJoinSession }) {
  const [mode, setMode] = useState(null) // 'create' or 'join'
  const [joinCode, setJoinCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleCreateSession = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const session = await createSession()
      onCreateSession(session.session_code, 'a')
    } catch (err) {
      setError('Failed to create session. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinSession = async (e) => {
    e.preventDefault()
    
    if (!joinCode.trim()) {
      setError('Please enter a session code')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      // Verify session exists
      await getSessionStatus(joinCode.toUpperCase())
      onJoinSession(joinCode.toUpperCase())
    } catch (err) {
      setError('Session not found. Check the code and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Main options */}
      {!mode && (
        <div className="card p-8">
          <h2 className="text-2xl font-semibold text-white text-center mb-6">
            How would you like to start?
          </h2>
          
          <div className="grid gap-4">
            <button
              onClick={() => setMode('create')}
              className="card p-6 text-left hover:bg-white/20 transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center">
                  <span className="text-2xl">🎉</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white group-hover:text-pink-300">
                    Start a New Session
                  </h3>
                  <p className="text-white/60 text-sm">
                    Create a session and share the code with your friend
                  </p>
                </div>
              </div>
            </button>
            
            <button
              onClick={() => setMode('join')}
              className="card p-6 text-left hover:bg-white/20 transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-500 to-orange-500 flex items-center justify-center">
                  <span className="text-2xl">🔗</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white group-hover:text-purple-300">
                    Join a Session
                  </h3>
                  <p className="text-white/60 text-sm">
                    Enter a code shared by your friend
                  </p>
                </div>
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Create session */}
      {mode === 'create' && (
        <div className="card p-8">
          <button 
            onClick={() => setMode(null)}
            className="text-white/60 hover:text-white mb-4 flex items-center gap-2"
          >
            ← Back
          </button>
          
          <h2 className="text-2xl font-semibold text-white text-center mb-4">
            Start a New Session
          </h2>
          
          <p className="text-white/70 text-center mb-6">
            Click below to create a session. You'll get a code to share with your friend.
          </p>
          
          <button
            onClick={handleCreateSession}
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? 'Creating...' : 'Create Session'}
          </button>
          
          {error && (
            <p className="text-red-400 text-center mt-4">{error}</p>
          )}
        </div>
      )}

      {/* Join session */}
      {mode === 'join' && (
        <div className="card p-8">
          <button 
            onClick={() => setMode(null)}
            className="text-white/60 hover:text-white mb-4 flex items-center gap-2"
          >
            ← Back
          </button>
          
          <h2 className="text-2xl font-semibold text-white text-center mb-4">
            Join a Session
          </h2>
          
          <p className="text-white/70 text-center mb-6">
            Enter the 6-character code your friend shared with you.
          </p>
          
          <form onSubmit={handleJoinSession} className="space-y-4">
            <input
              type="text"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              placeholder="Enter code (e.g., ABC123)"
              maxLength={6}
              className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white text-center text-2xl tracking-widest placeholder:text-white/30 focus:outline-none focus:border-pink-500"
            />
            
            <button
              type="submit"
              disabled={loading || joinCode.length !== 6}
              className="btn-primary w-full"
            >
              {loading ? 'Joining...' : 'Join Session'}
            </button>
          </form>
          
          {error && (
            <p className="text-red-400 text-center mt-4">{error}</p>
          )}
        </div>
      )}

      {/* How it works */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">How it works</h3>
        
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-pink-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-pink-400 font-semibold">1</span>
            </div>
            <div>
              <p className="text-white">Download your Instagram data</p>
              <p className="text-white/50 text-sm">Settings → Your Activity → Download Your Information → JSON format</p>
            </div>
          </div>
          
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-purple-400 font-semibold">2</span>
            </div>
            <div>
              <p className="text-white">Upload your data ZIP file</p>
              <p className="text-white/50 text-sm">We only analyze likes, saved posts, and who you follow</p>
            </div>
          </div>
          
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-orange-500/20 flex items-center justify-center flex-shrink-0">
              <span className="text-orange-400 font-semibold">3</span>
            </div>
            <div>
              <p className="text-white">Discover your shared interests!</p>
              <p className="text-white/50 text-sm">Get a relationship summary and ways to connect</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
