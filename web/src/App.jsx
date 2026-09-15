import { useEffect, useMemo, useState } from 'react'
import { api } from './api/client.js'
import { formatDate } from './lib/format.js'
import { Sidebar } from './components/Sidebar.jsx'
import { TopNav } from './components/TopNav.jsx'
import { KpiCards } from './components/KpiCards.jsx'
import { RankingChart } from './components/RankingChart.jsx'
import { RiskPanel } from './components/RiskPanel.jsx'
import { RankingTable } from './components/RankingTable.jsx'
import {
  DEMO_PROJECT,
  DEMO_SUPPLIERS,
  EvaluateForm,
} from './components/EvaluateForm.jsx'
import { LookupPanel } from './components/LookupPanel.jsx'

const STORAGE_KEY = 'nexus-supply-last-result'

export default function App() {
  const [view, setView] = useState('dashboard')
  const [menuOpen, setMenuOpen] = useState(false)
  const [apiOnline, setApiOnline] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState('')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [project, setProject] = useState(DEMO_PROJECT)
  const [suppliers, setSuppliers] = useState(DEMO_SUPPLIERS)
  const [lookupId, setLookupId] = useState('')

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY)
      if (raw) setResult(JSON.parse(raw))
    } catch {
      /* ignore */
    }
    pingApi()
  }, [])

  useEffect(() => {
    if (result) sessionStorage.setItem(STORAGE_KEY, JSON.stringify(result))
  }, [result])

  async function pingApi() {
    try {
      await api.health()
      setApiOnline(true)
    } catch {
      setApiOnline(false)
    }
  }

  const ranking = result?.ranking ?? []
  const empty = ranking.length === 0
  const titles = {
    dashboard: ['Tổng quan quyết định', 'KPI, biểu đồ xếp hạng và phân tích rủi ro'],
    evaluate: ['Đánh giá mới', 'Tạo dự án, báo giá rồi chạy pipeline AI'],
    lookup: ['Tra cứu quyết định', 'Tải kết quả đã lưu theo project_id'],
  }

  async function runEvaluation() {
    if (suppliers.length < 2) {
      setError('Cần ít nhất 2 nhà cung cấp để so sánh.')
      return
    }
    setError('')
    setLoading(true)
    try {
      setProgress('Đang tạo dự án…')
      const createdProject = await api.createProject({
        name: project.name,
        province: project.province,
        budget: Number(project.budget),
        required_deadline: project.required_deadline || null,
        requires_public_bidding: project.requires_public_bidding,
      })

      for (let i = 0; i < suppliers.length; i += 1) {
        const row = suppliers[i]
        setProgress(`Đang ghi nhà cung cấp ${i + 1}/${suppliers.length}…`)
        const createdSupplier = await api.createSupplier({
          name: row.name,
          province: row.province,
          financial_rating: row.financial_rating || null,
        })
        await api.createBid({
          project_id: createdProject.project_id,
          supplier_id: createdSupplier.supplier_id,
          category_name: row.category_name,
          unit_price: Number(row.unit_price),
          quantity_offered: Number(row.quantity_offered),
          proposed_delivery_days: Number(row.proposed_delivery_days),
        })
      }

      setProgress('AI đang phân tích: trọng số, rule-based, ML rủi ro, uy tín LLM…')
      const evalResult = await api.evaluateProject(createdProject.project_id)
      setResult({
        ...evalResult,
        project_id: createdProject.project_id,
        project_name: createdProject.name,
        decided_at: new Date().toISOString(),
      })
      setLookupId(createdProject.project_id)
      setView('dashboard')
    } catch (err) {
      setError(err.message || 'Không gọi được API. Kiểm tra backend tại cổng 8000.')
    } finally {
      setLoading(false)
      setProgress('')
    }
  }

  async function loadDecision() {
    setError('')
    setLoading(true)
    setProgress('Đang tải quyết định đã lưu…')
    try {
      const data = await api.getDecision(lookupId)
      setResult({
        ...data,
        project_id: lookupId,
        decision_id: data.decision_id ?? null,
      })
      setView('dashboard')
    } catch (err) {
      setError(err.message || 'Không tải được quyết định.')
    } finally {
      setLoading(false)
      setProgress('')
    }
  }

  const subtitle = useMemo(() => {
    if (result?.decided_at) return `${titles[view][1]} · ${formatDate(result.decided_at)}`
    return titles[view][1]
  }, [result, view])

  return (
    <div className="flex min-h-screen bg-slate-200/80">
      <Sidebar
        view={view}
        onChange={setView}
        apiOnline={apiOnline}
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav
          title={titles[view][0]}
          subtitle={subtitle}
          onMenu={() => setMenuOpen(true)}
          loading={loading}
          projectId={result?.project_id}
        />

        <main className="relative flex-1 px-4 py-5 sm:px-6">

          {apiOnline === false && (
            <div className="relative mb-4 rounded-xl border border-orange-200 bg-orange-50 px-4 py-3 text-sm text-orange-800">
              Không kết nối được API. Chạy <code className="font-mono">uvicorn api.main:app --reload</code> tại cổng 8000.
            </div>
          )}

          {error && (
            <div className="relative mb-4 flex items-start justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
              <span>{error}</span>
              <button type="button" className="text-xs font-semibold" onClick={() => setError('')}>
                Đóng
              </button>
            </div>
          )}

          {view === 'evaluate' && (
            <div className="relative">
              <EvaluateForm
                project={project}
                setProject={setProject}
                suppliers={suppliers}
                setSuppliers={setSuppliers}
                onSubmit={runEvaluation}
                loading={loading}
                progress={progress}
              />
            </div>
          )}

          {view === 'lookup' && (
            <div className="relative">
              <LookupPanel
                projectId={lookupId}
                setProjectId={setLookupId}
                onSubmit={loadDecision}
                loading={loading}
              />
            </div>
          )}

          {view === 'dashboard' && (
            <div className="relative space-y-4">
              <KpiCards
                ranking={ranking}
                chosenId={result?.chosen_supplier_id}
                loading={loading}
                empty={empty}
              />
              <div className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
                <RankingChart ranking={ranking} loading={loading} empty={empty} />
                <RiskPanel
                  ranking={ranking}
                  explanation={result?.explanation}
                  loading={loading}
                  empty={empty}
                />
              </div>
              <RankingTable
                ranking={ranking}
                chosenId={result?.chosen_supplier_id}
                loading={loading}
                empty={empty}
              />
              {empty && !loading && (
                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <p className="text-sm font-bold text-navy-900">Chưa có kết quả đánh giá</p>
                  <p className="mt-1 max-w-2xl text-sm text-slate-600">
                    Tạo dự án và báo giá, rồi chạy pipeline — hoặc nhập project_id để tải quyết định đã lưu.
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setView('evaluate')}
                      className="rounded-xl bg-navy-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-navy-700"
                    >
                      Tạo đánh giá mới
                    </button>
                    <button
                      type="button"
                      onClick={() => setView('lookup')}
                      className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-navy-800 transition hover:border-accent hover:text-accent"
                    >
                      Tra cứu quyết định
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
