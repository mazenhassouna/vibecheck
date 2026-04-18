export default function ResultsPage({ result, onStartOver }) {
  const { score, label, breakdown, shared_interests, bonus_points } = result

  // Calculate circle progress
  const circumference = 2 * Math.PI * 45
  const strokeDashoffset = circumference - (score / 100) * circumference

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
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="45"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="10"
              fill="none"
            />
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

      {/* Shared interests with examples */}
      {shared_interests && shared_interests.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            🎯 What You Have in Common
          </h3>
          
          <div className="space-y-4">
            {shared_interests.map((interest, index) => (
              <div 
                key={index}
                className={`p-4 rounded-lg ${
                  interest.quality === 'Strong match'
                    ? 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30'
                    : interest.quality === 'Good match'
                    ? 'bg-gradient-to-r from-pink-500/15 to-purple-500/15 border border-pink-500/20'
                    : 'bg-white/5 border border-white/10'
                }`}
              >
                {/* Theme header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-semibold text-lg">
                    {interest.emoji} {interest.theme}
                  </span>
                  {interest.quality === 'Strong match' && (
                    <span className="text-xs bg-green-500/30 text-green-300 px-2 py-1 rounded-full">
                      ⭐ Strong
                    </span>
                  )}
                </div>
                
                {/* Examples */}
                {interest.examples && interest.examples.length > 0 && (
                  <div className="space-y-1 mb-3">
                    {interest.examples.map((example, i) => (
                      <p key={i} className="text-white/80 text-sm pl-2 border-l-2 border-white/20">
                        {example}
                      </p>
                    ))}
                  </div>
                )}
                
                {/* Ways to connect */}
                {interest.ways_to_connect && interest.ways_to_connect.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-white/50 mb-2">Ways to connect:</p>
                    <div className="flex flex-wrap gap-2">
                      {interest.ways_to_connect.map((idea, i) => (
                        <span 
                          key={i}
                          className="text-xs bg-white/10 text-white/70 px-3 py-1 rounded-full"
                        >
                          💡 {idea}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score breakdown */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          📊 Score Breakdown
        </h3>
        
        <p className="text-white/50 text-xs mb-4">
          Your score blends exact matches (40%) with shared interest themes (60%)
        </p>
        
        <div className="space-y-4">
          {Object.entries(breakdown).map(([category, data]) => (
            <div key={category}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-white/70 capitalize">{category}</span>
                <span className="text-white">
                  {data.score}% similarity
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
