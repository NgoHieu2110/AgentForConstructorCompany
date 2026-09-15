import { sourceLabel } from '../lib/format.js'

const SOURCE_TONE = {
  rule_based: 'bg-blue-50 text-blue-700',
  ml_model: 'bg-orange-50 text-orange-700',
  llm: 'bg-emerald-50 text-emerald-700',
}

export function RankingTable({ ranking, chosenId, loading, empty }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="text-sm font-bold text-navy-900">Bảng xếp hạng chi tiết</h2>
          <p className="text-xs text-slate-500">criterion_breakdown theo từng nhà cung cấp</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        {loading ? (
          <div className="space-y-2 p-5">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton h-12 rounded-lg" />
            ))}
          </div>
        ) : empty ? (
          <div className="px-5 py-12 text-center text-sm text-slate-500">
            Bảng trống — chưa có ranking từ API.
          </div>
        ) : (
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-[11px] tracking-wide text-slate-500 uppercase">
              <tr>
                <th className="px-5 py-3 font-semibold">#</th>
                <th className="px-5 py-3 font-semibold">Nhà cung cấp</th>
                <th className="px-5 py-3 font-semibold">Tổng điểm</th>
                <th className="px-5 py-3 font-semibold">Tiêu chí</th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((row, i) => {
                const chosen = row.supplier_id === chosenId
                return (
                  <tr
                    key={row.supplier_id}
                    className={`border-t border-slate-100 transition hover:bg-slate-50/80 ${
                      chosen ? 'bg-blue-50/50' : ''
                    }`}
                  >
                    <td className="px-5 py-4 font-bold text-slate-400">{i + 1}</td>
                    <td className="px-5 py-4">
                      <div className="font-semibold text-navy-900">{row.supplier_name}</div>
                      {chosen && (
                        <span className="mt-1 inline-flex rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent">
                          Đề xuất
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 font-mono text-base font-bold text-navy-900">
                      {row.total_score}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex min-w-[280px] flex-col gap-2">
                        {(row.criterion_breakdown ?? []).map((c) => (
                          <div key={c.criterion} className="grid grid-cols-[110px_1fr_42px] items-center gap-2">
                            <span className="truncate text-xs text-slate-500">{c.criterion}</span>
                            <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                              <div
                                className="h-full rounded-full bg-navy-700"
                                style={{ width: `${Math.round(c.normalized_score * 100)}%` }}
                              />
                            </div>
                            <span
                              className={`justify-self-end rounded-md px-1.5 py-0.5 text-[10px] font-semibold ${
                                SOURCE_TONE[c.computed_by] || 'bg-slate-100 text-slate-600'
                              }`}
                              title={sourceLabel(c.computed_by)}
                            >
                              {Math.round(c.normalized_score * 100)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}
