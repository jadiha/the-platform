import { loadBudget } from '#lib/server/data.ts';

export const load = () => ({
	trees: [
		{ key: 'ontario', label: 'Ontario', tree: loadBudget('ontario', '2026-27') },
		{ key: 'toronto', label: 'Toronto', tree: loadBudget('toronto', '2026') },
		{ key: 'scarborough', label: 'Scarborough', tree: loadBudget('scarborough', '2026') }
	].filter((t) => t.tree)
});
