export const USE_DISCLAIMER =
  'This tool is for information only. It is not legal, credit, tax, or financial advice. You must do your own independent checks at the official source before you act. The authors are not liable for decisions you make from these results.'

export function LegalBanner() {
  return (
    <p className="legal-banner" role="note">
      {USE_DISCLAIMER}
    </p>
  )
}

export function DisclaimerFooter({ extra }: { extra?: string }) {
  return (
    <footer className="footer legal-foot">
      {USE_DISCLAIMER}
      {extra ? ` ${extra}` : ''}
    </footer>
  )
}
