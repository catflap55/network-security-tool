import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  api,
  getConsoleToken,
  type Finding,
  type Job,
  type JobDiff,
  type PluginInfo,
  type Project,
  type Schedule,
  type Settings,
} from './api'
import { CopyBtn } from './CopyBtn'
import { TokenGate } from './TokenGate'
import {
  QUICK_START_STEPS,
  autoFixSnippets,
  friendlyJobError,
  jobLogIntro,
  jobStatusPlain,
  laymanForFinding,
  severityPlain,
} from './noviceGuide'
import './App.css'

export default function App() {
  const [unlocked, setUnlocked] = useState(() => Boolean(getConsoleToken()))
  const [tokenError, setTokenError] = useState<string | null>(null)
  const [settings, setSettings] = useState<Settings | null>(null)
  const [settingsError, setSettingsError] = useState<string | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [plugins, setPlugins] = useState<PluginInfo[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [pluginId, setPluginId] = useState('nmap_quick')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [playbook, setPlaybook] = useState<{ key: string; md: string } | null>(null)
  const [pollJobId, setPollJobId] = useState<number | null>(null)
  const logPreRef = useRef<HTMLPreElement>(null)
  const [newProj, setNewProj] = useState({
    name: '',
    targets: '127.0.0.1',
    environment: 'mixed',
  })
  const [diffOld, setDiffOld] = useState<number | ''>('')
  const [diffNew, setDiffNew] = useState<number | ''>('')
  const [diff, setDiff] = useState<JobDiff | null>(null)
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [schedHours, setSchedHours] = useState(24)

  const selectedPlugin = useMemo(
    () => plugins.find((p) => p.id === pluginId),
    [plugins, pluginId],
  )

  const findingsNeedAttention = useMemo(
    () => findings.filter((f) => laymanForFinding(f).needsFix).length,
    [findings],
  )

  const loadSettings = useCallback(async () => {
    setSettingsError(null)
    try {
      setSettings(await api.getSettings())
    } catch (e) {
      if (e instanceof Error && e.message === 'TOKEN_REQUIRED') {
        setUnlocked(false)
        setTokenError('That token was rejected. Copy CONSOLE_TOKEN from backend/.env and try again.')
        return
      }
      setSettingsError(e instanceof Error ? e.message : 'Failed to load settings')
    }
  }, [])

  const loadProjects = useCallback(async () => {
    try {
      setProjects(await api.listProjects())
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Failed to load projects')
    }
  }, [])

  const loadPlugins = useCallback(async () => {
    try {
      setPlugins(await api.listPlugins())
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Failed to load plugins')
    }
  }, [])

  useEffect(() => {
    if (!unlocked) return
    void loadSettings()
    void loadPlugins()
    void api.listSchedules().then(setSchedules).catch(() => setSchedules([]))
  }, [unlocked, loadSettings, loadPlugins])

  useEffect(() => {
    if (settings?.authorization_acknowledged) void loadProjects()
  }, [settings?.authorization_acknowledged, loadProjects])

  useEffect(() => {
    if (!selectedProjectId) {
      setJobs([])
      return
    }
    void (async () => {
      try {
        setJobs(await api.listJobs(selectedProjectId))
      } catch (e) {
        setErr(e instanceof Error ? e.message : 'Failed to load jobs')
      }
    })()
  }, [selectedProjectId])

  useEffect(() => {
    if (!selectedProjectId || !selectedJobId) {
      setFindings([])
      return
    }
    if (pollJobId === selectedJobId) {
      return
    }
    void (async () => {
      try {
        setFindings(await api.listFindings(selectedProjectId, selectedJobId))
      } catch {
        setFindings([])
      }
    })()
  }, [selectedProjectId, selectedJobId, pollJobId])

  useEffect(() => {
    if (!selectedProjectId || pollJobId === null) return
    let cancelled = false
    const tick = async () => {
      try {
        const j = await api.getJob(selectedProjectId, pollJobId)
        if (cancelled) return
        setJobs((prev) => {
          const rest = prev.filter((x) => x.id !== j.id)
          return [j, ...rest].sort((a, b) => b.id - a.id)
        })
        if (j.status === 'completed' || j.status === 'failed' || j.status === 'cancelled') {
          setPollJobId(null)
          setSelectedJobId(j.id)
          try {
            const list = await api.listJobs(selectedProjectId)
            if (!cancelled) setJobs(list)
          } catch {
            /* keep local merge */
          }
        }
      } catch {
        /* ignore transient errors while polling */
      }
    }
    void tick()
    const id = window.setInterval(tick, 450)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [selectedProjectId, pollJobId])

  const logFocusId = pollJobId ?? selectedJobId
  const logJob = useMemo(
    () => (logFocusId != null ? jobs.find((j) => j.id === logFocusId) ?? null : null),
    [jobs, logFocusId],
  )

  useEffect(() => {
    const el = logPreRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [logJob?.log_text, logJob?.status])

  async function saveAuth(checked: boolean) {
    setBusy(true)
    setErr(null)
    try {
      setSettings(await api.putSettings({ authorization_acknowledged: checked }))
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Save failed')
    } finally {
      setBusy(false)
    }
  }

  async function createProject(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setErr(null)
    try {
      const p = await api.createProject(newProj)
      setNewProj({ name: '', targets: '127.0.0.1', environment: 'mixed' })
      await loadProjects()
      setSelectedProjectId(p.id)
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Create failed')
    } finally {
      setBusy(false)
    }
  }

  async function runScan() {
    if (!selectedProjectId) return
    const plug = plugins.find((p) => p.id === pluginId)
    if (!plug?.available) {
      setErr('Select an available plugin (unlocked in the list).')
      return
    }
    setBusy(true)
    setErr(null)
    try {
      const job = await api.startJob(selectedProjectId, pluginId)
      setSelectedJobId(job.id)
      setPollJobId(job.id)
      setJobs((prev) => {
        const rest = prev.filter((x) => x.id !== job.id)
        return [job, ...rest].sort((a, b) => b.id - a.id)
      })
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Scan failed')
    } finally {
      setBusy(false)
    }
  }

  async function openPlaybook(key: string) {
    try {
      const p = await api.getPlaybook(key)
      setPlaybook({ key: p.remediation_key, md: p.markdown })
    } catch {
      setPlaybook({ key, md: '_No playbook in console for this key. See docs/REMEDIATION_PLAYBOOKS.md_' })
    }
  }

  const selectedJob = jobs.find((j) => j.id === selectedJobId) ?? null

  function jobStatusClass(s: string) {
    if (s === 'running' || s === 'pending') return 'job-status-active'
    if (s === 'cancelled') return 'job-status-cancelled'
    if (s === 'failed') return 'job-status-failed'
    if (s === 'completed') return 'job-status-done'
    return ''
  }

  const canStop =
    selectedProjectId != null &&
    logFocusId != null &&
    logJob != null &&
    (logJob.status === 'running' || logJob.status === 'pending')

  if (!unlocked) {
    return (
      <TokenGate
        error={tokenError}
        onReady={() => {
          setTokenError(null)
          setUnlocked(true)
        }}
      />
    )
  }

  async function stopScan() {
    if (!selectedProjectId || logFocusId == null) return
    setErr(null)
    try {
      await api.cancelJob(selectedProjectId, logFocusId)
      const j = await api.getJob(selectedProjectId, logFocusId)
      setJobs((prev) => {
        const rest = prev.filter((x) => x.id !== j.id)
        return [j, ...rest].sort((a, b) => b.id - a.id)
      })
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Stop failed')
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Network security check</h1>
          <p className="sub">
            For your own network only. We scan, then explain results in plain language — no jargon
            required.
          </p>
        </div>
        <code className="api" title="Backend address">
          {api.displayUrl}
          {import.meta.env.DEV && !import.meta.env.VITE_API_URL ? ' · dev' : ''}
        </code>
      </header>

      {settingsError && (
        <div className="banner warn">
          <strong>This page cannot talk to the checker.</strong> Start the backend first (the
          second part of the app). From the project folder run <code>npm run api</code>, then refresh.
          <details className="novice-details">
            <summary>More help</summary>
            <p className="small">
              You need Python and packages: <code>pip install -r backend/requirements.txt</code>.
              Technical detail: {api.displayUrl} — {settingsError}
            </p>
          </details>
        </div>
      )}

      {err && (
        <div className="banner error">
          <pre>{err}</pre>
          <button type="button" className="btn ghost" onClick={() => setErr(null)}>
            Dismiss
          </button>
        </div>
      )}

      <details className="card novice-welcome" open>
        <summary className="novice-welcome-summary">How to use this (click to collapse)</summary>
        <ol className="quick-steps">
          {QUICK_START_STEPS.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
        <p className="small muted novice-tip">
          <strong>Auto-fix:</strong> where we can, we offer copy-paste commands. You still review and
          run them — we never change your PC without you doing it.
        </p>
      </details>

      <section className="card">
        <h2>Permission</h2>
        <p className="muted plain-lead">
          Only use this on <strong>your</strong> Wi‑Fi or gear you are allowed to test.
        </p>
        {settings && (
          <label className="check">
            <input
              type="checkbox"
              checked={settings.authorization_acknowledged}
              disabled={busy}
              onChange={(e) => void saveAuth(e.target.checked)}
            />
            I am allowed to scan the targets I type in below.
          </label>
        )}
        {settings && settings.lab_mode_enabled && (
          <p className="small muted">Extra lab scans: on (for advanced users).</p>
        )}
      </section>

      <section className="card">
        <h2>Your network checks</h2>
        {settings?.authorization_acknowledged ? (
          <>
            <form className="rowform" onSubmit={createProject}>
              <input
                placeholder="Name"
                value={newProj.name}
                onChange={(e) => setNewProj({ ...newProj, name: e.target.value })}
                required
              />
              <input
                placeholder="Targets (comma-separated IPs/CIDR)"
                value={newProj.targets}
                onChange={(e) => setNewProj({ ...newProj, targets: e.target.value })}
                required
              />
              <select
                value={newProj.environment}
                onChange={(e) => setNewProj({ ...newProj, environment: e.target.value })}
              >
                <option value="home">home</option>
                <option value="lab">lab</option>
                <option value="office">office</option>
                <option value="mixed">mixed</option>
              </select>
              <button type="submit" className="btn" disabled={busy}>
                Add project
              </button>
            </form>
            <div className="grid2">
              <div>
                <h3>Saved targets</h3>
                <ul className="list">
                  {projects.map((p) => (
                    <li key={p.id}>
                      <button
                        type="button"
                        className={p.id === selectedProjectId ? 'link active' : 'link'}
                        onClick={() => {
                          setSelectedProjectId(p.id)
                          setSelectedJobId(null)
                          setPollJobId(null)
                        }}
                      >
                        {p.name}
                      </button>
                      <span className="muted small"> — {p.environment}</span>
                      <button
                        type="button"
                        className="btn tiny danger"
                        onClick={() => {
                          void (async () => {
                            if (!confirm(`Delete project "${p.name}"?`)) return
                            try {
                              await api.deleteProject(p.id)
                              await loadProjects()
                              if (selectedProjectId === p.id) {
                                setSelectedProjectId(null)
                                setSelectedJobId(null)
                                setPollJobId(null)
                              }
                            } catch (e) {
                              setErr(e instanceof Error ? e.message : 'Delete failed')
                            }
                          })()
                        }}
                      >
                        Delete
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                {selectedProjectId && (
                  <>
                    <h3>Run a check</h3>
                    <label className="block">
                      Check type
                      <select
                        value={pluginId}
                        onChange={(e) => setPluginId(e.target.value)}
                      >
                        {plugins.map((p) => (
                          <option key={p.id} value={p.id} disabled={!p.available}>
                            {p.display_name}
                            {p.requires_lab_mode ? ' (lab)' : ''}
                            {!p.available ? ' — locked' : ''}
                          </option>
                        ))}
                      </select>
                    </label>
                    {plugins.some((p) => !p.available) && (
                      <p className="plugin-locked-hint small muted">
                        Some check types are locked until your setup turns them on:{' '}
                        {plugins
                          .filter((p) => !p.available)
                          .map(
                            (p) =>
                              `${p.display_name}${
                                p.unavailable_reason ? ` (${p.unavailable_reason})` : ''
                              }`,
                          )
                          .join(' · ')}
                        .
                      </p>
                    )}
                    {selectedPlugin && (
                      <div className="impact">
                        <strong>What it does</strong>
                        <p>{selectedPlugin.impact_summary}</p>
                      </div>
                    )}
                    <button
                      type="button"
                      className="btn primary"
                      disabled={busy || !plugins.find((p) => p.id === pluginId)?.available}
                      onClick={() => void runScan()}
                    >
                      Start check
                    </button>
                    <p className="small muted scan-hint">
                      Runs in the background. Use <strong>Jobs</strong> below to see progress and
                      Stop if needed.
                    </p>
                  </>
                )}
              </div>
            </div>
            {selectedProjectId && (
              <section className="jobs-window" aria-label="Scan jobs">
                <div className="jobs-window-head">
                  <h2>Jobs — what is running</h2>
                  <div className="jobs-window-actions">
                    {pollJobId !== null && (
                      <span className="jobs-live-pill" title="This screen refreshes about every half second">
                        Live
                      </span>
                    )}
                    {canStop && (
                      <button type="button" className="btn stop-btn" onClick={() => void stopScan()}>
                        Stop
                      </button>
                    )}
                  </div>
                </div>
                <p className="small muted jobs-window-sub">
                  {pollJobId !== null
                    ? `Live updates for job #${pollJobId}. When it says Done, scroll to “What we found”.`
                    : 'Click a job on the left to see its log. Finished jobs show results below.'}
                </p>
                <div className="jobs-window-body">
                  <ul className="jobs-window-list">
                    {jobs.map((j) => (
                      <li key={j.id}>
                        <button
                          type="button"
                          className={
                            j.id === selectedJobId ? 'jobs-win-link active' : 'jobs-win-link'
                          }
                          onClick={() => setSelectedJobId(j.id)}
                        >
                          <span className={`job-status-dot ${jobStatusClass(j.status)}`} aria-hidden />
                          Check #{j.id}
                          <span className="jobs-win-meta">{jobStatusPlain(j.status)}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                  <div className="jobs-log-pane">
                    <div className="jobs-log-toolbar">
                      <span className="small muted">
                        {logJob
                          ? `Check #${logJob.id} — ${jobStatusPlain(logJob.status)}`
                          : 'Pick a job'}
                      </span>
                      {selectedJob && selectedJob.status === 'completed' && (
                        <>
                          <button
                            type="button"
                            className="btn tiny ghost"
                            onClick={() =>
                              void api.downloadExport(selectedProjectId, selectedJob.id, 'json')
                            }
                          >
                            Download report (JSON)
                          </button>
                          <button
                            type="button"
                            className="btn tiny ghost"
                            onClick={() =>
                              void api.downloadExport(selectedProjectId, selectedJob.id, 'sarif')
                            }
                          >
                            Download (SARIF)
                          </button>
                        </>
                      )}
                    </div>
                    {logJob && (
                      <p className="jobs-log-intro small">{jobLogIntro(logJob)}</p>
                    )}
                    <pre ref={logPreRef} className="jobs-log-pre">
                      {logJob?.log_text?.trim() ? logJob.log_text : '—'}
                    </pre>
                    {logJob?.error_message && (
                      <p className="error-text jobs-log-error">
                        {friendlyJobError(logJob.error_message) ?? logJob.error_message}
                      </p>
                    )}
                    {logJob?.status === 'failed' &&
                      logJob.error_message &&
                      /nmap/i.test(logJob.error_message) && (
                        <div className="jobs-nmap-hint">
                          <p className="small">Quick fix: install Nmap, restart the backend, try again.</p>
                          <CopyBtn text="https://nmap.org/download.html">Copy Nmap download page link</CopyBtn>
                        </div>
                      )}
                  </div>
                </div>
              </section>
            )}
            {selectedProjectId && jobs.length >= 2 && (
              <section className="card">
                <h2>Compare two checks</h2>
                <p className="small muted">See what appeared or disappeared between two finished jobs.</p>
                <div className="rowform">
                  <select
                    value={diffOld}
                    onChange={(e) => setDiffOld(e.target.value ? Number(e.target.value) : '')}
                  >
                    <option value="">Older job</option>
                    {jobs.map((j) => (
                      <option key={j.id} value={j.id}>
                        #{j.id} {j.plugin_id} ({j.status})
                      </option>
                    ))}
                  </select>
                  <select
                    value={diffNew}
                    onChange={(e) => setDiffNew(e.target.value ? Number(e.target.value) : '')}
                  >
                    <option value="">Newer job</option>
                    {jobs.map((j) => (
                      <option key={`n-${j.id}`} value={j.id}>
                        #{j.id} {j.plugin_id} ({j.status})
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="btn"
                    disabled={!diffOld || !diffNew || diffOld === diffNew}
                    onClick={() => {
                      void (async () => {
                        try {
                          setDiff(
                            await api.diffJobs(selectedProjectId, Number(diffOld), Number(diffNew)),
                          )
                        } catch (e) {
                          setErr(e instanceof Error ? e.message : 'Compare failed')
                        }
                      })()
                    }}
                  >
                    Compare
                  </button>
                </div>
                {diff && <p className="plain-lead">{diff.summary}</p>}
              </section>
            )}
            {selectedProjectId && (
              <section className="card">
                <h2>Repeat this check</h2>
                <p className="small muted">
                  While this app is running it can start the selected check again every N hours.
                  Closing the app stops the timer.
                </p>
                <div className="rowform">
                  <input
                    type="number"
                    min={1}
                    max={720}
                    value={schedHours}
                    onChange={(e) => setSchedHours(Number(e.target.value) || 24)}
                  />
                  <button
                    type="button"
                    className="btn"
                    onClick={() => {
                      void (async () => {
                        try {
                          const row = await api.createSchedule({
                            project_id: selectedProjectId,
                            plugin_id: pluginId,
                            interval_hours: schedHours,
                          })
                          setSchedules((s) => [...s, row])
                        } catch (e) {
                          setErr(e instanceof Error ? e.message : 'Schedule failed')
                        }
                      })()
                    }}
                  >
                    Schedule selected check
                  </button>
                </div>
                <ul className="list">
                  {schedules
                    .filter((s) => s.project_id === selectedProjectId)
                    .map((s) => (
                      <li key={s.id}>
                        Every {s.interval_hours}h — {s.plugin_id}{' '}
                        <button
                          type="button"
                          className="btn tiny danger"
                          onClick={() => {
                            void (async () => {
                              await api.deleteSchedule(s.id)
                              setSchedules((all) => all.filter((x) => x.id !== s.id))
                            })()
                          }}
                        >
                          Remove
                        </button>
                      </li>
                    ))}
                </ul>
              </section>
            )}
          </>
        ) : (
          <p className="muted">Tick permission above to continue.</p>
        )}
      </section>

      {selectedProjectId && selectedJobId && (
        <section className="card findings-section">
          <h2>What we found</h2>
          {findings.length === 0 ? (
            <p className="muted plain-lead">
              Nothing listed yet. If the job is still running, wait for <strong>Done</strong> in Jobs.
            </p>
          ) : (
            <>
              <p className="findings-summary plain-lead">
                <strong>{findings.length}</strong> item{findings.length === 1 ? '' : 's'}.
                {findingsNeedAttention > 0 ? (
                  <>
                    {' '}
                    <strong>{findingsNeedAttention}</strong> may need a fix or a second look.
                  </>
                ) : (
                  ' Nothing here looks urgent from this scan.'
                )}
              </p>
              <div className="findings-cards">
                {findings.map((f) => {
                  const L = laymanForFinding(f)
                  const fixes = autoFixSnippets(f)
                  return (
                    <article key={f.finding_id} className="finding-card">
                      <header className="finding-card-head">
                        <span className={`sev-pill sev-${f.severity}`}>{severityPlain(f.severity)}</span>
                        <h3 className="finding-card-title">{L.headline}</h3>
                      </header>
                      <p className="finding-means">{L.means}</p>
                      <div className="finding-target">
                        <span className="muted small">Address: </span>
                        <code>{f.target}</code>
                      </div>
                      {L.doNext.length > 0 && (
                        <div className="finding-next">
                          <strong className="small">What to do</strong>
                          <ul>
                            {L.doNext.map((line, i) => (
                              <li key={i}>{line}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {fixes.length > 0 && (
                        <div className="finding-autofix">
                          <strong className="small">Auto-fix helpers (you paste and run)</strong>
                          {fixes.map((fx, i) => (
                            <div key={i} className="autofix-block">
                              <p className="autofix-label">{fx.label}</p>
                              <pre className="autofix-pre">{fx.script}</pre>
                              <div className="autofix-actions">
                                <CopyBtn text={fx.script}>Copy command</CopyBtn>
                              </div>
                              <p className="small muted autofix-note">{fx.note}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="finding-extra">
                        <button
                          type="button"
                          className="btn tiny ghost"
                          onClick={() => void openPlaybook(f.remediation_key)}
                        >
                          More detail (technical)
                        </button>
                      </div>
                    </article>
                  )
                })}
              </div>
            </>
          )}
        </section>
      )}

      {playbook && (
        <div className="modal" role="dialog" aria-modal="true">
          <div className="modal-inner">
            <header>
              <h3>Technical notes</h3>
              <button type="button" className="btn ghost" onClick={() => setPlaybook(null)}>
                Close
              </button>
            </header>
            <p className="small muted">Code: {playbook.key}</p>
            <div className="md">{playbook.md}</div>
          </div>
        </div>
      )}

      <footer className="footer muted small">
        One scan cannot prove a network is perfect. Keep devices updated and Wi‑Fi passwords strong.
      </footer>
    </div>
  )
}
