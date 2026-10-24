import type { Finding, Intent } from "../types";

/** Intent Lock: warn when a suggested edit could change what the writer meant. */
export function intentWarnings(f: Finding, intent: Intent): string[] {
  if (!f.fix) return [];
  const w: string[] = [];
  const q = f.quote.toLowerCase(), fix = f.fix.toLowerCase(), cta = intent.cta.trim().toLowerCase();
  if (cta && q.includes(cta) && !fix.includes(cta)) w.push("Removes the call to action");
  intent.claims.split(",").map((c) => c.trim().toLowerCase()).filter(Boolean).forEach((c) => {
    if (q.includes(c)) w.push(`Touches key claim “${c}”`);
  });
  const a = f.quote.match(/\d+(\.\d+)?/g) ?? [], b = f.fix.match(/\d+(\.\d+)?/g) ?? [];
  if (a.length && a.join() !== b.join()) w.push(`Changes the promise: ${f.quote} → ${f.fix}`);
  return w;
}

/** Hard guard: never let an accepted edit delete the call to action. */
export function removesCta(text: string, edited: string, intent: Intent): boolean {
  const cta = intent.cta.trim();
  return !!cta && text.includes(cta) && !edited.includes(cta);
}
