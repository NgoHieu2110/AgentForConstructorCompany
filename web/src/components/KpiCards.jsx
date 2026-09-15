function Card({ label, value, hint, accent, loading }) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div
        className={`absolute inset-x-0 top-0 h-0.5 ${accent}`}
      />
      <p className="text-[11px] font-semibold tracking-[0.14em] text-slate-400 uppercase">
        {label}
      </p>
      {loading ? (
        <div className="skeleton mt-3 h-8 w-28 rounded-lg" />
      ) : (
        <p className="mt-2 truncate text-2xl font-extrabold tracking-tight text-navy-900">
          {value}
        </p>
      )}
      <p className="mt-1 text-xs text-slate-500">{loading ? 'Đang tải…' : hint}</p>
    </div>
  )
}

export function KpiCards({ ranking, chosenId, loading, empty }) {
  const winner = ranking?.find((r) => r.supplier_id === chosenId) ?? ranking?.[0]
  const runner = ranking?.[1]
  const gap =
    winner && runner ? (winner.total_score - runner.total_score).toFixed(1) : null
  const riskItem = winner?.criterion_breakdown?.find((c) => c.criterion === 'Rủi ro chậm/lỗi')
  const riskPct = riskItem ? Math.round((1 - riskItem.normalized_score) * 100) : null

  if (empty && !loading) {
    return (
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {['Nhà cung cấp đề xuất', 'Điểm tổng hợp', 'Số ứng viên', 'Rủi ro NCC chọn'].map(
          (label) => (
            <div
              key={label}
              className="rounded-2xl border border-dashed border-slate-300 bg-white p-4 shadow-sm"
            >
              <p className="text-[11px] font-semibold tracking-[0.14em] text-slate-500 uppercase">
                {label}
              </p>
              <p className="mt-2 text-2xl font-bold text-slate-400">—</p>
              <p className="mt-1 text-xs text-slate-500">Chưa có đánh giá</p>
            </div>
          ),
        )}
      </div>
    )
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Card
        label="Nhà cung cấp đề xuất"
        value={winner?.supplier_name ?? '—'}
        hint="Điểm cao nhất sau pipeline AI"
        accent="bg-linear-to-r from-accent to-sky-400"
        loading={loading}
      />
      <Card
        label="Điểm tổng hợp"
        value={winner ? `${winner.total_score}` : '—'}
        hint="Thang 0–100, đã nhân trọng số"
        accent="bg-linear-to-r from-navy-700 to-accent"
        loading={loading}
      />
      <Card
        label="Số ứng viên"
        value={ranking?.length ?? 0}
        hint={gap != null ? `Cách biệt #2: +${gap}` : 'Cần ≥ 2 NCC để so sánh'}
        accent="bg-linear-to-r from-slate-400 to-slate-300"
        loading={loading}
      />
      <Card
        label="Rủi ro NCC chọn"
        value={riskPct == null ? '—' : `${riskPct}%`}
        hint="1 − điểm chuẩn hoá tiêu chí rủi ro"
        accent="bg-linear-to-r from-orange-500 to-red-500"
        loading={loading}
      />
    </div>
  )
}
