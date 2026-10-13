<script lang="ts">
	// A TTC subway train (Toronto Rocket style), drawn simply: brushed-silver body, black window
	// band, red door accents. Faces left; flip it with CSS to run the other way.
	let { width = 300, cars = 1 }: { width?: number; cars?: number } = $props();
	const W = 300;
</script>

<svg viewBox="0 0 {W * cars} 70" {width} aria-hidden="true" class="train">
	{#each Array.from({ length: cars }, (_, i) => i) as i (i)}
		<g transform="translate({i * W} 0)">
			{#if i === 0}
				<path d="M2 58 L2 30 Q4 10 30 8 L298 8 L298 58 Z" fill="#d9dde1" stroke="#9aa3ab" stroke-width="1.5" />
				<path d="M6 30 Q8 16 30 14 L44 14 L44 34 L6 34 Z" fill="#1b1f24" />
				<circle cx="10" cy="46" r="3" fill="#ffe08a" />
			{:else}
				<rect x="2" y="8" width="296" height="50" fill="#d9dde1" stroke="#9aa3ab" stroke-width="1.5" />
			{/if}
			<rect x={i === 0 ? 50 : 8} y="14" width={i === 0 ? 242 : 284} height="18" rx="3" fill="#1b1f24" />
			<rect x="2" y="44" width="296" height="5" fill="#da251d" />
			<g fill="#c3c9cf" stroke="#da251d" stroke-width="1.5">{#each [80, 170, 260] as x (x)}<rect {x} y="12" width="24" height="44" rx="2" />{/each}</g>
			<g stroke="#1b1f24" stroke-width="1">{#each [92, 182, 272] as x (x)}<line x1={x} y1="14" x2={x} y2="54" />{/each}</g>
			<g fill="#2a2e33">{#each [40, 120, 200, 270] as x (x)}<rect {x} y="58" width="22" height="6" rx="2" />{/each}</g>
		</g>
	{/each}
</svg>

<style>
	.train { display: block; height: auto; overflow: visible; }
</style>
