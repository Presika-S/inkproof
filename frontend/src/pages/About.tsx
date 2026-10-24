export default function About() {
  return (
    <div className="card">
      <h2>How a finding is checked</h2>
      <p>Exact checks and claim matching propose findings. An independent verifier then confirms four things: the rule is approved, the quote is in the draft, the fact is current, and the fact applies to the claim. If any check fails, or no approved fact covers the claim, the finding goes to human review and is never shown as a confirmed violation. “No approved source” does not mean a claim is false.</p>
      <h2>Privacy</h2>
      <p>Drafts are stored in the server database and visible only to their author and reviewers. Sign-in uses hashed passwords and expiring tokens. The AI step runs on the server, so no API key reaches your browser. It sends the draft plus rule and fact text to the AI provider only when you choose “Run with AI review”. Use synthetic data in demos. You can delete any of your drafts from the Review page.</p>
    </div>
  );
}
