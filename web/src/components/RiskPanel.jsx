import { riskScore } from '../lib/format.js'

function RiskBar({ value }) {
  const pct = Math.round(value * 100)
  const tone =
    pct >= 60 ? 'from-red-500 to-orange-500' : pct >= 35 ? 'from-orange-400 to-amber-400' : 'from-emerald-400 to-teal-400'
  return (
    <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
      <div
        className={`h-full rounded-full bg-linear-to-r ${tone} transition-all duration-500`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

export function RiskPanel({ ranking, explanation, loading, empty }) {
  const rows = [...(ranking ?? [])]
    .map((r) => ({ ...r, risk: riskScore(r) }))
    .sort((a, b) => (b.risk ?? 0) - (a.risk ?? 0))

  return (
    <section className="flex min-h-[340px] flex-col rounded-2xl border border-slate-200/80 bg-linear-to-b from-white to-orange-50/40 p-5 shadow-sm">
      <div className="mb-4">
        <p className="text-[11px] font-semibold tracking-[0.16em] text-orange-600 uppercase">
          Risk analysis
        </p>
        <h2 className="text-sm font-bold text-navy-900">Phân tích rủi ro chậm / lỗi</h2>
        <p className="text-xs text-slate-500">
          Từ tiêu chí ML “Rủi ro chậm/lỗi” (normalized_score đảo ngược)
        </p>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-12 rounded-xl" />
          ))}
        </div>
      ) : empty ? (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-orange-200 bg-white text-center">
          <p className="px-4 text-sm font-medium text-slate-600">Chưa có tín hiệu rủi ro để hiển thị.</p>
        </div>
      ) : (
        <>
          <ul className="space-y-3">
            {rows.map((row) => (
              <li key={row.supplier_id}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="font-semibold text-navy-800">{row.supplier_name}</span>
                  <span className="font-mono text-orange-700">
                    {row.risk == null ? '—' : `${Math.round(row.risk * 100)}%`}
                  </span>
                </div>
                <RiskBar value={row.risk ?? 0} />
              </li>
            ))}
          </ul>
          <div className="mt-4 flex-1 rounded-xl border border-orange-100 bg-white/80 p-3">
            <p className="text-[10px] font-semibold tracking-[0.12em] text-orange-600 uppercase">
              Giải thích AI
            </p>
            <p className="mt-1 text-sm leading-relaxed text-slate-700">
              {explanation || 'Không có explanation_text.'}
            </p>
          </div>
        </>
      )}
    </section>
  )
}
