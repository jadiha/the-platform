<script lang="ts">
	// The journey bar: one slim line with a streetcar that moves as you scroll, and the current
	// stop's name. Big stops are places; candidates are small ticks. Colour belongs to the route,
	// never to a candidate.
	import SubwayTrain from './SubwayTrain.svelte';
	let { stops, active, onjump }: { stops: { label: string; big: boolean }[]; active: number; onjump: (i: number) => void } = $props();
	const at = $derived(Math.max(active, 0));
	// Places get more room on the route than the candidate stops between them.
	const pos = $derived.by(() => {
		const c: number[] = stops.map((_, i) => (i === 0 ? 0 : stops[i].big || stops[i - 1].big ? 5 : 1));
		const cum = c.map((_, i) => c.slice(0, i + 1).reduce((a, b) => a + b, 0));
		const total = cum.at(-1) || 1;
		return cum.map((x) => (x / total) * 100);
	});
	const pct = (i: number) => pos[i] ?? 0;
	let last = $state(0);
	let dir = $state(1);
	$effect(() => { if (at !== last) { dir = at > last ? 1 : -1; last = at; } });
</script>

<nav class="ride sans" aria-label="Where you are on the journey">
	<div class="inner">
		<span class="here" aria-live="polite">{stops[at]?.label}</span>
		<div class="track">
			<div class="done" style="width:{pct(at)}%"></div>
			{#each stops as s, i (i)}
				<button class="st" class:big={s.big} class:passed={i <= at} style="left:{pct(i)}%" aria-label="Go to {s.label}" onclick={() => onjump(i)}></button>
			{/each}
			<div class="tram" class:back={dir < 0} style="left:{pct(at)}%"><SubwayTrain width={54} /></div>
		</div>
	</div>
</nav>

<style>
	.ride { position: sticky; top: var(--mast, 61px); z-index: 6; background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--rule); padding: 14px 20px 10px; overflow-x: clip; }
	.inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; gap: 18px; }
	.here { flex: none; width: 220px; font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.track { position: relative; flex: 1; height: 4px; background: #d9d4c9; border-radius: 4px; }
	.done { position: absolute; inset: 0 auto 0 0; background: #da251d; border-radius: 4px; transition: width 0.8s cubic-bezier(0.45, 0, 0.2, 1); }
	.st { position: absolute; top: 50%; width: 2px; height: 8px; margin: -4px 0 0 -1px; background: #c9c4b9; border: 0; padding: 0; cursor: pointer; }
	.st.passed { background: #fff; }
	.st.big { width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; background: var(--paper); border: 2px solid #9a958b; }
	.st.big.passed { border-color: #da251d; }
	.st::after { content: ''; position: absolute; inset: -10px -4px; }
	.tram { position: absolute; bottom: 3px; width: 54px; margin-left: -27px; transition: left 0.8s cubic-bezier(0.45, 0, 0.2, 1); pointer-events: none; }
	/* The train is drawn facing left; face it the way it's travelling. */
	.tram :global(svg) { transform: scaleX(-1); }
	.tram.back :global(svg) { transform: none; }
	@media (max-width: 640px) {
		.ride { --mast: 0px; padding: 12px 14px 8px; }
		.here { width: 110px; font-size: 12px; }
	}
	@media (prefers-reduced-motion: reduce) { .done, .tram { transition: none; } }
</style>
