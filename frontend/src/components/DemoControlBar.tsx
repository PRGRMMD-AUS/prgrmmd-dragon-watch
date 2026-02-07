import { Play, Pause, RotateCcw } from 'lucide-react'
import { useDemoControl } from '../hooks/useDemoControl'

export function DemoControlBar() {
  const { status, start, pause, reset, setSpeed, error } = useDemoControl()

  const isIdle = status?.state === 'idle'
  const isPlaying = status?.state === 'playing'
  const isPaused = status?.state === 'paused'

  const handlePlayPause = () => {
    if (isPlaying) pause()
    else if (isIdle) start(true)
    else if (isPaused) start(false)
  }

  const getSpeedClass = (preset: string) => {
    const isActive = status?.speed_label === preset
    return `px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider transition-all duration-150 ${
      isActive
        ? 'text-[var(--text-primary)] border border-[var(--border-active)]'
        : 'text-[var(--text-dim)] hover:text-[var(--text-muted)] border border-transparent'
    }`
  }

  const disabled = !!error || !status

  return (
    <div className="h-8 flex items-center px-4 gap-3 bg-[var(--bg-panel)] border-b border-[var(--border-glass)]">
      <button
        onClick={handlePlayPause}
        disabled={disabled}
        className="flex items-center gap-1.5 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-[var(--text-primary)] border border-[var(--border-active)] hover:bg-white/[0.03] disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150"
      >
        {isPlaying ? <><Pause size={10} /><span>Pause</span></> : <><Play size={10} /><span>{isIdle ? 'Start' : 'Resume'}</span></>}
      </button>

      <button
        onClick={() => reset()}
        disabled={disabled}
        className="flex items-center gap-1.5 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-[var(--text-dim)] border border-[var(--border-subtle)] hover:text-[var(--text-muted)] hover:border-[var(--border-glass)] disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150"
      >
        <RotateCcw size={10} />
        <span>Reset</span>
      </button>

      <div className="h-3 w-px bg-[var(--border-glass)]" />

      <div className="flex items-center gap-0.5">
        {(['normal', 'fast', 'slow'] as const).map((preset) => (
          <button key={preset} onClick={() => setSpeed(preset)} disabled={disabled} className={getSpeedClass(preset)}>
            {preset}
          </button>
        ))}
      </div>

      <div className="h-3 w-px bg-[var(--border-glass)]" />

      <div className="flex items-center gap-2">
        <span className="text-[10px] text-[var(--text-dim)] font-medium uppercase tracking-wider">T:</span>
        <span className="font-mono text-[11px] text-[var(--text-secondary)] font-medium tabular-nums">
          {status?.simulated_time || 'T+0h'}
        </span>
      </div>

      <div className="h-3 w-px bg-[var(--border-glass)]" />

      <div className="flex items-center gap-2 flex-1">
        <div className="flex-1 bg-white/[0.03] h-[2px] max-w-[160px]">
          <div
            className="h-full bg-[var(--text-muted)] transition-all duration-500 ease-out"
            style={{ width: `${status?.progress || 0}%` }}
          />
        </div>
        <span className="font-mono text-[10px] text-[var(--text-dim)] font-medium min-w-[28px] text-right tabular-nums">
          {status?.progress ? `${Math.round(status.progress)}%` : '0%'}
        </span>
      </div>

      {error && (
        <>
          <div className="h-3 w-px bg-[var(--border-glass)]" />
          <span className="text-[10px] text-[var(--accent)] font-medium uppercase tracking-wider">Offline</span>
        </>
      )}
    </div>
  )
}
