import { useState } from 'react'
import { setConsoleToken } from './api'

export function TokenGate({
  onReady,
  error,
}: {
  onReady: () => void
  error: string | null
}) {
  const [value, setValue] = useState('')
  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Unlock Security Console</h1>
          <p className="sub">
            This tool stays on your computer. Paste the console token, then click
            Continue. Find it in the text window that stayed open (look for
            CONSOLE_TOKEN), or open the file <code>CONSOLE-TOKEN.txt</code> in the
            unzipped folder (next to Mac / Windows / Linux).
          </p>
        </div>
      </header>
      {error && (
        <div className="banner error">
          <pre>{error}</pre>
        </div>
      )}
      <form
        className="card"
        onSubmit={(e) => {
          e.preventDefault()
          setConsoleToken(value)
          onReady()
        }}
      >
        <label className="block">
          Console token
          <input
            type="password"
            autoComplete="off"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            required
          />
        </label>
        <p className="small muted">Stored in this browser tab only (session storage), not on GitHub.</p>
        <button type="submit" className="btn primary">
          Continue
        </button>
      </form>
      <footer className="footer muted small">
        This tool is for information only. It is not legal, credit, tax, or financial advice. You must do your own independent checks at the official source before you act. The authors are not liable for decisions you make from these results.
      </footer>
    </div>
  )
}
