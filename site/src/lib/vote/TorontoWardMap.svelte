<script lang="ts">
	// All 25 Toronto wards, smoothed. Hover or tap a ward to see its name and a link to who's
	// running there. Wards are all drawn the same way; nothing about a ward's candidates is coloured.
	import { geoMercator } from 'd3-geo';
	import type { FeatureCollection, Geometry, Position } from 'geojson';
	import wardsGeo from '#lib/geo/wards.json';

	type Person = { name: string; website: string | null };
	type Race = { ward: number; councillor: Person[]; trustees: { board: string; kind: string; board_ward: string; candidates: Person[] }[] };
	let { listUrl, chartUrl, races, guided = [] }: { listUrl: string; chartUrl: string; races: Race[]; guided?: number[] } = $props();
	// School boards in the order the Clerk lists them. You vote on one: English public unless you've chosen another.
	const BOARDS = ['TDSB', 'TCDSB', 'Viamonde', 'MonAvenir'];
	let board = $state('TDSB');

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

	// Hover previews a ward with a mouse or keyboard only. On a phone a tap would "hover" first,
	// open the sheet over the finger and swallow the tap, so touch goes straight to picking.
	let hover = $state<number | null>(null);
	let picked = $state<number | null>(null);
	const shown = $derived(shapes.find((s) => s.ward === (hover ?? picked)));
	const race = $derived(races.find((r) => r.ward === shown?.ward));
	const trustee = $derived(race?.trustees.find((t) => t.board === board));
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
				onpointerenter={(e) => e.pointerType === 'mouse' && (hover = s.ward)}
				onpointerleave={(e) => e.pointerType === 'mouse' && (hover = null)}
				onfocus={(e) => e.currentTarget.matches(':focus-visible') && (hover = s.ward)}
				onblur={() => (hover = null)}
				onclick={() => (picked = s.ward)}
				onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), (picked = s.ward))}
			><title>Ward {s.ward} {s.name}</title></path>
		{/each}
		{#each shapes as s (s.ward)}<text x={s.c[0]} y={s.c[1] + 4} class:on={s.ward === (hover ?? picked)}>{s.ward}</text>{/each}
	</svg>
	<div class="panel" class:open={!!(shown && race)} aria-live="polite">
		{#if shown && race}
			<button class="close" aria-label="Back to the map" onclick={() => { picked = null; hover = null; }}><span class="x" aria-hidden="true">×</span><span class="back">← Back to the map</span></button>
			<span class="num">Ward {shown.ward}</span>
			<b>{shown.name}</b>
			<div class="race">
				<h3>City councillor <span>{race.councillor.length} running</span></h3>
				<ul class="names" class:many={race.councillor.length > 8}>{#each race.councillor as c (c.name)}<li>{#if c.website}<a href={c.website} target="_blank" rel="noopener">{c.name}</a>{:else}{c.name}{/if}</li>{/each}</ul>
			</div>
			<div class="race">
				<h3>School board trustee <span>you vote on one board</span></h3>
				<div class="boards" role="tablist" aria-label="School board">
					{#each BOARDS as b (b)}
						{@const t = race.trustees.find((x) => x.board === b)}
						<button role="tab" aria-selected={board === b} class:on={board === b} onclick={() => (board = b)}>{t?.kind ?? b}</button>
					{/each}
				</div>
				{#if trustee}
					<p class="bw">{trustee.board} Ward {trustee.board_ward} · {trustee.candidates.length === 1 ? 'only candidate, already elected by acclamation' : `${trustee.candidates.length} running`}</p>
					<ul class="names" class:many={trustee.candidates.length > 6}>{#each trustee.candidates as c (c.name)}<li>{#if c.website}<a href={c.website} target="_blank" rel="noopener">{c.name}</a>{:else}{c.name}{/if}</li>{/each}</ul>
				{/if}
			</div>
			<p class="fine">Ballot order. Names link to the website each candidate gave the City. <a href={listUrl} target="_blank" rel="noopener">Official list ↗</a> · <a href={chartUrl} target="_blank" rel="noopener">Which school ward ↗</a>{#if guided.includes(shown.ward)} · Our full guide for this ward is coming this week.{/if}</p>
		{:else}
			<span class="num">Your ward</span>
			<b>Tap your part of the city</b>
			<span class="hint">See everyone running for city councillor and school board trustee there.</span>
		{/if}
	</div>
</div>

<style>
	.wardmap { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, 1fr); gap: 48px; align-items: center; margin-top: 22px; }
	svg { width: 100%; height: auto; max-height: 46vh; }
	.w { fill: #ebe7df; stroke: var(--paper); stroke-width: 2.5; stroke-linejoin: round; cursor: pointer; transition: fill 0.2s; outline: none; }
	.w:hover, .w.on { fill: #da251d; }
	text { font-size: 11px; font-weight: 700; fill: #8a857b; text-anchor: middle; pointer-events: none; }
	text.on { fill: #fff; }
	.panel { display: flex; flex-direction: column; gap: 2px; background: #fff; border: var(--line); box-shadow: var(--pop); border-radius: 16px; padding: 16px; min-height: 140px; justify-content: center; }
	.panel.open { align-self: start; }
	.panel:not(.open) { padding: 24px; gap: 6px; }
	.num { font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #da251d; }
	.panel b { font-family: var(--display); font-weight: 700; letter-spacing: 0; font-size: 24px; line-height: 1.15; }
	.hint { font-size: 12.5px; color: var(--mute); margin-top: 4px; }
	.race { border-top: 1px solid var(--rule); margin-top: 8px; padding-top: 7px; }
	h3 { font-size: 13px; font-weight: 700; margin: 0 0 6px; display: flex; justify-content: space-between; gap: 8px; }
	h3 span, .bw { font-weight: 400; font-size: 12px; color: var(--mute); }
	.bw { margin: 6px 0 4px; }
	.names { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 14px; font-size: 13px; line-height: 1.5; }
	.names.many { columns: 3; font-size: 12.5px; line-height: 1.45; }
	.names li { break-inside: avoid; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.names a { color: inherit; text-decoration: underline; text-decoration-color: #c9c4b9; text-underline-offset: 2px; }
	.boards { display: flex; flex-wrap: wrap; gap: 4px; }
	.boards button { font: inherit; font-size: 11.5px; border: 1px solid var(--rule); background: var(--paper); border-radius: 999px; padding: 3px 9px; cursor: pointer; color: var(--ink-2); }
	.boards button.on { background: var(--ink); border-color: var(--ink); color: #fff; }
	.fine { font-size: 11px; color: var(--mute); margin: 10px 0 0; line-height: 1.45; }
	.fine a { color: inherit; }
	.close { display: none; }
	.close .back { display: inline; }
	.panel { position: relative; }
	@media (max-width: 700px) {
		.wardmap { gap: 16px; margin-top: 12px; }
		.names.many { columns: 2; font-size: 13px; }
		.wardmap { grid-template-columns: 1fr; }
		.panel { min-height: 0; }
		/* On phones the ward takes the map's place (no sheet from the bottom); 'Back to the map' brings it back. */
		.wardmap:has(.panel.open) svg { display: none; }
		.panel.open { animation: swap 0.25s ease-out; }
		.close { display: block; order: -1; align-self: flex-start; border: 0; background: none; padding: 0 0 8px; font: inherit; font-size: 14px; font-weight: 600; color: var(--ink-2); cursor: pointer; }
		.close .x { display: none; }
		@keyframes swap { from { opacity: 0; transform: translateY(6px); } }
	}
	@media (prefers-reduced-motion: reduce) { .w { transition: none; } }
</style>
