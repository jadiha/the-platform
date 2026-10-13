import { loadBudget } from '#lib/server/data.ts';

export const load = () => ({
	trees: [
		{ key: 'toronto', label: 'Toronto', tree: loadBudget('toronto', '2026') },
		{ key: 'ontario', label: 'Ontario', tree: loadBudget('ontario', '2026-27') }
	].filter((t) => t.tree)
});
