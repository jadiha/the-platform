<script lang="ts" module>
	export interface Stop { lonlat: [number, number]; label: string }
</script>

<script lang="ts">
	// Scarborough's six wards, smoothed, with the walk's route. The current room's colour washes
	// over the map; the reader's ward fills with a slowly drifting gradient of it.
	import { geoMercator } from 'd3-geo';
	import type { FeatureCollection, Geometry, Position } from 'geojson';
	import wardsGeo from '#lib/geo/wards.json';

	let { stops, active, ward = $bindable(), color }: { stops: Stop[]; active: number; ward: number | null; color: string } = $props();

	const W = 440, H = 400;
	const SCARB = [20, 21, 22, 23, 24, 25];
	const fc = wardsGeo as unknown as FeatureCollection<Geometry, { ward: number; name: string }>;
	const feats = fc.features.filter((f) => SCARB.includes(f.properties.ward));
	const outerRings = (g: Geometry): Position[][] =>
		g.type === 'Polygon' ? [g.coordinates[0]] : g.type === 'MultiPolygon' ? g.coordinates.map((p) => p[0]) : [];
	// Fit on the raw points (no winding issues: we never ask d3 for areas).
	const pts = feats.flatMap((f) => outerRings(f.geometry).flat());
	const projection = geoMercator().fitExtent([[16, 16], [W - 16, H - 16]], { type: 'MultiPoint', coordinates: pts });
	const proj = (p: Position) => projection(p as [number, number]) as [number, number];

	// Douglas–Peucker, then two rounds of Chaikin corner-cutting for soft edges.
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
	function chaikin(P: [number, number][], n = 2): [number, number][] {
		for (let k = 0; k < n; k++) {
			P = P.flatMap((a, i) => {
				const b = P[(i + 1) % P.length];
				return [[0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]], [0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]]] as [number, number][];
			});
		}
		return P;
	}
	const shapes = feats
		.map((f) => {
			const rings = outerRings(f.geometry).map((r) => r.map(proj)).filter((r) => r.length > 8);
			const d = rings
				.map((r) => {
					const h = Math.floor(r.length / 2);
					const s = chaikin([...simplify(r.slice(0, h + 1), 0.9).slice(0, -1), ...simplify([...r.slice(h), r[0]], 0.9).slice(0, -1)]);
					return 'M' + s.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join('L') + 'Z';
				})
				.join('');
			const all = rings.flat();
			const c = [all.reduce((s, p) => s + p[0], 0) / all.length, all.reduce((s, p) => s + p[1], 0) / all.length];
			return { ward: f.properties.ward, name: f.properties.name, d, c };
		})
		.sort((a, b) => a.ward - b.ward);

	const sp = $derived(stops.map((s) => proj(s.lonlat)));
	// Smooth route through the stops (Catmull-Rom to Bezier).
	const routeD = $derived.by(() => {
		const P = sp;
		if (!P.length) return '';
		let d = `M${P[0]}`;
		for (let i = 0; i < P.length - 1; i++) {
			const p0 = P[i - 1] ?? P[i], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2] ?? p2;
			d += ` C${p1[0] + (p2[0] - p0[0]) / 6},${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6},${p2[1] - (p3[1] - p1[1]) / 6} ${p2}`;
		}
		return d;
	});
	let doneEl: SVGPathElement | undefined = $state();
	let len = $state(0);
	let at = $state<number[]>([]);
	$effect(() => {
		if (!doneEl || !routeD) return;
		const L = doneEl.getTotalLength();
		len = L;
		// Distance along the route at each stop.
		at = sp.map((p, i) => {
			if (!i) return 0;
			let best = 0, bd = Infinity;
			for (let s = 0; s <= L; s += 2) {
				const q = doneEl!.getPointAtLength(s);
				const d = (q.x - p[0]) ** 2 + (q.y - p[1]) ** 2;
				if (d < bd) { bd = d; best = s; }
			}
			return best;
		});
	});
	// SMIL animations ignore CSS, so drop them ourselves when the reader asks for less motion.
	let still = $state(false);
	$effect(() => { still = matchMedia('(prefers-reduced-motion: reduce)').matches; });
	const offset = $derived(len - (active >= 0 ? (at[active] ?? 0) : 0));
</script>

<svg viewBox="0 0 {W} {H}" style="--room:{color}" role="group" aria-label="Map of Scarborough's six wards. Choose your ward.">
	<defs>
		<linearGradient id="flow" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2={W} y2="120" spreadMethod="reflect">
			<stop offset="0" style="stop-color:color-mix(in srgb,var(--room) 55%,#fff)" />
			<stop offset=".5" style="stop-color:var(--room)" />
			<stop offset="1" style="stop-color:color-mix(in srgb,var(--room) 55%,#fff)" />
			{#if !still}<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{W} 120" dur="6s" repeatCount="indefinite" />{/if}
		</linearGradient>
	</defs>
	{#each shapes as s (s.ward)}<path class="shadow" d={s.d} />{/each}
	{#each shapes as s (s.ward)}
		<path
			class="ward"
			class:mine={ward === s.ward}
			d={s.d}
			role="button"
			tabindex="0"
			aria-label="Ward {s.ward} {s.name}"
			aria-pressed={ward === s.ward}
			onclick={() => (ward = s.ward)}
			onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), (ward = s.ward))}
		><title>Ward {s.ward} {s.name}</title></path>
	{/each}
	{#each shapes as s (s.ward)}<text class="wl" class:mine={ward === s.ward} x={s.c[0]} y={s.c[1] + 18} text-anchor="middle">{s.ward}</text>{/each}
	<path class="route" id="vote-route" d={routeD} />
	<path class="done" bind:this={doneEl} d={routeD} style="stroke-dasharray:{len};stroke-dashoffset:{offset}" />
	{#if !still}<circle class="traveller" r="4"><animateMotion dur="7s" repeatCount="indefinite"><mpath href="#vote-route" /></animateMotion></circle>{/if}
	{#each sp as [x, y], i (i)}
		<g class="stop" class:on={i === active} class:seen={i < active}>
			<circle class="halo" cx={x} cy={y} r="10" />
			<circle cx={x} cy={y} r="7" />
			<text x={x + 12} y={y + 4}>{stops[i].label}</text>
		</g>
	{/each}
</svg>

<style>
	svg { width: 100%; height: auto; overflow: visible; font-family: var(--sans); }
	.ward { fill: color-mix(in srgb, var(--room) 9%, #fff); stroke: #fff; stroke-width: 3; stroke-linejoin: round; transition: fill 0.8s; cursor: pointer; outline: none; }
	.ward:hover, .ward:focus-visible { fill: color-mix(in srgb, var(--room) 24%, #fff); }
	.ward.mine { fill: url(#flow); }
	.shadow { fill: none; stroke: color-mix(in srgb, var(--room) 35%, #bbb); stroke-width: 6; stroke-linejoin: round; opacity: 0.25; filter: blur(4px); }
	.wl { font-size: 11px; font-weight: 600; fill: color-mix(in srgb, var(--room) 60%, #333); pointer-events: none; transition: fill 0.8s; }
	.wl.mine { fill: #fff; }
	.route { fill: none; stroke: #bdb8ad; stroke-width: 2; stroke-dasharray: 2 5; stroke-linecap: round; }
	.done { fill: none; stroke: var(--room); stroke-width: 3.5; stroke-linecap: round; transition: stroke-dashoffset 1s ease, stroke 0.8s; }
	.stop circle { fill: #fff; stroke: #9a958b; stroke-width: 1.5; transition: fill 0.5s, stroke 0.5s; }
	.stop.seen circle { fill: var(--ink); stroke: var(--ink); }
	.stop.on circle { fill: var(--room); stroke: #fff; stroke-width: 3; }
	.stop .halo { fill: none; stroke: var(--room); opacity: 0; }
	.stop.on .halo { animation: halo 1.8s ease-out infinite; }
	@keyframes halo { from { r: 10; opacity: 0.6; } to { r: 26; opacity: 0; } }
	.stop text { font-size: 11px; fill: var(--mute); paint-order: stroke; stroke: var(--paper); stroke-width: 4px; }
	.stop.on text { fill: var(--ink); font-weight: 600; }
	.traveller { fill: var(--room); transition: fill 0.8s; }
	@media (prefers-reduced-motion: reduce) {
		.traveller { display: none; }
		.done, .ward, .stop circle { transition: none; }
		.stop.on .halo { animation: none; }
	}
</style>
