<script lang="ts">
	// All 25 Toronto wards, smoothed. Hover or tap a ward to see its name and a link to who's
	// running there. Wards are all drawn the same way; nothing about a ward's candidates is coloured.
	import { geoMercator } from 'd3-geo';
	import type { FeatureCollection, Geometry, Position } from 'geojson';
	import wardsGeo from '#lib/geo/wards.json';

	let { listUrl, guided = [] }: { listUrl: string; guided?: number[] } = $props();

	const W = 640, H = 420;
	const fc = wardsGeo as unknown as FeatureCollection<Geometry, { ward: number; name: string }>;
	const outerRings = (g: Geometry): Position[][] =>
		g.type === 'Polygon' ? [g.coordinates[0]] : g.type === 'MultiPolygon' ? g.coordinates.map((p) => p[0]) : [];
	const pts = fc.features.flatMap((f) => outerRings(f.geometry).flat());
	const projection = geoMercator().fitExtent([[10, 10], [W - 10, H - 10]], { type: 'MultiPoint', coordinates: pts });
	const proj = (p: Position) => projection(p as [number, number]) as [number, number];

	function simplify(P: [number, number][], eps: number): [number, number][] {
		if (P.length < 3) return P;
		const [a, b] = [P[0], P[P.length - 1]];
		let dmax = 0, idx = 0;
		for (let i = 1; i < P.length - 1; i++) {
			const d = Math.abs((b[1] - a[1]) * P[i][0] - (b[0] - a[0]) * P[i][1] + b[0] * a[1] - b[1] * a[0]) / (Math.hypot(b[0] - a[0], b[1] - a[1]) || 1);
			if (d > dmax) { dmax = d; idx = i; }
		}
		return dmax > eps ? [...simplify(P.slice(0, idx + 1), eps).slice(0, -1), ...simplify(P.slice(idx), eps)] : [a, b];
	}
	function chaikin(P: [number, number][]): [number, number][] {
		return P.flatMap((a, i) => {
			const b = P[(i + 1) % P.length];
			return [[0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]], [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]] as [number, number][];
		});
	}
	const shapes = fc.features
		.map((f) => {
			const rings = outerRings(f.geometry).map((r) => r.map(proj)).filter((r) => r.length > 8);
			const d = rings
				.map((r) => {
					const h = Math.floor(r.length / 2);
					const s = chaikin([...simplify(r.slice(0, h + 1), 0.6).slice(0, -1), ...simplify([...r.slice(h), r[0]], 0.6).slice(0, -1)]);
					return 'M' + s.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join('L') + 'Z';
				})
				.join('');
			const all = rings.flat();
			const c = [all.reduce((s, p) => s + p[0], 0) / all.length, all.reduce((s, p) => s + p[1], 0) / all.length];
			return { ward: f.properties.ward, name: f.properties.name, d, c };
		})
		.sort((a, b) => a.ward - b.ward);

	let hover = $state<number | null>(null);
	let picked = $state<number | null>(null);
	const shown = $derived(shapes.find((s) => s.ward === (hover ?? picked)));
</script>

<div class="wardmap sans">
	<svg viewBox="0 0 {W} {H}" role="group" aria-label="Map of Toronto's 25 wards. Choose your ward.">
		{#each shapes as s (s.ward)}
			<path
				class="w"
				class:on={s.ward === (hover ?? picked)}
				d={s.d}
				role="button"
				tabindex="0"
				aria-label="Ward {s.ward} {s.name}"
				onmouseenter={() => (hover = s.ward)}
				onmouseleave={() => (hover = null)}
				onfocus={() => (hover = s.ward)}
				onblur={() => (hover = null)}
				onclick={() => (picked = s.ward)}
				onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), (picked = s.ward))}
			><title>Ward {s.ward} {s.name}</title></path>
		{/each}
		{#each shapes as s (s.ward)}<text x={s.c[0]} y={s.c[1] + 4} class:on={s.ward === (hover ?? picked)}>{s.ward}</text>{/each}
	</svg>
	<div class="panel" aria-live="polite">
		{#if shown}
			<span class="num">Ward {shown.ward}</span>
			<b>{shown.name}</b>
			<a class="go" href={listUrl} target="_blank" rel="noopener">See who's running ↗</a>
			{#if guided.includes(shown.ward)}<span class="soon">Our full guide for this ward is coming this week.</span>{/if}
		{:else}
			<span class="num">Your ward</span>
			<b>Tap your part of the city</b>
			<span class="hint">Then see who's running for councillor there.</span>
		{/if}
	</div>
</div>

<style>
	.wardmap { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(200px, 1fr); gap: 16px; align-items: center; }
	svg { width: 100%; height: auto; max-height: 46vh; }
	.w { fill: #ebe7df; stroke: var(--paper); stroke-width: 2.5; stroke-linejoin: round; cursor: pointer; transition: fill 0.2s; outline: none; }
	.w:hover, .w.on { fill: #da251d; }
	text { font-size: 11px; font-weight: 700; fill: #8a857b; text-anchor: middle; pointer-events: none; }
	text.on { fill: #fff; }
	.panel { display: flex; flex-direction: column; gap: 4px; background: #fff; border: 1px solid var(--rule); border-radius: 16px; padding: 16px; min-height: 140px; justify-content: center; }
	.num { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #da251d; }
	.panel b { font-family: var(--serif); font-size: 24px; line-height: 1.15; }
	.go { align-self: flex-start; margin-top: 8px; font-weight: 700; font-size: 14px; text-decoration: none; background: var(--ink); color: #fff; border-radius: 999px; padding: 9px 16px; }
	.soon, .hint { font-size: 12.5px; color: var(--mute); margin-top: 4px; }
	@media (max-width: 700px) { .wardmap { grid-template-columns: 1fr; } .panel { min-height: 0; } }
	@media (prefers-reduced-motion: reduce) { .w { transition: none; } }
</style>
