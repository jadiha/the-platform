<script lang="ts">
	// A red-and-white Toronto streetcar, drawn simply. `sign` shows on the orange LED destination sign.
	let { sign = '', width = 300 }: { sign?: string; width?: number } = $props();
</script>

<svg viewBox="0 0 300 70" {width} aria-hidden="true" class="car">
	<!-- body -->
	<path d="M4 20 Q6 10 18 9 L292 9 Q297 9 297 14 L297 58 L4 58 Z" fill="#da251d" />
	<!-- white band -->
	<rect x="4" y="28" width="293" height="16" fill="#fff" />
	<!-- windows -->
	<g fill="#1d2329">
		<path d="M9 30 Q10 16 22 15 L40 15 L40 41 L9 41 Z" />
		{#each [48, 76, 104, 140, 168, 196, 232, 260] as x (x)}<rect {x} y="15" width="22" height="26" rx="2" />{/each}
	</g>
	<!-- articulation joints -->
	<g fill="#3a3f45">{#each [130, 222] as x (x)}<rect {x} y="11" width="6" height="47" />{/each}</g>
	<!-- destination sign -->
	<rect x="44" y="2" width="120" height="10" rx="2" fill="#111" />
	<text x="104" y="9.6" text-anchor="middle" class="led">{sign}</text>
	<!-- wheels -->
	<g fill="#222">{#each [30, 110, 190, 270] as x (x)}<circle cx={x} cy="60" r="5" />{/each}</g>
	<!-- headlight -->
	<circle cx="9" cy="50" r="2.5" fill="#ffe08a" />
</svg>

<style>
	.car { display: block; height: auto; overflow: visible; }
	.led { font: 700 6.5px ui-monospace, 'SF Mono', Menlo, monospace; fill: #ff9a1f; letter-spacing: 0.3px; }
</style>
