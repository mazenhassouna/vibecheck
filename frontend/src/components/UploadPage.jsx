import { useState, useRef } from 'react'
import { uploadData, getResult } from '../api'

export default function UploadPage({ sessionCode, person, onComplete, onBack }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [showPrivacy, setShowPrivacy] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return
    
    if (!selectedFile.name.toLowerCase().endsWith('.zip')) {
      setError('Please select a ZIP file')
      return
    }
    
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('File is too large (max 50MB)')
      return
    }
    
    setFile(selectedFile)
    setError(null)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    
    const droppedFile = e.dataTransfer.files[0]
    handleFileSelect(droppedFile)
  }

  const handleUpload = async () => {
    if (!file) return
    
    setUploading(true)
    setError(null)
    
    try {
      const result = await uploadData(sessionCode, file, person)
      
      if (result.result_ready) {
        // Both people uploaded, get result
        const fullResult = await getResult(sessionCode)
        onComplete(fullResult)
      } else {
        // Waiting for partner
        onComplete(null)
      }
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Session code display */}
      <div className="card p-6 text-center">
        <p className="text-white/60 text-sm mb-2">Session Code</p>
        <p className="text-3xl font-bold text-white tracking-widest">{sessionCode}</p>
        {person === 'a' && (
          <p className="text-white/60 text-sm mt-2">
            Share this code with your friend!
          </p>
        )}
      </div>

      {/* Privacy disclosure */}
      <div className="card p-6">
        <button 
          onClick={() => setShowPrivacy(!showPrivacy)}
          className="w-full flex items-center justify-between text-left"
        >
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            🔒 What we analyze (5 things only)
          </h3>
          <span className="text-white/60">{showPrivacy ? '▲' : '▼'}</span>
        </button>
        
        {showPrivacy && (
          <div className="mt-4 space-y-4">
            <div className="grid gap-3">
              <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg">
                <span className="text-green-400">✓</span>
                <div>
                  <p className="text-white font-medium">Likes</p>
                  <p className="text-white/50 text-sm">What content you enjoy</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg">
                <span className="text-green-400">✓</span>
                <div>
                  <p className="text-white font-medium">Saved Posts</p>
                  <p className="text-white/50 text-sm">Your saved interests</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg">
                <span className="text-green-400">✓</span>
                <div>
                  <p className="text-white font-medium">Comments</p>
                  <p className="text-white/50 text-sm">Your engagement style (not the actual text)</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg">
                <span className="text-green-400">✓</span>
                <div>
                  <p className="text-white font-medium">Following</p>
                  <p className="text-white/50 text-sm">Types of accounts you follow</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg">
                <span className="text-green-400">✓</span>
                <div>
                  <p className="text-white font-medium">Topics</p>
                  <p className="text-white/50 text-sm">Instagram's interest categories</p>
                </div>
              </div>
            </div>
            
            <div className="border-t border-white/10 pt-4">
              <p className="text-red-400 font-medium mb-2">🚫 We NEVER access:</p>
              <ul className="text-white/50 text-sm space-y-1">
                <li>• Messages or DMs</li>
                <li>• Search history</li>
                <li>• Personal information</li>
                <li>• Login/security data</li>
                <li>• Any other private files</li>
              </ul>
            </div>
            
            <p className="text-white/40 text-xs">
              Your data is processed in memory and deleted immediately after analysis.
            </p>
          </div>
        )}
      </div>

      {/* Upload zone */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Upload Your Instagram Data
        </h3>
        
        <div
          className={`upload-zone ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            onChange={(e) => handleFileSelect(e.target.files[0])}
            className="hidden"
          />
          
          {file ? (
            <div>
              <span className="text-4xl mb-2 block">📁</span>
              <p className="text-white font-medium">{file.name}</p>
              <p className="text-white/50 text-sm">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <button
                onClick={(e) => { e.stopPropagation(); setFile(null) }}
                className="mt-2 text-red-400 text-sm hover:text-red-300"
              >
                Remove
              </button>
            </div>
          ) : (
            <div>
              <span className="text-4xl mb-2 block">📤</span>
              <p className="text-white">Drop your ZIP file here</p>
              <p className="text-white/50 text-sm">or click to browse</p>
            </div>
          )}
        </div>

        {error && (
          <p className="text-red-400 text-center mt-4">{error}</p>
        )}

        <div className="flex gap-4 mt-6">
          <button
            onClick={onBack}
            className="btn-secondary flex-1"
          >
            Back
          </button>
          
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="btn-primary flex-1"
          >
            {uploading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </div>
      </div>

      {/* Instructions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          How to download your Instagram data
        </h3>
        
        <ol className="space-y-3 text-white/70">
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">1.</span>
            <span>Open Instagram and go to Settings</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">2.</span>
            <span>Tap "Accounts Center" → "Your information and permissions"</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">3.</span>
            <span>Tap "Download your information"</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">4.</span>
            <span>Select your Instagram account</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">5.</span>
            <span>Choose "Download or transfer information" → "Some of your information"</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">6.</span>
            <span>Select: Followers, Following, Likes, Saved, Comments, Topics</span>
          </li>
          <li className="flex gap-3">
            <span className="text-pink-400 font-semibold">7.</span>
            <span>Choose JSON format and download the ZIP</span>
          </li>
        </ol>
      </div>
    </div>
  )
}
