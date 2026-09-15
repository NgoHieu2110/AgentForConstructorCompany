import { Icon } from './Icon.jsx'

export function TopNav({ title, subtitle, onMenu, loading, projectId }) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            className="rounded-lg p-2 text-navy-800 transition hover:bg-slate-100 lg:hidden"
            onClick={onMenu}
            aria-label="Mở menu"
          >
            <Icon name="menu" />
          </button>
          <div className="min-w-0">
            <h1 className="truncate text-base font-bold tracking-tight text-navy-900 sm:text-lg">
              {title}
            </h1>
            <p className="truncate text-xs text-slate-500 sm:text-sm">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {projectId && (
            <span className="hidden max-w-[220px] truncate rounded-full border border-slate-200 bg-slate-50 px-3 py-1 font-mono text-[11px] text-slate-500 md:inline">
              {projectId}
            </span>
          )}
          {loading && (
            <span className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-accent">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
              Đang xử lý
            </span>
          )}
          <div className="hidden h-9 w-9 items-center justify-center rounded-full bg-linear-to-br from-navy-800 to-navy-950 text-xs font-bold text-white sm:flex">
            NC
          </div>
        </div>
      </div>
    </header>
  )
}
