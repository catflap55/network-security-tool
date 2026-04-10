import { useState, type ReactNode } from 'react'

export function CopyBtn({ text, children }: { text: string; children: ReactNode }) {
  const [done, setDone] = useState(false)
  return (
    <button
      type="button"
      className="btn tiny autofix-copy"
      onClick={() => {
        void navigator.clipboard.writeText(text).then(() => {
          setDone(true)
          window.setTimeout(() => setDone(false), 1600)
        })
      }}
    >
      {done ? 'Copied!' : children}
    </button>
  )
}
