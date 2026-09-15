import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export function RankingChart({ ranking, loading, empty }) {
  const data = (ranking ?? []).map((row, i) => ({
    name: row.supplier_name,
    score: row.total_score,
    fill: i === 0 ? '#2563eb' : i === 1 ? '#64748b' : '#94a3b8',
  }))

  return (
    <section className="flex min-h-[340px] flex-col rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-bold text-navy-900">Xếp hạng điểm tổng hợp</h2>
          <p className="text-xs text-slate-500">So sánh total_score từ pipeline đánh giá</p>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-1 items-end gap-3 px-2 pb-2">
          {[72, 54, 40, 28].map((h) => (
            <div key={h} className="skeleton flex-1 rounded-t-lg" style={{ height: `${h}%` }} />
          ))}
        </div>
      ) : empty ? (
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 text-center">
          <p className="text-sm font-semibold text-slate-600">Chưa có dữ liệu biểu đồ</p>
          <p className="mt-1 max-w-xs text-xs text-slate-500">
            Chạy đánh giá mới hoặc tra cứu quyết định đã lưu để hiển thị xếp hạng.
          </p>
        </div>
      ) : (
        <div className="min-h-0 flex-1">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 8 }}>
              <CartesianGrid stroke="#e8eef6" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                interval={0}
                height={48}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: 'rgba(37,99,235,0.06)' }}
                contentStyle={{
                  borderRadius: 12,
                  border: '1px solid #e2e8f0',
                  fontSize: 12,
                }}
                formatter={(value) => [`${value}`, 'Điểm']}
              />
              <Bar dataKey="score" radius={[8, 8, 4, 4]} maxBarSize={56}>
                {data.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  )
}
