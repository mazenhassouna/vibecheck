export default function WaitingRoom({ sessionCode, person }) {
  return (
    <div className="space-y-6">
      {/* Session code display */}
      <div className="card p-6 text-center">
        <p className="text-white/60 text-sm mb-2">Session Code</p>
        <p className="text-3xl font-bold text-white tracking-widest">{sessionCode}</p>
      </div>

      {/* Waiting animation */}
      <div className="card p-12 text-center">
        <div className="mb-6">
          <div className="w-24 h-24 mx-auto relative">
            {/* Animated circles */}
            <div className="absolute inset-0 rounded-full border-4 border-pink-500/30 pulse-gentle"></div>
            <div className="absolute inset-2 rounded-full border-4 border-purple-500/30 pulse-gentle" style={{ animationDelay: '0.5s' }}></div>
            <div className="absolute inset-4 rounded-full border-4 border-orange-500/30 pulse-gentle" style={{ animationDelay: '1s' }}></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-4xl">⏳</span>
            </div>
          </div>
        </div>
        
        <h2 className="text-2xl font-semibold text-white mb-2">
          Waiting for your friend...
        </h2>
        
        <p className="text-white/60 mb-6">
          {person === 'a' 
            ? "Share the code above with your friend so they can join!"
            : "Your friend has uploaded their data. Waiting for results..."}
        </p>
        
        <div className="flex items-center justify-center gap-2 text-white/40">
          <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>

      {/* Tips while waiting */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          💡 While you wait...
        </h3>
        
        <div className="space-y-3 text-white/70">
          <p>
            • Your data is being processed securely
          </p>
          <p>
            • Only shared interests will be revealed
          </p>
          <p>
            • Nothing private will be shown
          </p>
          <p>
            • Results appear automatically when ready
          </p>
        </div>
      </div>

      {/* Share instructions */}
      {person === 'a' && (
        <div className="card p-6 bg-gradient-to-r from-pink-500/10 to-purple-500/10">
          <h3 className="text-lg font-semibold text-white mb-2">
            📱 Share with your friend
          </h3>
          <p className="text-white/70 mb-4">
            Tell them to go to this site and enter code:
          </p>
          <div className="bg-white/10 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-white tracking-widest">
              {sessionCode}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
