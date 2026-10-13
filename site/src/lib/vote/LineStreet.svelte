<script lang="ts">
	// The street you walk: a Line 2 strip pinned to the top. Big stops are stations; candidates are
	// the small ticks between them. Colour flows along the line as you go (never per candidate).
	let { stops, active, onjump }: { stops: { label: string; big: boolean }[]; active: number; onjump: (i: number) => void } = $props();
	const pct = (i: number) => (stops.length > 1 ? (i / (stops.length - 1)) * 100 : 0);
	const cur = $derived(stops[Math.max(active, 0)]);
</script>

<nav class="street sans" aria-label="Where you are on the walk">
	<div class="label">
		<span class="line2">LINE 2</span>
		<span class="here" aria-live="polite">{cur?.label}</span>
		<span class="step">{Math.max(active, 0) + 1} / {stops.length}</span>
	</div>
	<div class="track">
		<div class="fill" style="width:{pct(Math.max(active, 0))}%"></div>
		{#each stops as s, i (i)}
			<button
				class="dot"
				class:big={s.big}
				class:passed={i <= active}
				class:now={i === active}
				style="left:{pct(i)}%"
				aria-label="Go to {s.label}"
				onclick={() => onjump(i)}
			></button>
		{/each}
	</div>
</nav>

<style>
	.street { overflow-x: clip; position: sticky; top: var(--mast, 61px); z-index: 6; background: var(--paper); border-bottom: 1px solid var(--rule); padding: 8px 20px 12px; }
	.label { display: flex; gap: 10px; align-items: baseline; max-width: 1100px; margin: 0 auto 8px; font-size: 13px; }
	.line2 { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; background: #2e7d32; color: #fff; padding: 2px 6px; border-radius: 4px; }
	.here { font-weight: 600; flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
	.step { color: var(--mute); font-size: 12px; font-variant-numeric: tabular-nums; }
	.track { position: relative; height: 6px; background: #e6e2d9; border-radius: 6px; max-width: 1100px; margin: 0 auto; }
	.fill { position: absolute; inset: 0 auto 0 0; border-radius: 6px; background: linear-gradient(90deg, #2f5d9b, #d9822b 55%, #4a8c5c); background-size: 1100px 100%; transition: width 0.6s cubic-bezier(0.2, 0.8, 0.2, 1); }
	.dot { position: absolute; top: 50%; width: 6px; height: 6px; margin: -3px 0 0 -3px; border-radius: 50%; background: #cfcabf; border: 0; padding: 0; cursor: pointer; }
	.dot.big { width: 14px; height: 14px; margin: -7px 0 0 -7px; background: #fff; border: 2px solid #9a958b; }
	.dot.passed { background: var(--ink); }
	.dot.big.passed { background: var(--ink); border-color: var(--ink); }
	.dot.now { box-shadow: 0 0 0 4px rgba(18, 18, 18, 0.15); transform: scale(1.3); }
	.dot::after { content: ''; position: absolute; inset: -10px; } /* bigger tap target */
	@media (max-width: 640px) { .street { --mast: 0px; padding: 6px 14px 10px; } }
	@media (prefers-reduced-motion: reduce) { .fill { transition: none; } }
</style>
