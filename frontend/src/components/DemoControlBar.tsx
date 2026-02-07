import { Play, Pause, RotateCcw } from 'lucide-react'
import { useDemoControl } from '../hooks/useDemoControl'

export function DemoControlBar() {
  const { status, start, pause, reset, setSpeed, error } = useDemoControl()

  const isIdle = status?.state === 'idle'
  const isPlaying = status?.state === 'playing'
  const isPaused = status?.state === 'paused'

  // Determine if this is the first start (idle) or resume (paused)
  const handlePlayPause = () => {
    if (isPlaying) {
      pause()
    } else if (isIdle) {
      // First start - clear tables
      start(true)
    } else if (isPaused) {
      // Resume - don't clear tables
      start(false)
    }
  }

  const handleReset = () => {
    reset()
  }

  const handleSpeedChange = (speed: number) => {
    setSpeed(speed)
  }

  // Progress bar color based on phase
  const getProgressColor = () => {
    const progress = status?.progress || 0
    if (progress < 33) return 'bg-emerald-500'
    if (progress < 67) return 'bg-amber-500'
    return 'bg-red-600'
  }

  // Speed preset button styles
  const getSpeedButtonClass = (targetSpeed: number) => {
    const isActive = status?.speed === targetSpeed
    return `px-3 py-1 text-xs font-medium rounded transition-colors ${
      isActive
        ? 'bg-slate-700 text-white'
        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    }`
  }

  // Disable controls if backend not connected
  const disabled = !!error || !status

  return (
    <div className="bg-white border-b border-slate-200 h-9 flex items-center px-4 gap-4">
      {/* Play/Pause Button */}
      <button
        onClick={handlePlayPause}
        disabled={disabled}
        className="flex items-center gap-1.5 px-3 py-1 text-xs font-medium bg-slate-700 text-white rounded hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isPlaying ? (
          <>
            <Pause size={14} />
            <span>Pause</span>
          </>
        ) : (
          <>
            <Play size={14} />
            <span>{isIdle ? 'Start' : 'Resume'}</span>
          </>
        )}
      </button>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        disabled={disabled}
        className="flex items-center gap-1.5 px-3 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <RotateCcw size={14} />
        <span>Reset</span>
      </button>

      {/* Divider */}
      <div className="h-5 w-px bg-slate-200" />

      {/* Speed Presets */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleSpeedChange(1.0)}
          disabled={disabled}
          className={getSpeedButtonClass(1.0)}
        >
          Normal
        </button>
        <button
          onClick={() => handleSpeedChange(2.0)}
          disabled={disabled}
          className={getSpeedButtonClass(2.0)}
        >
          Fast
        </button>
        <button
          onClick={() => handleSpeedChange(0.5)}
          disabled={disabled}
          className={getSpeedButtonClass(0.5)}
        >
          Slow
        </button>
      </div>

      {/* Divider */}
      <div className="h-5 w-px bg-slate-200" />

      {/* Simulated Clock */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500 font-medium">Scenario Time:</span>
        <span className="font-mono text-xs text-slate-700 font-semibold">
          {status?.simulated_time || 'T+0h'}
        </span>
      </div>

      {/* Divider */}
      <div className="h-5 w-px bg-slate-200" />

      {/* Progress Indicator */}
      <div className="flex items-center gap-2 flex-1">
        <span className="text-xs text-slate-500 font-medium">Progress:</span>
        <div className="flex-1 bg-slate-100 rounded-full h-2 max-w-[200px]">
          <div
            className={`h-full rounded-full transition-all duration-300 ${getProgressColor()}`}
            style={{ width: `${status?.progress || 0}%` }}
          />
        </div>
        <span className="text-xs text-slate-600 font-medium min-w-[35px] text-right">
          {status?.progress ? `${Math.round(status.progress)}%` : '0%'}
        </span>
      </div>

      {/* Error State */}
      {error && (
        <>
          <div className="h-5 w-px bg-slate-200" />
          <span className="text-xs text-red-600 font-medium">
            Backend not connected
          </span>
        </>
      )}
    </div>
  )
}
