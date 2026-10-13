<script lang="ts">
	// "The $18.9 billion question": a walk through five rooms of the city budget, each ending with
	// what mayoral candidates have published about it. Spec: docs/superpowers/specs/2026-10-12-election-guide-design.md
	import '#lib/vote/vote.css';
	import Fact from '#lib/components/Fact.svelte';
	import SourceLine from '#lib/vote/SourceLine.svelte';
	import VoteMap, { type Stop } from '#lib/vote/VoteMap.svelte';
	import PromiseQuote from '#lib/vote/PromiseQuote.svelte';
	import TaxWhatIf from '#lib/vote/TaxWhatIf.svelte';
	import HomesWhatIf from '#lib/vote/HomesWhatIf.svelte';
	import TripsWhatIf from '#lib/vote/TripsWhatIf.svelte';
	import { displayName } from '#lib/vote/links.ts';
	import { siteData } from '#lib/context.ts';
	import { formatFact, money } from '#lib/format.ts';
	import type { RoomId } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { facts } = siteData();
	const headline = facts['toronto.operating.2026.gross'] ? formatFact(facts['toronto.operating.2026.gross']) : 'budget';

	const ROOMS: { id: RoomId; title: string; place: string; color: string; tint: string; stop: Stop }[] = [
		{ id: 'tax', title: 'Your tax bill', place: 'Home', color: '#d9822b', tint: '#fbefe2', stop: { lonlat: [-79.26, 43.71], label: 'Home' } },
		{ id: 'transit', title: 'Getting around', place: 'Kennedy Station · the TTC, roads and traffic', color: '#2f5d9b', tint: '#e8eef7', stop: { lonlat: [-79.2637, 43.7323], label: 'Kennedy Stn' } },
		{ id: 'housing', title: 'Rent and housing', place: 'Scarborough Centre · shelters and homes', color: '#4a8c5c', tint: '#e7f1ea', stop: { lonlat: [-79.258, 43.7754], label: 'Scarborough Centre' } },
		{ id: 'build', title: 'What gets built here', place: 'City projects in your ward', color: '#3f7f74', tint: '#e4f0ee', stop: { lonlat: [-79.262, 43.8135], label: 'Finch Ave E' } },
		{ id: 'safety', title: 'Safety', place: 'A police division · Toronto Police Service', color: '#7a5c99', tint: '#efe9f5', stop: { lonlat: [-79.1878, 43.7712], label: '43 Division' } }
	];

	// svelte-ignore state_referenced_locally
	let ward = $state<number | null>(21);
	let active = $state(-1);
	const color = $derived(ROOMS[Math.max(active, 0)].color);
	const wardRow = $derived(data.wards?.wards.find((w) => w.ward === ward));

	const mayor = $derived(data.official?.mayor ?? []);
	const byRoom = (room: RoomId) => data.promises.filter((p) => p.room === room);
	/** Everyone on the mayor ballot without a promise in this room, in ballot order. */
	const others = (room: RoomId) => {
		const has = new Set(byRoom(room).map((p) => p.candidate));
		return mayor.filter((c) => !has.has(c.ballot_name));
	};

	// Passport stamps and pins (kept in this browser only).
	let seen = $state<Set<number>>(new Set());
	let pins = $state<string[]>([]);
	const PIN_KEY = 'ftb-vote-pins';
	$effect(() => {
		try { pins = JSON.parse(localStorage.getItem(PIN_KEY) ?? '[]'); } catch { pins = []; }
	});
	function togglePin(key: string) {
		pins = pins.includes(key) ? pins.filter((k) => k !== key) : [...pins, key];
		try { localStorage.setItem(PIN_KEY, JSON.stringify(pins)); } catch { /* storage blocked: pins last for this visit */ }
	}
	const pinKey = (p: { candidate: string; text: string }) => `${p.candidate}|${p.text.slice(0, 40)}`;
	const pinned = $derived(data.promises.filter((p) => pins.includes(pinKey(p))));

	// Which room is in the middle of the screen.
	function room(node: HTMLElement, i: number) {
		const io = new IntersectionObserver(
			(es) => es.forEach((e) => { if (e.isIntersecting) { active = i; seen = new Set([...seen, i]); } }),
			{ rootMargin: '-45% 0px -45% 0px' }
		);
		io.observe(node);
		return { destroy: () => io.disconnect() };
	}

	let shared = $state('');
	async function share() {
		const text = "I walked through Toronto's city budget before I voted. Election day is Monday, October 26.";
		const url = location.origin + '/vote/';
		try {
			if (navigator.share) { await navigator.share({ title: 'Follow the Budget', text, url }); return; }
			await navigator.clipboard.writeText(`${text} ${url}`);
			shared = 'Link copied.';
		} catch { /* dismissed */ }
	}
</script>

<svelte:head>
	<title>The {headline} question · Toronto votes October 26 · Follow the Budget</title>
	<meta name="description" content="Walk through Toronto's city budget in five rooms, then see what mayoral candidates have promised about it, with every number linked to its proof." />
	<meta property="og:title" content="The {headline} question" />
	<meta property="og:description" content="Toronto votes Monday, October 26. See what council controls, and what mayoral candidates have promised, with every number linked to its proof." />
	<meta property="og:type" content="website" />
	<meta property="og:image" content="/og-vote.png" />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<div class="passport sans" aria-label="Rooms visited">
	YOUR WALK
	{#each ROOMS as r, i (r.id)}<i class:got={seen.has(i)} style="--c:{r.color}" title={r.title}></i>{/each}
</div>

<section class="hall wrap">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>The <span><Fact id="toronto.operating.2026.gross" plain /></span> question</h1>
	<p class="dek">
		Every year, city council decides how <Fact id="toronto.operating.2026.gross" /> gets spent: your bus, your rent, your tax bill.
		On October 26 you choose who sits there. Walk through five rooms to see the money, then read what the people running for mayor have promised about it, in their own words.
	</p>
	<p class="proofnote sans">Every number on this page links to its proof. Tap a number, or a "Proof" or "See it highlighted" link.</p>
	<div class="ticket sans">
		<span class="lbl">YOUR TICKET · PICK YOUR SCARBOROUGH WARD (OR TAP IT ON THE MAP)</span>
		{#each data.wards?.wards.filter((w) => w.scarborough) ?? [] as w (w.ward)}
			<button aria-pressed={ward === w.ward} onclick={() => (ward = w.ward)}>{w.ward} {w.name.replace(/^Scarborough[ -]?/, '') || w.name}</button>
		{/each}
		<span class="hint">Everyone in Toronto votes for mayor, so the promises in this walk are from the mayor's race.</span>
	</div>
</section>

<div class="scrolly">
	<div class="sticky">
		<VoteMap stops={ROOMS.map((r) => r.stop)} {active} bind:ward {color} />
		<div class="legend sans">{#each ROOMS as r (r.id)}<span><i style="background:{r.color}"></i>{r.title}</span>{/each}</div>
	</div>

	<div class="steps">
		{#each ROOMS as r, i (r.id)}
			{@const ps = byRoom(r.id)}
			{@const rest = others(r.id)}
			<article class="room" class:on={active === i} style="--c:{r.color};--t:{r.tint}" use:room={i}>
				<div class="n sans">ROOM {i + 1} OF {ROOMS.length}</div>
				<h2>{r.title}</h2>
				<div class="place sans">{r.place}</div>

				<div class="exhibit">
					{#if r.id === 'tax'}
						The average Toronto home's city property tax bill this year:
						<span class="big"><Fact id="toronto.property-tax.2026.avg-bill" /></span>
						<span class="sub sans">Up <Fact id="toronto.property-tax.2026.increase" /> from 2025. Renters pay it too, inside their rent.</span>
						<SourceLine id="toronto.property-tax.2026.avg-bill" />
						<div class="decides sans">Who decides: council votes on the tax increase every winter, when it passes the budget.</div>
						<TaxWhatIf bill={Number(facts['toronto.property-tax.2026.avg-bill']?.value)} promises={ps} />
					{:else if r.id === 'transit'}
						Running the TTC costs
						<span class="big"><Fact id="toronto.ttc.2026.gross" /></span>
						<span class="sub sans">a year. The city itself pays <Fact id="toronto.ttc.2026.net" />; fares and other sources pay the rest.</span>
						<SourceLine id="toronto.ttc.2026.gross" />
						<p>Roads, traffic signals and road safety are a separate budget:</p>
						<span class="big mid"><Fact id="toronto.transportation.2026.gross" /></span>
						<span class="sub sans">Transportation Services, 2026.</span>
						<SourceLine id="toronto.transportation.2026.gross" />
						<div class="decides sans">Who decides: council sets the TTC's budget, fares and service each year, and decides what happens on city roads.</div>
						<TripsWhatIf promises={ps}>
							<p class="fine sans">Today: after <Fact id="toronto.ttc.fare-cap.2026" /> paid trips in a calendar month, the rest of the month is free. <SourceLine id="toronto.ttc.fare-cap.2026" /></p>
						</TripsWhatIf>
					{:else if r.id === 'housing'}
						The city's shelter system costs
						<span class="big"><Fact id="toronto.shelter.2026.gross" /></span>
						<span class="sub sans">a year, 2026.</span>
						<SourceLine id="toronto.shelter.2026.gross" />
						<div class="decides sans">Who decides: council funds shelters and city housing programs. Rent rules are set by the Province.</div>
						<HomesWhatIf promises={ps} />
					{:else if r.id === 'build'}
						{#if wardRow}
							City projects planned in Ward {wardRow.ward} {wardRow.name}, 2026–2035:
							<span class="big">{money(wardRow.capital10yr)}</span>
							{#if wardRow.topProjects[0]}<span class="sub sans">Biggest: {wardRow.topProjects[0].name} ({wardRow.topProjects[0].program}), {money(wardRow.topProjects[0].amount10yr)}.</span>{/if}
							<a class="src sans" href="https://open.toronto.ca/dataset/budget-capital-budget-plan-by-ward-10-yr-approved/" target="_blank" rel="noopener">Proof: City of Toronto Open Data, 10-year capital plan by ward ↗</a>
						{/if}
						<p class="sans small">Most city projects aren't tied to one ward: <Fact id="scarborough.capital.city-wide-share" /> of the 10-year plan is city-wide.</p>
						<div class="decides sans">Who decides: council approves the 10-year capital plan each year, along with the budget.</div>
					{:else if r.id === 'safety'}
						The police budget is
						<span class="big"><Fact id="toronto.police.2026.gross" /></span>
						<span class="sub sans">a year, 2026.</span>
						<SourceLine id="toronto.police.2026.gross" />
						<div class="decides sans">Who decides: council sets the total. The Police Services Board decides how it's spent.</div>
					{/if}
				</div>

				{#if r.id !== 'build' && data.reviewing.includes(r.id)}
					<div class="wall"><p class="reviewing sans">Mayoral candidates' promises on this topic are being checked word for word against their campaign sites. They'll appear here once every one is checked.</p></div>
				{:else if r.id !== 'build'}
					<div class="wall">
						<div class="h sans">WHAT MAYORAL CANDIDATES HAVE PROMISED, IN THEIR OWN WORDS</div>
						<div class="plaques">
							{#each ps as p (p.candidate + p.text)}
								<PromiseQuote {p} pinned={pins.includes(pinKey(p))} onpin={() => togglePin(pinKey(p))} />
							{/each}
						</div>
						<details class="rest sans">
							<summary>{rest.length} other candidates: no promise with a number or clear rule on this topic on their campaign site</summary>
							<p>{rest.map((c) => displayName(c.ballot_name)).join(' · ')}</p>
							<p>Some have no campaign website on the City's list. <a href="/vote/mayor/">See every candidate and their links</a>.</p>
						</details>
					</div>
				{/if}
			</article>
		{/each}
	</div>
</div>

<section class="exit wrap">
	<p class="kicker">Exit · your ballot</p>
	<h2>Before you vote</h2>
	<div class="mywalk sans">
		<b>Your walk:</b> {seen.size} of {ROOMS.length} rooms · {pinned.length} promise{pinned.length === 1 ? '' : 's'} pinned
		{#if pinned.length}<ul>{#each pinned as p (pinKey(p))}<li><b>{displayName(p.candidate)}:</b> “{p.text}”</li>{/each}</ul>{/if}
		<span class="hint">Pins stay in this browser. Nothing about what you pinned is sent anywhere.</span>
	</div>
	<div class="cta sans">
		<a href="/vote/mayor/">Every mayoral candidate and their links</a>
		<a href="https://www.toronto.ca/city-government/elections/candidate-list/#tabCouncillor" target="_blank" rel="noopener">Who's running for council in Ward {ward ?? ''} (City of Toronto) ↗</a>
		<a href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Where and when to vote (City of Toronto) ↗</a>
	</div>
	<button class="share sans" onclick={share}>Share the walk</button> <span class="hint">{shared}</span>
	<p class="method sans">
		How we chose these promises: on {data.scan?.date ?? 'October 13'}, we read every mayoral campaign website on the City Clerk's certified candidate list, and included each promise that has a number or a clear rule on these five topics, word for word. We don't include news reports or opponents' estimates, and we don't predict what a promise would do.
		Spotted a mistake or a missing promise? <a href="/sources/#corrections">Tell us</a>.
	</p>
</section>

<style>
	.passport { position: sticky; top: var(--mast, 61px); z-index: 5; background: var(--paper); border-bottom: 1px solid var(--rule); display: flex; gap: 8px; align-items: center; justify-content: center; padding: 8px; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; }
	.passport i { width: 20px; height: 20px; border-radius: 50%; border: 1.5px dashed #aaa; transition: all 0.4s; }
	.passport i.got { border-style: solid; border-color: var(--c); background: var(--c); transform: rotate(-8deg); }
	.hall { margin-top: 44px; }
	.kicker { color: #2f5d9b; }
	h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.04; margin: 10px 0 14px; letter-spacing: -1px; }
	h1 span { color: #2f5d9b; }
	.dek { font-size: 20px; line-height: 1.45; color: var(--ink-2); margin: 0; }
	.proofnote { font-size: 13px; color: var(--mute); margin: 12px 0 0; }
	.ticket { margin: 24px 0 8px; border: 1.5px dashed #2f5d9b; background: #f6f9fd; padding: 16px 18px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; border-radius: 6px; }
	.ticket .lbl { font-size: 11px; font-weight: 600; letter-spacing: 2px; width: 100%; color: #2f5d9b; }
	.ticket button { font: inherit; font-size: 14px; background: #fff; border: 1px solid var(--ink); border-radius: 999px; padding: 7px 13px; cursor: pointer; }
	.ticket button[aria-pressed='true'] { background: #2f5d9b; border-color: #2f5d9b; color: #fff; }
	.hint { font-size: 12px; color: var(--mute); }
	.scrolly { display: grid; grid-template-columns: 1fr 1fr; gap: 44px; max-width: 1140px; margin: 0 auto; padding: 0 20px; }
	.sticky { position: sticky; top: calc(var(--mast, 61px) + 37px); height: calc(100vh - var(--mast, 61px) - 37px); display: flex; flex-direction: column; justify-content: center; }
	.legend { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; font-size: 11px; color: var(--mute); margin-top: 6px; }
	.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: -1px; }
	.steps { padding: 16vh 0 24vh; }
	.room { margin: 0 0 40vh; opacity: 0.35; padding: 22px 22px 26px; border-top: 6px solid var(--c); border-radius: 0 0 14px 14px; background: linear-gradient(var(--t), var(--t)) top / 100% 0 no-repeat; transition: opacity 0.5s, background-size 0.7s; }
	.room.on { opacity: 1; background-size: 100% 100%; }
	.n { font-size: 11px; font-weight: 600; letter-spacing: 2px; color: var(--c); }
	h2 { font-size: 32px; margin: 6px 0 2px; letter-spacing: -0.5px; }
	.place { font-size: 13px; color: var(--mute); margin-bottom: 14px; }
	.exhibit { font-size: 18px; line-height: 1.55; }
	.big { font-weight: 700; font-size: 46px; line-height: 1; display: block; margin: 12px 0 6px; color: var(--c); }
	.big.mid { font-size: 34px; }
	.sub { display: block; font-size: 13px; color: var(--mute); }
	.small { font-size: 13px; color: var(--ink-2); }
	.src { display: inline-block; font-size: 11.5px; color: var(--mute); margin-top: 4px; }
	.decides { font-size: 13px; background: #fff; padding: 8px 10px; margin: 12px 0 6px; border-left: 3px solid var(--c); border-radius: 0 8px 8px 0; }
	.wall .h { font-size: 11px; font-weight: 600; letter-spacing: 2px; margin: 20px 0 8px; }
	.plaques { display: grid; gap: 8px; }
	.room :global(.plaque) { transform: translateY(8px); opacity: 0; transition: all 0.5s; }
	.room.on :global(.plaque) { transform: none; opacity: 1; }
	.reviewing { font-size: 13px; background: #fff; border: 1px dashed var(--rule); border-radius: 8px; padding: 10px 12px; color: var(--ink-2); }
	.rest { font-size: 12.5px; color: var(--ink-2); margin-top: 10px; background: #fff; border-radius: 8px; padding: 8px 10px; }
	.rest summary { cursor: pointer; }
	.exit { margin: 0 auto 80px; padding-top: 30px; border-top: 8px solid transparent; border-image: linear-gradient(90deg, #2f5d9b 0 33.3%, #d9822b 33.3% 66.6%, #4a8c5c 66.6%) 1; }
	.exit .kicker { color: #4a8c5c; }
	.mywalk { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px 16px; font-size: 14px; margin: 12px 0; }
	.mywalk ul { margin: 8px 0; padding-left: 18px; font-size: 13px; }
	.cta { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0; }
	.cta a { font-size: 14px; font-weight: 600; border: 1.5px solid; border-radius: 999px; padding: 10px 16px; text-decoration: none; }
	.cta a:nth-child(1) { background: #2f5d9b; border-color: #2f5d9b; color: #fff; }
	.cta a:nth-child(2) { border-color: #d9822b; color: #a65d14; }
	.cta a:nth-child(3) { border-color: #4a8c5c; color: #356b45; }
	.share { font: inherit; font-weight: 600; font-size: 14px; background: var(--ink); color: #fff; border: 0; border-radius: 999px; padding: 10px 18px; cursor: pointer; }
	.method { font-size: 12.5px; color: var(--mute); margin-top: 24px; line-height: 1.5; }
	@media (max-width: 640px) { .passport { --mast: 0px; } .sticky { --mast: 0px; } }
	@media (max-width: 860px) {
		.scrolly { grid-template-columns: 1fr; gap: 0; }
		.sticky { height: auto; top: calc(var(--mast, 61px) + 37px); z-index: 3; background: var(--paper); border-bottom: 1px solid var(--rule); padding: 4px 0; }
		.sticky :global(svg) { max-height: 34vh; }
		.legend { display: none; }
		.room { padding: 18px 14px 22px; }
		.big { font-size: 38px; }
	}
	@media (prefers-reduced-motion: reduce) {
		.room, .room :global(.plaque), .passport i { transition: none; }
		.room :global(.plaque) { transform: none; opacity: 1; }
	}
</style>
