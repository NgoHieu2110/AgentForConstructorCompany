export function LookupPanel({ projectId, setProjectId, onSubmit, loading }) {
  return (
    <form
      className="mx-auto max-w-xl rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <h2 className="text-sm font-bold text-navy-900">Tra cứu quyết định đã lưu</h2>
      <p className="mt-1 text-xs text-slate-500">
        GET /projects/{'{project_id}'}/decision — không chạy lại pipeline.
      </p>
      <label className="mt-4 block text-xs font-medium text-slate-600">
        project_id
        <input
          required
          value={projectId}
          onChange={(e) => setProjectId(e.target.value.trim())}
          placeholder="UUID từ lần tạo dự án"
          className="input mt-1 font-mono"
        />
      </label>
      <button
        type="submit"
        disabled={loading}
        className="mt-4 w-full rounded-xl bg-navy-900 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-700 disabled:opacity-60"
      >
        {loading ? 'Đang tải…' : 'Lấy quyết định mới nhất'}
      </button>
    </form>
  )
}
