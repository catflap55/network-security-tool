/** Shown in the UI; real server URL (not the dev proxy path). */
export const apiDisplayUrl =
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

const TOKEN_KEY = 'security-console-token'

export function getConsoleToken(): string {
  return sessionStorage.getItem(TOKEN_KEY) ?? ''
}

export function setConsoleToken(token: string): void {
  const t = token.trim()
  if (t) sessionStorage.setItem(TOKEN_KEY, t)
  else sessionStorage.removeItem(TOKEN_KEY)
}

const base =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000')

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getConsoleToken()
  const r = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-Console-Token': token } : {}),
      ...(init?.headers ?? {}),
    },
  })
  if (r.status === 401) {
    const err = new Error('TOKEN_REQUIRED')
    throw err
  }
  if (!r.ok) {
    const text = await r.text()
    throw new Error(text || r.statusText)
  }
  if (r.status === 204) return undefined as T
  return r.json() as Promise<T>
}

export type PluginInfo = {
  id: string
  display_name: string
  description: string
  requires_lab_mode: boolean
  impact_summary: string
  available: boolean
  unavailable_reason: string | null
}

export type Project = {
  id: number
  name: string
  targets: string
  environment: string
  created_at: string
}

export type Job = {
  id: number
  project_id: number
  plugin_id: string
  status: string
  started_at: string | null
  finished_at: string | null
  log_text: string
  error_message: string | null
  artifact_dir: string | null
}

export type Finding = {
  finding_id: string
  severity: string
  title: string
  description: string
  remediation_key: string
  plugin_id: string
  target: string
  evidence: Record<string, unknown>
  first_seen: string | null
}

export type Settings = {
  authorization_acknowledged: boolean
  lab_mode_enabled: boolean
  bind_host: string
  token_required: boolean
}

export type JobDiff = {
  old_job_id: number
  new_job_id: number
  added: { title: string; target: string; severity: string }[]
  removed: { title: string; target: string; severity: string }[]
  unchanged_count: number
  summary: string
}

export type Schedule = {
  id: number
  project_id: number
  plugin_id: string
  interval_hours: number
  enabled: boolean
  last_run_at: string | null
}

export const api = {
  baseUrl: base,
  displayUrl: apiDisplayUrl,
  health: () => fetch(`${base}/health`).then((r) => r.json() as Promise<{ status: string }>),
  getSettings: () => req<Settings>('/settings'),
  putSettings: (body: { authorization_acknowledged: boolean }) =>
    req<Settings>('/settings', { method: 'PUT', body: JSON.stringify(body) }),
  listPlugins: () => req<PluginInfo[]>('/plugins'),
  listProjects: () => req<Project[]>('/projects'),
  createProject: (body: { name: string; targets: string; environment: string }) =>
    req<Project>('/projects', { method: 'POST', body: JSON.stringify(body) }),
  deleteProject: (id: number) =>
    req<void>(`/projects/${id}`, { method: 'DELETE' }),
  startJob: (projectId: number, plugin_id: string) =>
    req<Job>(`/projects/${projectId}/jobs`, {
      method: 'POST',
      body: JSON.stringify({ plugin_id }),
    }),
  cancelJob: (projectId: number, jobId: number) =>
    req<Job>(`/projects/${projectId}/jobs/${jobId}/cancel`, { method: 'POST' }),
  listJobs: (projectId: number) => req<Job[]>(`/projects/${projectId}/jobs`),
  getJob: (projectId: number, jobId: number) =>
    req<Job>(`/projects/${projectId}/jobs/${jobId}`),
  listFindings: (projectId: number, jobId: number) =>
    req<Finding[]>(`/projects/${projectId}/jobs/${jobId}/findings`),
  diffJobs: (projectId: number, oldId: number, newId: number) =>
    req<JobDiff>(`/projects/${projectId}/jobs/${oldId}/diff/${newId}`),
  listSchedules: () => req<Schedule[]>('/schedules'),
  createSchedule: (body: { project_id: number; plugin_id: string; interval_hours: number }) =>
    req<Schedule>('/schedules', { method: 'POST', body: JSON.stringify(body) }),
  deleteSchedule: (id: number) => req<void>(`/schedules/${id}`, { method: 'DELETE' }),
  getPlaybook: (key: string) =>
    req<{ remediation_key: string; markdown: string }>(`/playbooks/${encodeURIComponent(key)}`),
  async downloadExport(projectId: number, jobId: number, kind: 'json' | 'sarif') {
    const path =
      kind === 'json'
        ? `/projects/${projectId}/jobs/${jobId}/export.json`
        : `/projects/${projectId}/jobs/${jobId}/export.sarif`
    const token = getConsoleToken()
    const r = await fetch(`${base}${path}`, {
      headers: token ? { 'X-Console-Token': token } : {},
    })
    if (!r.ok) throw new Error(await r.text())
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = kind === 'json' ? `job-${jobId}.json` : `job-${jobId}.sarif.json`
    a.click()
    URL.revokeObjectURL(url)
  },
}
