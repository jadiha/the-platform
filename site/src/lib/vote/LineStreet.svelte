<script lang="ts">
	// The journey: a streetcar riding past the Toronto skyline, pinned to the top. It moves as you
	// scroll; a stop display shows NOW and NEXT. Big stops are places on the memory walk, candidates
	// are the small stops between them. Colour belongs to the route, never to a candidate.
	import Streetcar from './Streetcar.svelte';
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
	const now = $derived(stops[at]);
	const next = $derived(stops[at + 1]);
	let last = $state(0);
	let dir = $state(1);
	$effect(() => { if (at !== last) { dir = at > last ? 1 : -1; last = at; } });
</script>

<nav class="ride sans" aria-label="Where you are on the journey">
	<div class="screen" aria-live="polite">
		<span class="now"><small>NOW AT</small>{now?.label}</span>
		{#if next}<span class="next"><small>NEXT STOP</small>{next.label}</span>{:else}<span class="next"><small>LAST STOP</small>Before you vote</span>{/if}
		<span class="count">{at + 1}/{stops.length}</span>
	</div>
	<div class="street">
		<svg class="sky" viewBox="0 0 1100 44" preserveAspectRatio="none" aria-hidden="true">
			<g fill="#cfd8e1">
				<rect x="20" y="18" width="26" height="26" /><rect x="52" y="8" width="20" height="36" /><rect x="160" y="14" width="30" height="30" />
				<rect x="196" y="24" width="18" height="20" /><rect x="330" y="10" width="24" height="34" /><rect x="360" y="20" width="30" height="24" />
				<rect x="520" y="16" width="22" height="28" /><rect x="700" y="12" width="28" height="32" /><rect x="734" y="22" width="22" height="22" />
				<rect x="880" y="6" width="26" height="38" /><rect x="912" y="18" width="30" height="26" /><rect x="1040" y="14" width="24" height="30" />
			</g>
			<g fill="#b8c5d2"><path d="M600 44 L604 10 L606 10 L610 44 Z" /><ellipse cx="605" cy="12" rx="6" ry="3" /><rect x="604" y="0" width="2" height="10" /></g>
		</svg>
		<div class="track">
			<div class="done" style="width:{pct(at)}%"></div>
			{#each stops as s, i (i)}
				<button class="st" class:big={s.big} class:passed={i <= at} class:here={i === at} style="left:{pct(i)}%" aria-label="Go to {s.label}" onclick={() => onjump(i)}>
					{#if s.big}<span class="name">{s.label.split(':')[0]}</span>{/if}
				</button>
			{/each}
			<div class="tram" class:back={dir < 0} style="left:{pct(at)}%"><Streetcar width={78} /></div>
		</div>
	</div>
</nav>

<style>
	.ride { position: sticky; top: var(--mast, 61px); z-index: 6; background: var(--paper); border-bottom: 1px solid var(--rule); padding: 8px 20px 22px; overflow-x: clip; }
	.screen { display: flex; align-items: center; gap: 12px; max-width: 1100px; margin: 0 auto 4px; background: #111; color: #ff9a1f; border-radius: 10px; padding: 7px 12px; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 13px; }
	.now, .next { display: flex; flex-direction: column; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
	.now { flex: 1.2; color: #fff; font-weight: 700; }
	.next { flex: 1; }
	.now small, .next small { font-size: 9px; letter-spacing: 2px; color: #9a958b; font-weight: 400; }
	.count { color: #9a958b; font-size: 11px; }
	.street { max-width: 1100px; margin: 0 auto; position: relative; padding: 0 14px; }
	.sky { display: block; width: 100%; height: 30px; }
	.track { position: relative; height: 7px; background: #9aa0a6; border-radius: 2px; }
	.done { position: absolute; inset: 0 auto 0 0; background: #da251d; border-radius: 2px; transition: width 0.8s cubic-bezier(0.45, 0, 0.2, 1); }
	.st { position: absolute; top: 50%; width: 3px; height: 11px; margin: -5.5px 0 0 -1.5px; background: #d9d4c9; border: 0; padding: 0; cursor: pointer; }
	.st.passed { background: #fff; }
	.st.big { width: 15px; height: 15px; margin: -7.5px 0 0 -7.5px; border-radius: 50%; background: #fff; border: 3px solid #6b7177; }
	.st.big.passed { border-color: #da251d; }
	.st.here { box-shadow: 0 0 0 5px rgba(218, 37, 29, 0.2); }
	.st::after { content: ''; position: absolute; inset: -10px -4px; }
	.name { position: absolute; top: 16px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; white-space: nowrap; color: var(--mute); }
	.tram { position: absolute; bottom: 5px; width: 78px; margin-left: -39px; transition: left 0.8s cubic-bezier(0.45, 0, 0.2, 1); pointer-events: none; }
	.tram.back :global(svg) { transform: scaleX(-1); }
	@media (max-width: 640px) {
		.ride { --mast: 0px; padding: 6px 12px 18px; }
		.screen { font-size: 12px; }
		.next, .count, .name { display: none; }
		.tram { width: 60px; margin-left: -30px; }
	}
	@media (prefers-reduced-motion: reduce) { .done, .tram { transition: none; } }
</style>
