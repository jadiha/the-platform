import { loadBudget, loadTrends, loadWards } from '#lib/server/data.ts';

export const load = () => ({
	toronto: loadBudget('toronto', '2026'),
	ontario: loadBudget('ontario', '2026-27'),
	scarborough: loadBudget('scarborough', '2026'),
	wards: loadWards(),
	trends: loadTrends()
});
