<script lang="ts">
	// Small multiples: one mini line chart per category, each on its own y-scale so the
	// direction of change is readable even for small categories. Plans are drawn dashed.
	import { scaleLinear, scalePoint } from 'd3-scale';
	import { line } from 'd3-shape';
	import { categoryColor, categoryLabel, isTrendCategory } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { Trends, TrendPoint } from '#lib/types.ts';

	let { trends }: { trends: Trends } = $props();

	const LEVELS = [
		['ontario', 'Ontario'],
		['toronto', 'Toronto']
	] as const;
	const available = $derived(LEVELS.filter(([k]) => trends[k] && Object.keys(trends[k]).length));
	let level = $state<'ontario' | 'toronto'>('ontario');
	const series = $derived(
		Object.entries((trends[level] ?? {}) as Record<string, TrendPoint[]>)
			.filter(([cat, pts]) => isTrendCategory(cat) && Array.isArray(pts) && pts.length > 1)
			.map(([cat, pts]) => {
				const first = pts[0].value, last = pts[pts.length - 1].value;
				return { cat, pts, change: ((last - first) / first) * 100, last };
			})
			.sort((a, b) => b.last - a.last)
	);

	const W = 220, H = 70, M = { t: 8, r: 6, b: 16, l: 6 };
	function geom(pts: TrendPoint[]) {
		const x = scalePoint<string>().domain(pts.map((p) => p.year)).range([M.l, W - M.r]);
		const vals = pts.map((p) => p.value);
		const lo = Math.min(...vals), hi = Math.max(...vals);
		const y = scaleLinear().domain([lo - (hi - lo) * 0.15 || lo * 0.9, hi + (hi - lo) * 0.15 || hi * 1.1]).range([H - M.b, M.t]);
		const ln = line<TrendPoint>().x((p) => x(p.year)!).y((p) => y(p.value));
		const firstPlan = pts.findIndex((p) => p.kind !== 'actual');
		const solid = firstPlan === -1 ? pts : pts.slice(0, Math.max(firstPlan, 1));
		const dashed = firstPlan === -1 ? [] : pts.slice(Math.max(firstPlan - 1, 0));
		return { x, y, solid: ln(solid), dashed: dashed.length > 1 ? ln(dashed) : null };
	}
</script>

{#if available.length}
	<div class="tabs sans" role="tablist">
		{#each available as [k, label]}
			<button role="tab" aria-selected={level === k} onclick={() => (level = k)}>{label}</button>
		{/each}
	</div>
	<p class="legend sans">Solid line = actual spending. Dashed = budget plan. Each chart has its own scale, so compare the direction of change, not the heights.</p>
	<div class="grid">
		{#each series as s (s.cat)}
			{@const g = geom(s.pts)}
			<figure>
				<figcaption class="sans">
					<span class="name">{categoryLabel(s.cat)}</span>
					<span class="chg" class:up={s.change > 0} class:down={s.change < 0}>
						{s.change > 0 ? '▲' : '▼'} {Math.abs(s.change).toFixed(0)}%
					</span>
				</figcaption>
				<svg viewBox="0 0 {W} {H}" role="img" aria-label="{categoryLabel(s.cat)}: {s.pts[0].year} {money(s.pts[0].value)} to {s.pts.at(-1)?.year} {money(s.last)}">
					<path d={g.solid} stroke={categoryColor(s.cat)} />
					{#if g.dashed}<path d={g.dashed} stroke={categoryColor(s.cat)} stroke-dasharray="3 3" />{/if}
					{#each s.pts as p}
						<circle cx={g.x(p.year)} cy={g.y(p.value)} r="2.5" fill={p.kind === 'actual' ? categoryColor(s.cat) : 'var(--paper)'} stroke={categoryColor(s.cat)}>
							<title>{p.year} ({p.kind}): {money(p.value)}</title>
						</circle>
					{/each}
					<text x={M.l} y={H - 3}>{s.pts[0].year}</text>
					<text x={W - M.r} y={H - 3} text-anchor="end">{s.pts.at(-1)?.year}</text>
				</svg>
				<p class="val sans">{money(s.pts[0].value, 'short')} → <strong>{money(s.last, 'short')}</strong></p>
			</figure>
		{/each}
	</div>
	<p class="caveat sans">
		Amounts are not adjusted for inflation or population growth. Governments re-label and restate past years, so we compare like with like where the official documents allow.
		Details are on the <a href="/sources/">sources page</a>.
	</p>
{:else}
	<p class="sans pending">Trend data is being prepared.</p>
{/if}

<style>
	.tabs { display: flex; gap: 0; border-bottom: 1px solid var(--ink); margin: 10px 0 8px; }
	.tabs button { font: inherit; font-size: 14px; font-weight: 600; background: none; border: 0; padding: 8px 14px; cursor: pointer; color: var(--mute); border-bottom: 3px solid transparent; margin-bottom: -1px; }
	.tabs button[aria-selected='true'] { color: var(--ink); border-bottom-color: var(--ink); }
	.legend, .caveat { font-size: 12px; color: var(--mute); }
	.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 18px 22px; margin: 14px 0; }
	figure { margin: 0; }
	figcaption { display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; }
	.chg { font-variant-numeric: tabular-nums; }
	.up { color: var(--ok); }
	.down { color: #b02a37; }
	svg { width: 100%; height: auto; display: block; }
	path { fill: none; stroke-width: 2; }
	text { font-family: var(--sans); font-size: 9px; fill: var(--mute); }
	.val { font-size: 12px; margin: 0; color: var(--ink-2); }
	.pending { color: var(--mute); }
</style>
