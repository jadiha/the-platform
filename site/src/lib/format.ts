import type { Fact } from '#lib/types.ts';

const int = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 0 });
const one = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 1 });

/** $ millions → "$18.9 billion" / "$786 million" (long) or "$18.9B" / "$786M" (short). */
export function money(millions: number, style: 'long' | 'short' = 'long'): string {
	const sign = millions < 0 ? '−' : '';
	const m = Math.abs(millions);
	if (m >= 1000) return `${sign}$${one.format(m / 1000)}${style === 'short' ? 'B' : ' billion'}`;
	if (m >= 1) return `${sign}$${int.format(m)}${style === 'short' ? 'M' : ' million'}`;
	return `${sign}$${int.format(m * 1e6)}`;
}

export function formatFact(fact: Fact, style: 'long' | 'short' = 'long'): string {
	const v = fact.value;
	if (typeof v !== 'number') return String(v);
	switch (fact.unit) {
		case '$M':
			return money(v, style);
		case '$':
			return `$${v >= 100 ? int.format(v) : v.toFixed(2)}`;
		case '%':
			return `${one.format(v)}%`;
		case 'people':
		case 'count':
			return int.format(v);
		default:
			return one.format(v);
	}
}

export function formatDate(iso: string): string {
	const d = new Date(iso + 'T12:00:00');
	return isNaN(+d) ? iso : d.toLocaleDateString('en-CA', { year: 'numeric', month: 'short', day: 'numeric' });
}

export const STATUS_LABEL = {
	verified: '✓ Verified',
	single: '◌ Single source',
	disagree: '⚠ Sources disagree',
	reported: 'Reported, not official'
} as const;

export const STATUS_HELP = {
	verified: 'Official source, and an independent source agrees.',
	single: 'From an official source; no independent check found yet.',
	disagree: 'Official sources give different numbers. Both are shown below.',
	reported: 'Reported by media, but not confirmed in an official document.'
} as const;
