const EMPTY_SUPPLIER = {
  name: '',
  province: '',
  financial_rating: 'A',
  category_name: 'Thép xây dựng',
  unit_price: '',
  quantity_offered: '1',
  proposed_delivery_days: '',
}

export const DEMO_PROJECT = {
  name: 'Xây cầu Sông Hàn giai đoạn 2',
  province: 'Đà Nẵng',
  budget: '15000000000',
  required_deadline: '2026-12-31',
  requires_public_bidding: true,
}

export const DEMO_SUPPLIERS = [
  {
    name: 'Công ty Thép ABC',
    province: 'Đà Nẵng',
    financial_rating: 'A',
    category_name: 'Thép xây dựng',
    unit_price: '18500000',
    quantity_offered: '1',
    proposed_delivery_days: '20',
  },
  {
    name: 'Công ty Thép XYZ',
    province: 'Đà Nẵng',
    financial_rating: 'B',
    category_name: 'Thép xây dựng',
    unit_price: '17800000',
    quantity_offered: '1',
    proposed_delivery_days: '25',
  },
  {
    name: 'Công ty Thép Miền Trung',
    province: 'Huế',
    financial_rating: 'A',
    category_name: 'Thép xây dựng',
    unit_price: '19000000',
    quantity_offered: '1',
    proposed_delivery_days: '15',
  },
]

export function EvaluateForm({
  project,
  setProject,
  suppliers,
  setSuppliers,
  onSubmit,
  loading,
  progress,
}) {
  function updateSupplier(index, patch) {
    setSuppliers((rows) => rows.map((row, i) => (i === index ? { ...row, ...patch } : row)))
  }

  return (
    <form
      className="mx-auto max-w-3xl space-y-6"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <section className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-bold text-navy-900">Thông tin dự án</h2>
        <p className="mb-4 text-xs text-slate-500">POST /projects</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Tên dự án">
            <input
              required
              value={project.name}
              onChange={(e) => setProject({ ...project, name: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Tỉnh / thành">
            <input
              required
              value={project.province}
              onChange={(e) => setProject({ ...project, province: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Ngân sách (VND)">
            <input
              required
              type="number"
              min="0"
              value={project.budget}
              onChange={(e) => setProject({ ...project, budget: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Hạn chót">
            <input
              type="date"
              value={project.required_deadline}
              onChange={(e) => setProject({ ...project, required_deadline: e.target.value })}
              className="input"
            />
          </Field>
        </div>
        <label className="mt-4 flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={project.requires_public_bidding}
            onChange={(e) =>
              setProject({ ...project, requires_public_bidding: e.target.checked })
            }
            className="h-4 w-4 rounded border-slate-300 text-accent"
          />
          Yêu cầu đấu thầu công khai
        </label>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-navy-900">Nhà cung cấp & báo giá</h2>
            <p className="text-xs text-slate-500">POST /suppliers rồi POST /bids cho từng dòng</p>
          </div>
          <button
            type="button"
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-navy-800 transition hover:border-accent hover:text-accent"
            onClick={() => setSuppliers((rows) => [...rows, { ...EMPTY_SUPPLIER }])}
          >
            + Thêm NCC
          </button>
        </div>

        {suppliers.map((row, index) => (
          <article
            key={index}
            className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm transition hover:border-slate-300"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="rounded-md bg-navy-900 px-2 py-0.5 text-[11px] font-semibold text-white">
                NCC {index + 1}
              </span>
              {suppliers.length > 2 && (
                <button
                  type="button"
                  className="text-xs text-red-600 hover:underline"
                  onClick={() => setSuppliers((rows) => rows.filter((_, i) => i !== index))}
                >
                  Xoá
                </button>
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <Field label="Tên">
                <input
                  required
                  value={row.name}
                  onChange={(e) => updateSupplier(index, { name: e.target.value })}
                  className="input"
                />
              </Field>
              <Field label="Địa phương">
                <input
                  required
                  value={row.province}
                  onChange={(e) => updateSupplier(index, { province: e.target.value })}
                  className="input"
                />
              </Field>
              <Field label="Rating tài chính">
                <select
                  value={row.financial_rating}
                  onChange={(e) => updateSupplier(index, { financial_rating: e.target.value })}
                  className="input"
                >
                  <option>A</option>
                  <option>B</option>
                  <option>C</option>
                </select>
              </Field>
              <Field label="Loại vật tư">
                <input
                  required
                  value={row.category_name}
                  onChange={(e) => updateSupplier(index, { category_name: e.target.value })}
                  className="input"
                />
              </Field>
              <Field label="Đơn giá">
                <input
                  required
                  type="number"
                  min="0"
                  value={row.unit_price}
                  onChange={(e) => updateSupplier(index, { unit_price: e.target.value })}
                  className="input"
                />
              </Field>
              <Field label="Số lượng">
                <input
                  required
                  type="number"
                  min="0"
                  step="any"
                  value={row.quantity_offered}
                  onChange={(e) => updateSupplier(index, { quantity_offered: e.target.value })}
                  className="input"
                />
              </Field>
              <Field label="Thời gian giao (ngày)">
                <input
                  required
                  type="number"
                  min="0"
                  value={row.proposed_delivery_days}
                  onChange={(e) =>
                    updateSupplier(index, { proposed_delivery_days: e.target.value })
                  }
                  className="input"
                />
              </Field>
            </div>
          </article>
        ))}
      </section>

      {progress && (
        <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-accent">
          <div className="mb-2 flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
            {progress}
          </div>
          <div className="h-1 overflow-hidden rounded-full bg-blue-100">
            <div className="h-full w-2/3 animate-pulse rounded-full bg-accent" />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-linear-to-r from-navy-900 to-navy-700 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-navy-900/20 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Đang chạy pipeline…' : 'Chạy đánh giá AI'}
      </button>
    </form>
  )
}

function Field({ label, children }) {
  return (
    <label className="block text-xs font-medium text-slate-600">
      {label}
      <div className="mt-1">{children}</div>
    </label>
  )
}
