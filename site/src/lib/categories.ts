// Shared categories (spec §6.5). Colours are the ones people already link to each service, and
// match Stop 2 of the ride: TTC red, police navy, shelter brown, asphalt grey, park green.
export const CATEGORIES: Record<string, { label: string; color: string }> = {
	transit: { label: 'Transit', color: '#da251d' },
	'police-justice': { label: 'Police & justice', color: '#1f3a68' },
	'fire-paramedics': { label: 'Fire & paramedics', color: '#e8742a' },
	'housing-shelter': { label: 'Housing & shelter', color: '#8b5e3c' },
	'social-services': { label: 'Social services', color: '#3f8f86' },
	health: { label: 'Health', color: 'var(--c-health)' },
	education: { label: 'Education', color: 'var(--c-education)' },
	'parks-rec-culture': { label: 'Parks, rec & culture', color: '#4a8c3f' },
	infrastructure: { label: 'Roads, water & infrastructure', color: '#6b7078' },
	'government-debt': { label: 'Government & debt', color: '#a39e93' },
	other: { label: 'Other', color: 'var(--c-other)' }
};

// The Ontario Budget reports trends by its own "sectors", which don't match the shared
// categories one-to-one. They keep their own labels, and borrow the closest colour.
const SECTORS: Record<string, { label: string; color: string }> = {
	postsecondary: { label: 'Colleges & universities', color: 'var(--c-education)' },
	'children-social-services': { label: 'Children & social services', color: '#3f8f86' },
	justice: { label: 'Justice (police, courts, jails)', color: '#1f3a68' },
	'other-programs': { label: 'All other programs', color: 'var(--c-other)' },
	interest: { label: 'Interest on the debt', color: '#a39e93' }
};

const lookup = (c?: string) => CATEGORIES[c ?? 'other'] ?? SECTORS[c ?? ''];
export const categoryColor = (c?: string) => lookup(c)?.color ?? 'var(--c-other)';
export const categoryLabel = (c?: string) => lookup(c)?.label ?? c ?? 'Other';
/** Series that are spending categories (not totals, revenue or one-off lines) and belong in trend charts. */
export const isTrendCategory = (c: string) => c in CATEGORIES || c in SECTORS;
