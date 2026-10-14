<script lang="ts">
	// The journey bar: the streetcar rides along one black line (the header's edge) and moves as you go, and the current
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
	// While the car is travelling it rocks a little; when it pulls in, the stop sparks under its wheels.
	let last = $state(0);
	let moving = $state(false);
	$effect(() => {
		if (at === last) return;
		last = at; moving = true;
		const t = setTimeout(() => (moving = false), 800);
		return () => clearTimeout(t);
	});

	// Stick right under the masthead whatever its height (it wraps to two rows on narrow laptops).
	// On phones the masthead scrolls away, so the bar sticks to the very top instead.
	$effect(() => {
		const mast = document.querySelector<HTMLElement>('.masthead');
		if (!mast) return;
		const fit = () => ride.style.setProperty('--mast', getComputedStyle(mast).position === 'sticky' ? `${mast.offsetHeight - 1}px` : '0px');
		const ro = new ResizeObserver(fit);
		ro.observe(mast);
		return () => ro.disconnect();
	});

	// Hopping on, as one continuous motion: the header's black line drops and tightens into the track
	// while the stops pop in left to right and the streetcar rolls in from off-screen, sparking as it
	// arrives. Only transforms animate (smooth on slow phones), and it starts once the new stop has
	// painted, so it never runs through the page swap.
	let ride: HTMLElement;
	let track: HTMLDivElement;
	let tram: HTMLDivElement;
	let intro = $state<'pre' | 'run' | 'done'>('pre');
	$effect(() => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) { intro = 'done'; return; }
		const rr = ride.getBoundingClientRect(), tr = track.getBoundingClientRect(), cr = tram.getBoundingClientRect();
		const sx = tr.width / rr.width, l = tr.left - rr.left;
		ride.style.setProperty('--ty', `${tr.top - rr.top}px`);
		ride.style.setProperty('--sx', `${sx}`);
		// Scaling about this point maps the full-width line exactly onto the track.
		ride.style.setProperty('--ox', `${l / (1 - sx || 1)}px`);
		ride.style.setProperty('--tx', `${-cr.right - 12}px`);
		let raf = requestAnimationFrame(() => (raf = requestAnimationFrame(() => (intro = 'run'))));
		const t = setTimeout(() => (intro = 'done'), 2400);
		return () => { cancelAnimationFrame(raf); clearTimeout(t); };
	});
</script>

<nav class="ride sans" class:pre={intro === 'pre'} class:run={intro === 'run'} bind:this={ride} aria-label="Where you are on the journey">
	<div class="inner">
		<!-- Just the stop number here; the page heading below says what the stop is. -->
		<span class="here visually-hidden" aria-live="polite">{stops[at]?.label.split(':')[0]}</span>
		<div class="track" bind:this={track}>
			{#each stops as s, i (i)}
				<button class="st" class:big={s.big} class:passed={i <= at} style="left:{pct(i)}%; --i:{i}" aria-label="Go to {s.label}" onclick={() => onjump(i)}></button>
			{/each}
			{#key at}<span class="spark" style="left:{pct(at)}%" aria-hidden="true"></span>{/key}
			<div class="tram" class:moving bind:this={tram} style="left:clamp(calc(var(--tw) / 2), {pct(at)}%, calc(100% - var(--tw) / 2))">
				<Streetcar width={100} />
			</div>
		</div>
		{#if children}<div class="acts">{@render children()}</div>{/if}
	</div>
</nav>

<style>
	/* One line only: the masthead drops its own bottom edge, and the track is the black line under it. */
	:global(body:has(nav.ride) .masthead) { border-bottom-color: transparent; padding-bottom: 6px; }
	.ride { position: sticky; top: var(--mast, 54px); z-index: 6; background: var(--paper); padding: 24px 20px 10px; overflow-x: clip; }
	.inner { max-width: 1080px; margin: 0 auto; display: flex; align-items: center; gap: 32px; }
	.acts { flex: none; display: flex; gap: 8px; }
	.here { flex: none; width: 76px; font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--ink-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.track { position: relative; flex: 1; margin-right: 12px; height: 2px; background: var(--ink); }
	.st { position: absolute; top: 50%; width: 2px; height: 8px; margin: -4px 0 0 -1px; background: #c9c4b9; border: 0; padding: 0; cursor: pointer; }
	.st.passed { background: #fff; }
	.st.big { width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; background: var(--paper); border: 2px solid var(--ink); }
	.st.big.passed { background: #da251d; }
	.st::after { content: ''; position: absolute; inset: -10px -4px; }
	.track { --tw: 88px; }
	.tram { position: absolute; bottom: 1px; width: var(--tw); margin-left: calc(var(--tw) / -2); transition: left 0.8s cubic-bezier(0.45, 0, 0.2, 1); pointer-events: none; }
	.tram :global(svg) { width: 100%; transform-origin: 50% 100%; }
	.tram.moving :global(svg) { animation: rock 0.4s ease-in-out 2; }
	/* Spark on the stop's dot, on the line under the wheels, once the car has pulled in. */
	.spark { position: absolute; top: 50%; z-index: 1; width: 9px; height: 9px; margin: -4.5px 0 0 -4.5px; pointer-events: none; border-radius: 50%; background: #ffd23f; box-shadow: 0 0 6px 3px rgb(255 200 40 / 0.8); opacity: 0; animation: spark 0.5s ease-out 0.75s; }
	@keyframes spark { 0% { opacity: 1; transform: scale(0.4); } 30% { opacity: 1; transform: scale(1.3); } 100% { opacity: 0; transform: scale(0.6); } }
	@keyframes rock { 25% { transform: rotate(-1.2deg); } 75% { transform: rotate(0.8deg); } }
	/* Hop-on intro. The header's edge becomes a full-width line that drops and tightens onto the track in one move. */
	.ride::before { content: ''; position: absolute; left: 0; right: 0; top: var(--ty, 0); height: 2px; margin-top: 0; background: var(--ink); opacity: 0; pointer-events: none; transform-origin: var(--ox, 50%) 50%; }
	.ride.pre::before { opacity: 1; transform: translateY(calc(-1 * var(--ty, 0px))); }
	.ride.run::before { animation: line-in 0.48s cubic-bezier(0.3, 0.75, 0.35, 1) forwards; }
	@keyframes line-in {
		from { opacity: 1; transform: translateY(calc(-1 * var(--ty, 0px))) scaleX(1); }
		99% { opacity: 1; transform: translateY(0) scaleX(var(--sx, 1)); }
		to { opacity: 0; transform: translateY(0) scaleX(var(--sx, 1)); }
	}
	/* The real track takes over the moment the line lands. */
	.ride.pre .track { background: transparent; }
	.ride.run .track { animation: track-in 0.48s steps(1, end) backwards; }
	@keyframes track-in { from { background: transparent; } }
	/* Stops pop in left to right, starting before the line has settled. */
	.ride.pre .st, .ride.pre .tram, .ride.pre .spark { visibility: hidden; }
	.ride.run .st { animation: pop 0.34s cubic-bezier(0.3, 1.6, 0.5, 1) backwards; animation-delay: calc(0.12s + var(--i) * 0.055s); }
	@keyframes pop { from { transform: scale(0); } }
	/* The streetcar rolls in from off-screen and eases into its stop; the spark waits for it. */
	.ride.run .tram { animation: roll-in 0.95s cubic-bezier(0.2, 0.7, 0.25, 1) 0.3s backwards; }
	@keyframes roll-in { from { transform: translateX(var(--tx, -200px)); } }
	.ride.run .tram :global(svg) { animation: rock 0.4s ease-in-out 0.85s 2; }
	.ride.run .spark { animation-delay: 1.1s; }
	@media (max-width: 640px) {
		.ride { padding: 19px 14px 12px; }
		.track { --tw: 68px; }
		.inner { gap: 10px 16px; flex-wrap: wrap; }
		.track { order: 3; flex-basis: 100%; margin: 6px 0 0; }
		.acts { margin-left: auto; }
		.here { width: auto; }
	}
	@media (prefers-reduced-motion: reduce) { .tram { transition: none; } .tram.moving :global(svg), .spark, .ride::before, .st, .tram, .track { animation: none !important; } }
</style>
