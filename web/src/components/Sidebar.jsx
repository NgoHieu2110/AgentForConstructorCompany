import { Icon } from './Icon.jsx'

const NAV = [
  { id: 'dashboard', label: 'Tổng quan', hint: 'KPI & xếp hạng', icon: 'grid' },
  { id: 'evaluate', label: 'Đánh giá mới', hint: 'Tạo dự án & báo giá', icon: 'spark' },
  { id: 'lookup', label: 'Tra cứu quyết định', hint: 'GET /decision', icon: 'search' },
]

export function Sidebar({ view, onChange, apiOnline, open, onClose }) {
  return (
    <>
      {open && (
        <button
          type="button"
          aria-label="Đóng menu"
          className="fixed inset-0 z-30 bg-navy-950/40 backdrop-blur-[2px] lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex h-dvh w-[272px] flex-col border-r border-white/10 bg-linear-to-b from-navy-900 via-navy-900 to-navy-950 text-white shadow-2xl transition-transform duration-300 lg:static lg:h-auto lg:min-h-screen lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center gap-3 px-5 py-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-accent-bright to-accent shadow-lg shadow-accent/30">
            <Icon name="chart" className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-[11px] font-semibold tracking-[0.18em] text-blue-200/70 uppercase">
              Nexus Supply
            </p>
            <p className="text-sm font-semibold">AI Supplier Desk</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {NAV.map((item) => {
            const active = view === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => {
                  onChange(item.id)
                  onClose()
                }}
                className={`group flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left transition-all duration-200 ${
                  active
                    ? 'bg-white/10 shadow-inner ring-1 ring-white/10'
                    : 'hover:bg-white/5'
                }`}
              >
                <span
                  className={`mt-0.5 rounded-lg p-1.5 ${
                    active ? 'bg-accent text-white' : 'bg-white/8 text-blue-100/80'
                  }`}
                >
                  <Icon name={item.icon} className="h-4 w-4" />
                </span>
                <span>
                  <span className="block text-sm font-semibold">{item.label}</span>
                  <span className="block text-[11px] text-blue-100/55">{item.hint}</span>
                </span>
              </button>
            )
          })}
        </nav>

        <div className="mx-3 mb-5 mt-auto rounded-xl border border-white/15 bg-white/10 p-3">
          <div className="flex items-center gap-2 text-xs">
            <span
              className={`h-2 w-2 rounded-full ${
                apiOnline === true
                  ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                  : apiOnline === false
                    ? 'bg-risk-hot'
                    : 'bg-slate-400'
              }`}
            />
            <span className="text-blue-100/80">
              {apiOnline === true
                ? 'API đang chạy'
                : apiOnline === false
                  ? 'API không phản hồi'
                  : 'Đang kiểm tra API'}
            </span>
          </div>
          <p className="mt-2 text-[11px] leading-relaxed text-blue-100/45">
            FastAPI · <code className="text-blue-100/70">127.0.0.1:8000</code>
          </p>
        </div>
      </aside>
    </>
  )
}
