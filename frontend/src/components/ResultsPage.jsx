export default function ResultsPage({ result, onStartOver }) {
  const { score, label, breakdown, shared_interests, bonus_points } = result

  // Calculate circle progress
  const circumference = 2 * Math.PI * 45 // radius = 45
  const strokeDashoffset = circumference - (score / 100) * circumference

  // Get score color
  const getScoreColor = () => {
    if (score >= 85) return 'text-green-400'
    if (score >= 70) return 'text-emerald-400'
    if (score >= 50) return 'text-yellow-400'
    if (score >= 30) return 'text-orange-400'
    return 'text-red-400'
  }

  const getStrokeColor = () => {
    if (score >= 85) return '#4ade80'
    if (score >= 70) return '#34d399'
    if (score >= 50) return '#facc15'
    if (score >= 30) return '#fb923c'
    return '#f87171'
  }

  return (
    <div className="space-y-6">
      {/* Score display */}
      <div className="card p-8 text-center">
        <div className="relative w-40 h-40 mx-auto mb-6">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="45"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="10"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="80"
              cy="80"
              r="45"
              stroke={getStrokeColor()}
              strokeWidth="10"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className="score-circle"
            />
          </svg>
          {/* Score text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold ${getScoreColor()}`}>
              {score}%
            </span>
          </div>
        </div>
        
        <div className="text-4xl mb-2">{label?.emoji}</div>
        <h2 className="text-2xl font-semibold text-white mb-2">
          {label?.text}
        </h2>
        
        {bonus_points > 0 && (
          <div className="mt-4 inline-block bg-yellow-500/20 text-yellow-300 px-4 py-2 rounded-full text-sm">
            ⭐ +{bonus_points} bonus points for special matches!
          </div>
        )}
      </div>

      {/* Shared interests */}
      {shared_interests && shared_interests.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            🎯 What You Have in Common
          </h3>
          
          <div className="space-y-3">
            {shared_interests.slice(0, 5).map((interest, index) => (
              <div 
                key={index}
                className={`flex items-center justify-between p-4 rounded-lg ${
                  interest.quality === 'Strong match'
                    ? 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30'
                    : interest.quality === 'Good match'
                    ? 'bg-gradient-to-r from-pink-500/15 to-purple-500/15 border border-pink-500/20'
                    : 'bg-white/5 border border-white/10'
                }`}
              >
                <span className="text-white font-medium">{interest.description}</span>
                {interest.quality === 'Strong match' && (
                  <span className="text-xs bg-green-500/30 text-green-300 px-2 py-1 rounded-full">⭐ Strong</span>
                )}
              </div>
            ))}
          </div>
          
          {shared_interests.length > 15 && (
            <p className="text-white/50 text-sm mt-4 text-center">
              + {shared_interests.length - 15} more shared interests
            </p>
          )}
        </div>
      )}

      {/* Score breakdown */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          📊 Score Breakdown
        </h3>
        
        <div className="space-y-4">
          {Object.entries(breakdown).map(([category, data]) => (
            <div key={category}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-white/70 capitalize">{category}</span>
                <span className="text-white">
                  {data.score}% × {(data.weight * 100).toFixed(0)}% = {data.weighted_contribution}
                </span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full transition-all duration-1000"
                  style={{ width: `${data.score}%` }}
                />
              </div>
            </div>
          ))}
          
          {bonus_points > 0 && (
            <div className="pt-4 border-t border-white/10">
              <div className="flex justify-between text-sm">
                <span className="text-yellow-300">Bonus Points</span>
                <span className="text-yellow-300">+{bonus_points}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Category explanation */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          📖 What the categories mean
        </h3>
        
        <div className="space-y-3 text-sm text-white/60">
          <p><strong className="text-white">Likes (30%):</strong> Accounts whose content you both like</p>
          <p><strong className="text-white">Saved (30%):</strong> Posts you've both saved for later</p>
          <p><strong className="text-white">Following (30%):</strong> Accounts you both follow</p>
          <p><strong className="text-white">Comments (10%):</strong> How similarly you engage (length, emoji use, etc.)</p>
        </div>
        
        <p className="text-xs text-white/40 mt-4">
          Interests are derived from the accounts you both engage with.
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex gap-4">
        <button
          onClick={onStartOver}
          className="btn-primary flex-1"
        >
          Start New Session
        </button>
      </div>

      {/* Privacy reminder */}
      <div className="text-center text-white/40 text-sm">
        <p>🔒 Your data has been deleted from our servers.</p>
        <p>Only the results above were generated.</p>
      </div>
    </div>
  )
}
