import type { Finding, Job } from './api'

/** Short steps shown at the top for first-time users. */
export const QUICK_START_STEPS = [
  'Turn on the backend (black window) and this page — both must run.',
  'Tick the box below if you are allowed to scan your own network.',
  'Add a project: give it a name and type IPs to check (e.g. 192.168.1.0/24 or 127.0.0.1).',
  'Click your project, pick a scan type, then Run scan. Watch Jobs for progress.',
  'When it finishes, read “What we found” — we explain each item simply.',
] as const

export function severityPlain(sev: string): string {
  if (sev === 'critical' || sev === 'high') return 'Important'
  if (sev === 'medium') return 'Worth fixing'
  if (sev === 'low') return 'Small issue'
  return 'FYI'
}

export function jobStatusPlain(status: string): string {
  switch (status) {
    case 'pending':
      return 'Queued'
    case 'running':
      return 'Running'
    case 'completed':
      return 'Done'
    case 'failed':
      return 'Failed'
    case 'cancelled':
      return 'Stopped'
    default:
      return status
  }
}

export function friendlyJobError(message: string | null): string | null {
  if (!message) return null
  if (/Executable not found|nmap/i.test(message) && /nmap/i.test(message)) {
    return 'Nmap was not found. Install Nmap for Windows, or set NMAP_PATH in backend/.env to your nmap.exe, then restart the backend.'
  }
  if (/timed out/i.test(message)) {
    return 'The scan took too long and was stopped. Try fewer targets or a quicker scan type.'
  }
  if (/LAB_MODE/i.test(message)) {
    return 'This scan type needs LAB_MODE turned on for the backend (advanced). Pick another scan or ask whoever set up the app.'
  }
  return message
}

export type LaymanFinding = {
  headline: string
  means: string
  doNext: string[]
  needsFix: boolean
}

export function laymanForFinding(f: Finding): LaymanFinding {
  const port =
    typeof f.evidence.port === 'number' || typeof f.evidence.port === 'string'
      ? String(f.evidence.port)
      : null
  const proto = typeof f.evidence.protocol === 'string' ? f.evidence.protocol : 'tcp'

  switch (f.remediation_key) {
    case 'OPEN_TCP_PORT':
    case 'OPEN_UDP_PORT':
      return {
        headline: port ? `Port ${port} (${proto}) is open` : 'An open port was found',
        means: `Something on ${f.target} is accepting network connections on this port. That can be fine (e.g. a web server) or a risk if you did not expect it.`,
        doNext: [
          'Figure out what device or app this is (router, PC, camera, etc.).',
          'If you do not use this service, turn it off or block it on the firewall.',
          'If you do use it, keep it updated and use a strong password.',
        ],
        needsFix: f.severity !== 'info',
      }
    case 'SERVICE_DETECTED':
      return {
        headline: port ? `Service spotted on port ${port}` : 'Software was detected',
        means: `We could tell what kind of program is listening on ${f.target}. Old or misconfigured software is a common way people get in.`,
        doNext: [
          'Check for updates for that program or device.',
          'Turn off the service if you do not need it.',
          'Use your router or PC firewall to limit who can reach it.',
        ],
        needsFix: true,
      }
    case 'HOST_UP':
      return {
        headline: 'Device responded',
        means: `This address (${f.target}) is on and answered the scan. That is normal — it is not a problem by itself.`,
        doNext: ['Use this to build a mental list of what is on your network.'],
        needsFix: false,
      }
    case 'SCAN_ERROR':
      return {
        headline: 'Scan did not finish cleanly',
        means: 'The scan tool hit a problem (missing program, bad target, or network block).',
        doNext: [
          'Install or fix Nmap, then run again.',
          'Check that the IP range is correct.',
          'Temporarily allow the scan in antivirus/firewall if it blocks Nmap.',
        ],
        needsFix: true,
      }
    case 'COVERAGE_GAP':
      return {
        headline: 'No open ports found in this pass',
        means: 'Either nothing common was open, or the scan did not cover everything. It does not prove the device is “100% safe.”',
        doNext: [
          'If you expected services to show up, try another scan type or targets.',
          'For deeper checks, use updated devices and strong Wi‑Fi passwords.',
        ],
        needsFix: false,
      }
    case 'UNSUPPORTED_PLUGIN':
      return {
        headline: 'This scan type is not ready',
        means: 'The app cannot run that plugin yet, or a setting is missing.',
        doNext: ['Pick a different scan from the list, or check locked plugins for setup notes.'],
        needsFix: false,
      }
    default:
      return {
        headline: f.title,
        means: f.description || 'See technical title above.',
        doNext: ['Use “More detail” if you want step-by-step text.'],
        needsFix: f.severity === 'medium' || f.severity === 'high' || f.severity === 'critical',
      }
  }
}

export type AutoFixSnippet = {
  label: string
  script: string
  note: string
}

export function autoFixSnippets(f: Finding): AutoFixSnippet[] {
  const out: AutoFixSnippet[] = []
  const port =
    typeof f.evidence.port === 'number' || typeof f.evidence.port === 'string'
      ? String(f.evidence.port)
      : null
  if (
    !port ||
    (f.remediation_key !== 'OPEN_TCP_PORT' && f.remediation_key !== 'SERVICE_DETECTED')
  ) {
    return out
  }

  out.push({
    label: 'Windows: block inbound on this port (copy, then run PowerShell as Admin)',
    script:
      `# Review before running — blocks inbound TCP ${port} on this PC only\n` +
      `New-NetFirewallRule -DisplayName "Block-in-${port}" -Direction Inbound -Action Block -Protocol TCP -LocalPort ${port}`,
    note: 'Only helps on the PC where you run it. Test that you still reach what you need.',
  })
  out.push({
    label: 'Linux (ufw): deny this port — copy, then run on that machine',
    script: `sudo ufw deny ${port}/tcp\nsudo ufw reload`,
    note: 'Run on the Linux box that owns the port. May lock you out if you need that port.',
  })
  return out
}

export function jobLogIntro(job: Job): string {
  if (job.status === 'running' || job.status === 'pending') {
    return 'Technical log (for support). Plain-English status is in the list on the left.'
  }
  if (job.status === 'completed') {
    return 'Scan finished. Scroll down to “What we found” for simple explanations.'
  }
  if (job.status === 'failed') {
    return 'The scan did not complete. Read the red line under the log if there is one.'
  }
  if (job.status === 'cancelled') {
    return 'You stopped this scan. Run again if you want a full result.'
  }
  return ''
}
