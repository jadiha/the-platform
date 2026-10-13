<script lang="ts">
	import { geoMercator, geoPath } from 'd3-geo';
	import { scaleSequential } from 'd3-scale';
	import { interpolateRgb } from 'd3-interpolate';
	import type { FeatureCollection, Geometry } from 'geojson';
	import wardsGeo from '#lib/geo/wards.json';
	import { STOPS, VIEWS } from './stops';
	import type { Wards } from '#lib/types.ts';

	let { step, wards }: { step: number; wards: Wards | null } = $props();

	const W = 600, H = 520;
	// GeoJSON (RFC 7946, as written by mapshaper) winds outer rings counter-clockwise; d3-geo
	// expects clockwise and would otherwise draw "the whole globe minus the ward". Rewind once.
	type Ring = [number, number][];
	const signedArea = (r: Ring) => r.reduce((a, [x, y], i) => { const [nx, ny] = r[(i + 1) % r.length]; return a + (x * ny - nx * y); }, 0);
	const rewind = (rings: Ring[]) => rings.map((r, i) => ((i === 0) === signedArea(r) > 0 ? [...r].reverse() : r));
	function rewound(fc: FeatureCollection<Geometry, { ward: number; name: string }>) {
		return {
			...fc,
			features: fc.features.map((f) => {
				const g = f.geometry;
				if (g.type === 'Polygon') return { ...f, geometry: { ...g, coordinates: rewind(g.coordinates as Ring[]) } };
				if (g.type === 'MultiPolygon') return { ...f, geometry: { ...g, coordinates: g.coordinates.map((p) => rewind(p as Ring[])) } };
				return f;
			})
		};
	}
	const geo = rewound(wardsGeo as unknown as FeatureCollection<Geometry, { ward: number; name: string }>);
	const projection = geoMercator().fitExtent([[10, 10], [W - 10, H - 10]], geo);
	const path = geoPath(projection);
	const SCARB = new Set([20, 21, 22, 23, 24, 25]);

	const scarbBounds = path.bounds({
		type: 'FeatureCollection',
		features: geo.features.filter((f) => SCARB.has(f.properties.ward))
	});
	const pad = 24;
	const frames = {
		city: `0 0 ${W} ${H}`,
		scarborough: `${scarbBounds[0][0] - pad} ${scarbBounds[0][1] - pad} ${scarbBounds[1][0] - scarbBounds[0][0] + pad * 2} ${scarbBounds[1][1] - scarbBounds[0][1] + pad * 2}`
	};

	const pts = STOPS.map((s) => projection(s.lonlat) as [number, number]);
	const view = $derived(VIEWS[Math.min(step, VIEWS.length - 1)] ?? VIEWS[0]);
	const zoom = $derived(view.frame === 'scarborough' ? (scarbBounds[1][0] - scarbBounds[0][0] + pad * 2) / W : 1);

	// Smooth curve through the stops.
	const routeD = pts.reduce((d, [x, y], i) => {
		if (i === 0) return `M${x},${y}`;
		const [px, py] = pts[i - 1];
		const mx = (px + x) / 2;
		return `${d} C${mx},${py} ${mx},${y} ${x},${y}`;
	}, '');
	let routeEl: SVGPathElement | undefined = $state();
	let routeLen = $state(0);
	$effect(() => { if (routeEl) routeLen = routeEl.getTotalLength(); });
	// Approximate share of the route drawn so far: cumulative segment lengths.
	const segLens = pts.map((p, i) => (i === 0 ? 0 : Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])));
	const cum = segLens.map((_, i) => segLens.slice(0, i + 1).reduce((a, b) => a + b, 0));
	const drawn = $derived(cum[view.upTo] / cum[cum.length - 1]);

	const perResident = $derived(new Map((wards?.wards ?? []).map((w) => [w.ward, w.perResident10yr])));
	const maxPR = $derived(Math.max(1, ...perResident.values()));
	const shadeScale = $derived(scaleSequential(interpolateRgb('#f3f0e9', '#4a8c5c')).domain([0, maxPR]));

	function fill(ward: number) {
		if (view.shade === 'perResident' && perResident.has(ward)) return shadeScale(perResident.get(ward)!);
		return SCARB.has(ward) ? '#ece8df' : '#f7f5f0';
	}
</script>

<svg viewBox={frames[view.frame]} role="img" aria-label="Map of Toronto wards with the walk through Scarborough" style="--z:{zoom}">
	<g class="wards">
		{#each geo.features as f (f.properties.ward)}
			<path d={path(f)} fill={fill(f.properties.ward)} class:scarb={SCARB.has(f.properties.ward)}>
				<title>Ward {f.properties.ward}: {f.properties.name}</title>
			</path>
		{/each}
	</g>

	<path d={routeD} class="route-ghost" />
	<path
		bind:this={routeEl}
		d={routeD}
		class="route"
		style="stroke-dasharray:{routeLen};stroke-dashoffset:{routeLen * (1 - drawn)}"
	/>

	{#each STOPS as s, i}
		{@const [x, y] = pts[i]}
		<g class="stop" class:on={i === view.upTo} class:past={i < view.upTo} transform="translate({x},{y})">
			<circle r={(i === view.upTo ? 9 : 6) * zoom} />
			{#if i <= view.upTo}
				<text x={12 * zoom} y={4 * zoom} style="font-size:{13 * zoom}px">{s.label}{s.exact ? '' : '*'}</text>
			{/if}
		</g>
	{/each}

	{#if view.frame === 'scarborough'}
		<text class="area-label" x={scarbBounds[1][0] - 6} y={scarbBounds[1][1] - 6} text-anchor="end" style="font-size:{11 * zoom}px">SCARBOROUGH</text>
	{:else}
		<text class="area-label" x={W - 16} y={H - 10} text-anchor="end" style="font-size:11px">CITY OF TORONTO</text>
	{/if}
</svg>

<style>
	svg { width: 100%; height: 100%; display: block; transition: all 1.1s cubic-bezier(0.3, 0.7, 0.2, 1); overflow: hidden; }
	.wards path { stroke: #fff; stroke-width: calc(1px * var(--z)); transition: fill 0.8s; }
	.wards path.scarb { stroke: #d6d1c6; }
	.route-ghost { fill: none; stroke: var(--ink); stroke-opacity: 0.25; stroke-width: calc(1.2px * var(--z)); stroke-dasharray: calc(3px * var(--z)) calc(4px * var(--z)); }
	.route { fill: none; stroke: var(--ink); stroke-width: calc(2.4px * var(--z)); transition: stroke-dashoffset 1.1s cubic-bezier(0.3, 0.7, 0.2, 1); }
	.stop circle { fill: var(--paper); stroke: var(--ink); stroke-width: calc(1.5px * var(--z)); transition: r 0.4s, fill 0.4s; }
	.stop.past circle { fill: var(--ink); }
	.stop.on circle { fill: var(--c-education); }
	.stop text { font-family: var(--sans); fill: var(--mute); paint-order: stroke; stroke: var(--paper); stroke-width: calc(3px * var(--z)); }
	.stop.on text { fill: var(--ink); font-weight: 600; }
	.area-label { font-family: var(--sans); fill: var(--mute); letter-spacing: 2px; }
</style>
