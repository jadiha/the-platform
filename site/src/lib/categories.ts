// Shared categories (spec §6.5). Colours come from CSS tokens in app.css.
export const CATEGORIES: Record<string, { label: string; color: string }> = {
	transit: { label: 'Transit', color: 'var(--c-transit)' },
	'police-justice': { label: 'Police & justice', color: 'var(--c-police)' },
	'fire-paramedics': { label: 'Fire & paramedics', color: 'var(--c-other)' },
	'housing-shelter': { label: 'Housing & shelter', color: 'var(--c-housing)' },
	'social-services': { label: 'Social services', color: '#8fb39a' },
	health: { label: 'Health', color: 'var(--c-health)' },
	education: { label: 'Education', color: 'var(--c-education)' },
	'parks-rec-culture': { label: 'Parks, rec & culture', color: '#9cb86a' },
	infrastructure: { label: 'Roads, water & infrastructure', color: '#8a9bb5' },
	'government-debt': { label: 'Government & debt', color: '#a39e93' },
	other: { label: 'Other', color: 'var(--c-other)' }
};

// The Ontario Budget reports trends by its own "sectors", which don't match the shared
// categories one-to-one. They keep their own labels, and borrow the closest colour.
const SECTORS: Record<string, { label: string; color: string }> = {
	postsecondary: { label: 'Colleges & universities', color: 'var(--c-education)' },
	'children-social-services': { label: 'Children & social services', color: '#8fb39a' },
	justice: { label: 'Justice (police, courts, jails)', color: 'var(--c-police)' },
	'other-programs': { label: 'All other programs', color: 'var(--c-other)' },
	interest: { label: 'Interest on the debt', color: '#a39e93' }
};

const lookup = (c?: string) => CATEGORIES[c ?? 'other'] ?? SECTORS[c ?? ''];
export const categoryColor = (c?: string) => lookup(c)?.color ?? 'var(--c-other)';
export const categoryLabel = (c?: string) => lookup(c)?.label ?? c ?? 'Other';
/** Series that are spending categories (not totals, revenue or one-off lines) and belong in trend charts. */
export const isTrendCategory = (c: string) => c in CATEGORIES || c in SECTORS;
