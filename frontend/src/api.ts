/** Shown in the UI; real server URL (not the dev proxy path). */
export const apiDisplayUrl =
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

/** Request base: dev uses Vite proxy unless VITE_API_URL is set. */
const base =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000')

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })
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
}

export const api = {
  /** Base used for fetch() (e.g. `/api` in dev behind Vite proxy). */
  baseUrl: base,
  /** Human-readable backend URL for labels and help text. */
  displayUrl: apiDisplayUrl,
  health: () => req<{ status: string }>('/health'),
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
  getPlaybook: (key: string) =>
    req<{ remediation_key: string; markdown: string }>(`/playbooks/${encodeURIComponent(key)}`),
  exportJsonUrl: (projectId: number, jobId: number) =>
    `${base}/projects/${projectId}/jobs/${jobId}/export.json`,
  exportSarifUrl: (projectId: number, jobId: number) =>
    `${base}/projects/${projectId}/jobs/${jobId}/export.sarif`,
}
