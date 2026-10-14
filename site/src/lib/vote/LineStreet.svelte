<script lang="ts">
	// The journey bar: one slim line with a streetcar (under its overhead wire) that moves as you scroll, and the current
	// stop's name. Big stops are places; candidates are small ticks. Colour belongs to the route,
	// never to a candidate.
	import type { Snippet } from 'svelte';
	import Streetcar from './Streetcar.svelte';
	let { stops, active, onjump, children }: { stops: { label: string; big: boolean }[]; active: number; onjump: (i: number) => void; children?: Snippet } = $props();
	const at = $derived(Math.max(active, 0));
	// Places get more room on the route than the candidate stops between them.
	const pos = $derived.by(() => {
		const c: number[] = stops.map((_, i) => (i === 0 ? 0 : stops[i].big || stops[i - 1].big ? 5 : 1));
		const cum = c.map((_, i) => c.slice(0, i + 1).reduce((a, b) => a + b, 0));
		const total = cum.at(-1) || 1;
		return cum.map((x) => (x / total) * 100);
	});
	const pct = (i: number) => pos[i] ?? 0;
	// While the car is travelling it rocks a little; when it arrives, the pantograph sparks on the wire.
	let last = $state(0);
	let moving = $state(false);
	$effect(() => {
		if (at === last) return;
		last = at; moving = true;
		const t = setTimeout(() => (moving = false), 800);
		return () => clearTimeout(t);
	});
</script>

<nav class="ride sans" aria-label="Where you are on the journey">
	<div class="inner">
		<!-- Just the stop number here; the page heading below says what the stop is. -->
		<span class="here visually-hidden" aria-live="polite">{stops[at]?.label.split(':')[0]}</span>
		<div class="track">
			<div class="done" style="width:{pct(at)}%"></div>
			{#each stops as s, i (i)}
				<button class="st" class:big={s.big} class:passed={i <= at} style="left:{pct(i)}%" aria-label="Go to {s.label}" onclick={() => onjump(i)}></button>
			{/each}
			<div class="wire" aria-hidden="true"></div>
			<div class="tram" class:moving style="left:clamp(calc(var(--tw) / 2), {pct(at)}%, calc(100% - var(--tw) / 2))">
				<Streetcar width={100} />
				{#key at}<span class="spark" aria-hidden="true"></span>{/key}
			</div>
		</div>
		{#if children}<div class="acts">{@render children()}</div>{/if}
	</div>
</nav>

<style>
	.ride { position: sticky; top: var(--mast, 61px); z-index: 6; background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--rule); padding: 40px 20px 12px; overflow-x: clip; }
	.inner { max-width: 1080px; margin: 0 auto; display: flex; align-items: center; gap: 32px; }
	.acts { flex: none; display: flex; gap: 8px; }
	.here { flex: none; width: 76px; font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--ink-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.track { position: relative; flex: 1; margin-right: 12px; height: 4px; background: #d9d4c9; border-radius: 4px; }
	.done { position: absolute; inset: 0 auto 0 0; background: #da251d; border-radius: 4px; transition: width 0.8s cubic-bezier(0.45, 0, 0.2, 1); }
	.st { position: absolute; top: 50%; width: 2px; height: 8px; margin: -4px 0 0 -1px; background: #c9c4b9; border: 0; padding: 0; cursor: pointer; }
	.st.passed { background: #fff; }
	.st.big { width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; background: var(--paper); border: 2px solid #9a958b; }
	.st.big.passed { border-color: #da251d; }
	.st::after { content: ''; position: absolute; inset: -10px -4px; }
	/* The overhead wire the streetcar's pantograph touches; it sits exactly at the top of the drawing. */
	.track { --tw: 88px; }
	.wire { position: absolute; left: -20px; right: -20px; bottom: calc(var(--tw) * 0.35); height: 1px; background: color-mix(in srgb, var(--ink) 45%, transparent); pointer-events: none; }
	.tram { position: absolute; bottom: 1px; width: var(--tw); margin-left: calc(var(--tw) / -2); transition: left 0.8s cubic-bezier(0.45, 0, 0.2, 1); pointer-events: none; }
	.tram :global(svg) { width: 100%; transform-origin: 50% 100%; }
	.tram.moving :global(svg) { animation: rock 0.4s ease-in-out 2; }
	@keyframes rock { 25% { transform: rotate(-1.2deg); } 75% { transform: rotate(0.8deg); } }
	/* Spark at the contact point (x 88/200 of the drawing), once the car has pulled in. */
	.spark { position: absolute; top: -3px; left: 44%; width: 7px; height: 7px; margin-left: -3.5px; border-radius: 50%; background: #ffd23f; box-shadow: 0 0 6px 3px rgb(255 200 40 / 0.8); opacity: 0; animation: spark 0.5s ease-out 0.75s; }
	@keyframes spark { 0% { opacity: 1; transform: scale(0.4); } 30% { opacity: 1; transform: scale(1.3); } 100% { opacity: 0; transform: scale(0.6); } }
	@media (max-width: 640px) {
		.ride { --mast: 0px; padding: 32px 14px 10px; }
		.track { --tw: 68px; }
		.inner { gap: 10px 16px; flex-wrap: wrap; }
		.track { order: 3; flex-basis: 100%; margin: 6px 0 0; }
		.acts { margin-left: auto; }
		.here { width: auto; }
	}
	@media (prefers-reduced-motion: reduce) { .done, .tram { transition: none; } .tram.moving :global(svg), .spark { animation: none; } }
</style>
