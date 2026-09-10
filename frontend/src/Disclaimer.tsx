export const USE_DISCLAIMER =
  'This tool is for information only. It is not legal, credit, tax, or financial advice. You must do your own independent checks at the official source before you act. The authors are not liable for decisions you make from these results.'

export const PERSONAL_USE =
  'PERSONAL USE ONLY. Strictly for a home network that you own. Do not scan work, school, public Wi-Fi, a neighbour, a client, or the public internet. Unauthorised scanning can be illegal.'

export function LegalBanner() {
  return (
    <div className="legal-stack">
      <p className="use-limit-banner" role="alert">
        {PERSONAL_USE}
      </p>
      <p className="legal-banner" role="note">
        {USE_DISCLAIMER} {PERSONAL_USE}
      </p>
    </div>
  )
}

export function DisclaimerFooter({ extra }: { extra?: string }) {
  return (
    <footer className="footer legal-foot">
      {PERSONAL_USE} {USE_DISCLAIMER}
      {extra ? ` ${extra}` : ''}
    </footer>
  )
}
