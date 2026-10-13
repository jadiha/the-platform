<script lang="ts">
	// The ride: a Line 2 track pinned to the top with a train that moves as you scroll, and a
	// "next train" style screen showing NOW and NEXT. Big stops are stations; candidates are ticks.
	// Colour belongs to the line, never to a candidate.
	let { stops, active, onjump }: { stops: { label: string; big: boolean }[]; active: number; onjump: (i: number) => void } = $props();
	const at = $derived(Math.max(active, 0));
	// Stations get more room on the track than the candidate ticks between them.
	const pos = $derived.by(() => {
		const c: number[] = stops.map((_, i) => (i === 0 ? 0 : stops[i].big || stops[i - 1].big ? 5 : 1));
		const cum = c.map((_, i) => c.slice(0, i + 1).reduce((a, b) => a + b, 0));
		const total = cum.at(-1) || 1;
		return cum.map((x) => (x / total) * 100);
	});
	const pct = (i: number) => pos[i] ?? 0;
	const now = $derived(stops[at]);
	const next = $derived(stops[at + 1]);
	// The train faces the way you're going.
	let last = $state(0);
	let dir = $state(1);
	$effect(() => { if (at !== last) { dir = at > last ? 1 : -1; last = at; } });
</script>

<nav class="ride sans" aria-label="Where you are on the ride">
	<div class="screen" aria-live="polite">
		<span class="roundel" aria-hidden="true">2</span>
		<span class="now"><small>NOW</small>{now?.label}</span>
		{#if next}<span class="next"><small>NEXT</small>{next.label}</span>{:else}<span class="next"><small>END OF THE LINE</small>Kennedy</span>{/if}
		<span class="count">{at + 1}/{stops.length}</span>
	</div>
	<div class="trackwrap">
		<div class="track">
			<div class="done" style="width:{pct(at)}%"></div>
			{#each stops as s, i (i)}
				<button class="st" class:big={s.big} class:passed={i <= at} class:here={i === at} style="left:{pct(i)}%" aria-label="Go to {s.label}" onclick={() => onjump(i)}>
					{#if s.big}<span class="name">{s.label.split(':')[0]}</span>{/if}
				</button>
			{/each}
			<svg class="train" class:back={dir < 0} style="left:{pct(at)}%" viewBox="0 0 64 24" aria-hidden="true">
				<rect x="1" y="3" width="56" height="18" rx="5" fill="#fff" stroke="#121212" stroke-width="2" />
				<path d="M57 6 q6 6 0 12" fill="#fff" stroke="#121212" stroke-width="2" />
				<rect x="7" y="7" width="9" height="6" rx="1.5" fill="#2f5d9b" />
				<rect x="20" y="7" width="9" height="6" rx="1.5" fill="#2f5d9b" />
				<rect x="33" y="7" width="9" height="6" rx="1.5" fill="#2f5d9b" />
				<rect x="46" y="7" width="7" height="6" rx="1.5" fill="#d9822b" />
				<rect x="1" y="16" width="56" height="2.5" fill="#00923f" />
			</svg>
		</div>
	</div>
</nav>

<style>
	.ride { position: sticky; top: var(--mast, 61px); z-index: 6; background: var(--paper); border-bottom: 1px solid var(--rule); padding: 8px 20px 26px; overflow-x: clip; }
	.screen { display: flex; align-items: center; gap: 12px; max-width: 1100px; margin: 0 auto 12px; background: #111; color: #ffb000; border-radius: 10px; padding: 7px 12px; font-family: ui-monospace, 'SF Mono', Menlo, monospace; font-size: 13px; }
	.roundel { flex: none; width: 22px; height: 22px; border-radius: 50%; background: #00923f; color: #fff; display: grid; place-items: center; font: 700 12px var(--sans); }
	.now, .next { display: flex; flex-direction: column; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
	.now { flex: 1.2; color: #fff; font-weight: 700; }
	.next { flex: 1; }
	.now small, .next small { font-size: 9px; letter-spacing: 2px; color: #9a958b; font-weight: 400; }
	.count { color: #9a958b; font-size: 11px; }
	.trackwrap { max-width: 1100px; margin: 0 auto; padding: 0 12px; }
	.track { position: relative; height: 8px; background: #d9d4c9; border-radius: 8px; }
	.done { position: absolute; inset: 0 auto 0 0; background: #00923f; border-radius: 8px; transition: width 0.7s cubic-bezier(0.2, 0.8, 0.2, 1); }
	.st { position: absolute; top: 50%; width: 4px; height: 12px; margin: -6px 0 0 -2px; border-radius: 2px; background: #bdb8ad; border: 0; padding: 0; cursor: pointer; }
	.st.passed { background: #0a5c29; }
	.st.big { width: 16px; height: 16px; margin: -8px 0 0 -8px; border-radius: 50%; background: #fff; border: 3px solid #9a958b; }
	.st.big.passed { border-color: #00923f; }
	.st.here { box-shadow: 0 0 0 5px rgba(0, 146, 63, 0.18); }
	.st::after { content: ''; position: absolute; inset: -10px -4px; }
	.name { position: absolute; top: 18px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; white-space: nowrap; color: var(--mute); letter-spacing: 0.5px; }
	.st.big:first-of-type .name { left: 0; transform: none; }
	.train { position: absolute; top: -26px; width: 46px; height: 18px; margin-left: -23px; transition: left 0.7s cubic-bezier(0.2, 0.8, 0.2, 1); animation: rock 1.2s ease-in-out infinite; }
	.train.back { transform: scaleX(-1); }
	@keyframes rock { 50% { translate: 0 -1px; } }
	@media (max-width: 640px) {
		.ride { --mast: 0px; padding: 6px 12px 22px; }
		.screen { font-size: 12px; gap: 8px; }
		.next, .count { display: none; }
		.name { display: none; }
	}
	@media (prefers-reduced-motion: reduce) { .done, .train { transition: none; animation: none; } }
</style>
