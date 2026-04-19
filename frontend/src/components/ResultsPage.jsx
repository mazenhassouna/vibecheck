export default function ResultsPage({ result, onStartOver }) {
  const { 
    score, 
    label, 
    breakdown, 
    shared_interests, 
    bonus_points, 
    relationship_summary,
    content_comparison,
    content_boost 
  } = result

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
        
        <h2 className="text-2xl font-semibold text-white mb-2">
          {label?.text}
        </h2>
      </div>

      {/* Relationship Summary */}
      {relationship_summary && (
        <div className="card p-6 bg-gradient-to-br from-pink-500/10 to-purple-500/10 border border-white/10">
          <h3 className="text-xl font-bold text-white mb-3">
            {relationship_summary.headline}
          </h3>
          <p className="text-white/80 leading-relaxed mb-4">
            {relationship_summary.description}
          </p>
          <p className="text-white/60 text-sm italic">
            {relationship_summary.dynamic}
          </p>
        </div>
      )}

      {/* AI Content Analysis Badge */}
      {content_comparison && content_comparison.shared_themes?.length > 0 && (
        <div className="card p-4 bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🤖</span>
            <h3 className="text-sm font-semibold text-blue-300">
              AI Content Analysis
            </h3>
            {content_boost > 0 && (
              <span className="text-xs bg-blue-500/30 text-blue-200 px-2 py-0.5 rounded-full ml-auto">
                +{content_boost}% boost
              </span>
            )}
          </div>
          <p className="text-white/70 text-sm mb-3">
            Based on analyzing the actual content of reels you both engage with:
          </p>
          <div className="flex flex-wrap gap-2">
            {content_comparison.shared_themes.map((theme, i) => (
              <span 
                key={i}
                className="text-sm bg-blue-500/20 text-blue-200 px-3 py-1 rounded-full border border-blue-500/30"
              >
                {theme}
              </span>
            ))}
          </div>
          {content_comparison.shared_interests?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-xs text-white/50 mb-2">Specific shared interests detected:</p>
              <div className="flex flex-wrap gap-2">
                {content_comparison.shared_interests.map((interest, i) => (
                  <span 
                    key={i}
                    className="text-xs bg-white/10 text-white/70 px-2 py-1 rounded"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Shared interests with examples */}
      {shared_interests && shared_interests.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            🎯 Shared Interests
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
                  <div className="flex gap-2">
                    {interest.type === 'ai_identified' && (
                      <span className="text-xs bg-blue-500/30 text-blue-300 px-2 py-1 rounded-full">
                        🤖 AI
                      </span>
                    )}
                    {interest.quality === 'Strong match' && (
                      <span className="text-xs bg-green-500/30 text-green-300 px-2 py-1 rounded-full">
                        ⭐ Strong
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Examples - only for matches with exact overlaps */}
                {interest.examples && interest.examples.length > 0 && (
                  <div className="space-y-1 mb-3">
                    {interest.examples.map((example, i) => (
                      <p key={i} className="text-white/80 text-sm pl-2 border-l-2 border-white/20">
                        {example}
                      </p>
                    ))}
                  </div>
                )}
                
                {/* Ways to connect - ONLY for Strong matches */}
                {interest.ways_to_connect && interest.ways_to_connect.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <p className="text-xs text-white/50 mb-2">Ways to connect:</p>
                    <div className="flex flex-wrap gap-2">
                      {interest.ways_to_connect.map((idea, i) => (
                        <span 
                          key={i}
                          className="text-xs bg-green-500/20 text-green-300 px-3 py-1 rounded-full"
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

      {/* Score breakdown - collapsed/minimal */}
      <details className="card p-4">
        <summary className="text-white/70 text-sm cursor-pointer hover:text-white">
          📊 View detailed score breakdown
        </summary>
        
        <div className="mt-4 space-y-3">
          {Object.entries(breakdown).map(([category, data]) => (
            <div key={category}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-white/70 capitalize">{category}</span>
                <span className="text-white/50 text-xs">
                  {data.score}% similarity
                </span>
              </div>
              <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full"
                  style={{ width: `${data.score}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </details>

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
      </div>
    </div>
  )
}
