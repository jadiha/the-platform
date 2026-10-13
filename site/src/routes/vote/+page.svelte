<script lang="ts">
	// The Toronto journey (spec §11): a streetcar ride with stops for "Whose job is it?",
	// "Did it change anything?" (City Hall), every mayoral candidate in ballot order, and the exit.
	import '#lib/vote/vote.css';
	import Fact from '#lib/components/Fact.svelte';
	import SourceLine from '#lib/vote/SourceLine.svelte';
	import LineStreet from '#lib/vote/LineStreet.svelte';
	import WhoseJob from '#lib/vote/WhoseJob.svelte';
	import StoryCard from '#lib/vote/StoryCard.svelte';
	import Scenery from '#lib/vote/Scenery.svelte';
	import { displayName } from '#lib/vote/links.ts';
	import { siteData } from '#lib/context.ts';
	import { formatFact } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { facts } = siteData();
	const headline = facts['toronto.operating.2026.gross'] ? formatFact(facts['toronto.operating.2026.gross']) : 'budget';

	const mayor = $derived(data.official?.mayor ?? []);
	const profileOf = (b: string) => data.profiles.find((p) => p.candidate === b);
	const withSite = $derived(mayor.filter((c) => profileOf(c.ballot_name)));
	const without = $derived(mayor.filter((c) => !profileOf(c.ballot_name)));

	// Stops on the ride: 0 Start, 1 City Hall, 2 Candidates, 3 Also on your ballot, 4 Last stop.
	const stops = [
		{ label: 'Start: whose job is it?', big: true },
		{ label: 'City Hall: did it change anything?', big: true },
		{ label: 'Meet the candidates', big: true },
		{ label: 'Also on your ballot', big: true },
		{ label: 'Last stop: before you vote', big: true }
	];
	let section = $state(0);
	const els: HTMLElement[] = [];
	const smooth = () => (matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth') as ScrollBehavior;
	function stop(node: HTMLElement, i: number) {
		els[i] = node;
		const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && (section = i)), { rootMargin: '-40% 0px -55% 0px' });
		io.observe(node);
		return { destroy: () => io.disconnect() };
	}
	const jump = (i: number) => els[i]?.scrollIntoView({ behavior: smooth(), block: 'start' });
	const active = $derived(section);
	// Scenery behind stops that don't have their own illustration (the quiz has its own city).
	const scene = $derived([-1, 1, 2, 3, 4][section] ?? -1);

	// Every candidate is a tile; tapping one opens their full story card on top of the page.
	let open = $state<number | null>(null);
	const TOPIC_COLOR = { tax: '#d9822b', transit: '#2f5d9b', housing: '#4a8c5c', safety: '#7a5c99', money: '#3f7f74', other: '#8a857b' } as const;
	const TOPIC = { tax: 'Taxes', transit: 'Getting around', housing: 'Housing', safety: 'Safety', money: 'City money', other: 'Other' } as const;
	const topicsOf = (b: string) => [...new Set((profileOf(b)?.priorities ?? []).map((p) => p.topic))];
	const initials = (b: string) => displayName(b).split(' ').map((w) => w[0]).filter(Boolean).slice(0, 2).join('');
	const firstLine = (b: string) => {
		const r = profileOf(b)?.record ?? [];
		if (r.some((x) => x.text.startsWith('Mayor'))) return 'Current mayor';
		if (r.some((x) => x.text.startsWith('City Councillor'))) return 'City councillor';
		if (r.some((x) => x.text.includes('2023'))) return 'Ran in 2023';
		return 'First run for mayor';
	};
	function onKey(e: KeyboardEvent) {
		if (open === null) return;
		if (e.key === 'Escape') open = null;
		const o: number = open ?? 0;
		if (e.key === 'ArrowRight' && o < withSite.length - 1) open = o + 1;
		if (e.key === 'ArrowLeft' && o > 0) open = o - 1;
	}

	// Pins stay in this browser only.
	let pins = $state<string[]>([]);
	const PIN_KEY = 'ftb-vote-pins-v2';
	$effect(() => { try { pins = JSON.parse(localStorage.getItem(PIN_KEY) ?? '[]'); } catch { pins = []; } });
	function togglePin(b: string) {
		pins = pins.includes(b) ? pins.filter((k) => k !== b) : [...pins, b];
		try { localStorage.setItem(PIN_KEY, JSON.stringify(pins)); } catch { /* blocked storage: pins last this visit */ }
	}

	let shared = $state('');
	async function share() {
		const text = "I walked through who's running for mayor of Toronto, and what the City actually controls. Election day is Monday, October 26.";
		const url = location.origin + '/vote/';
		try {
			if (navigator.share) return await navigator.share({ title: 'Follow the Budget', text, url });
			await navigator.clipboard.writeText(`${text} ${url}`);
			shared = 'Link copied.';
		} catch { /* dismissed */ }
	}
</script>

<svelte:head>
	<title>Who's running for mayor, and what the City controls · Toronto votes October 26 · Follow the Budget</title>
	<meta name="description" content="Ride a streetcar through Toronto's mayoral race: what the City controls, what changed, and every candidate in their own words, with proof." />
	<meta property="og:title" content="The {headline} question" />
	<meta property="og:description" content="Toronto votes Monday, October 26. Meet every mayoral candidate in their own words, with every number linked to its proof." />
	<meta property="og:type" content="website" />
	<meta property="og:image" content="/og-vote.png" />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<svelte:window onkeydown={onKey} />
<LineStreet {stops} {active} onjump={jump} />
<Scenery {scene} />

<section class="hall wrap">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>The <span><Fact id="toronto.operating.2026.gross" plain /></span> question</h1>
	<p class="dek">
		Every year the mayor and council decide how <Fact id="toronto.operating.2026.gross" /> gets spent. This fall, {mayor.length} people are
		on the ballot for mayor. Hop on the streetcar for a ride through the city: first, what the City actually controls; then, everyone running, in their own words.
	</p>
	<p class="proofnote sans">Every number and every quote links to its proof. Nothing here tells you who to vote for.</p>
</section>

<section class="stop wide quiz" use:stop={0}>
	<h2 class="head"><span class="stopno sans">Stop 1</span>Whose job is it?</h2>
	<WhoseJob cards={data.whoseJob} />
</section>

<section class="stop wrap" use:stop={1}>
	<h2 class="head"><span class="stopno sans">Stop 2 · City Hall</span>Did it change anything?</h2>
	<p class="lede">Yes. Here's what the people you elect decided over the last three years, in your money.</p>
	<div class="bills sans">
		<div class="bill"><span class="yr">2024</span><span class="amt"><Fact id="toronto.property-tax.2024.avg-bill" /></span><span class="chg">up <Fact id="toronto.property-tax.2024.increase" /> that year</span></div>
		<div class="bill"><span class="yr">2025</span><span class="amt"><Fact id="toronto.property-tax.2025.avg-bill" /></span><span class="chg">up <Fact id="toronto.property-tax.2025.increase" /></span></div>
		<div class="bill"><span class="yr">2026</span><span class="amt"><Fact id="toronto.property-tax.2026.avg-bill" /></span><span class="chg">up <Fact id="toronto.property-tax.2026.increase" /></span></div>
	</div>
	<p class="cap sans">The City's property tax bill for an average Toronto home. Renters pay it too, inside their rent. Tap any number for its proof.</p>
	<div class="facts2 sans">
		<div><b>TTC fares:</b> <Fact id="toronto.ttc.fares.2026" />. <SourceLine id="toronto.ttc.fares.2026" /></div>
		<div><b>Fare cap:</b> since September, after <Fact id="toronto.ttc.fare-cap.2026" /> paid trips in a month, the rest of the month is free. <SourceLine id="toronto.ttc.fare-cap.2026" /></div>
		<div><b>Police:</b> <Fact id="toronto.police.2026.gross" /> this year. <b>Shelters:</b> <Fact id="toronto.shelter.2026.gross" />. <b>TTC:</b> <Fact id="toronto.ttc.2026.gross" />. <b>Roads and traffic:</b> <Fact id="toronto.transportation.2026.gross" />.</div>
	</div>
	<p class="lede">The mayor you choose on October 26 leads these decisions for the next four years.</p>
</section>

<section class="wide meet" use:stop={2}>
	<h2 class="head"><span class="stopno sans">Stop 3 · Meet the candidates</span>Everyone running for mayor with a campaign website</h2>
	<p class="lede sans">{withSite.length} candidates, in ballot order (alphabetical by last name). Tap anyone to see who they are, what they stand for, their numbers and their links.</p>
	<div class="legend sans">{#each Object.entries(TOPIC) as [k, label] (k)}<span><i style="background:{TOPIC_COLOR[k as keyof typeof TOPIC]}"></i>{label}</span>{/each}</div>
	<ul class="tiles sans">
		{#each withSite as c, i (c.ballot_name)}
			<li>
				<button class="tile" onclick={() => (open = i)} aria-label="Open {displayName(c.ballot_name)}">
					<span class="ini">{initials(c.ballot_name)}</span>
					<span class="nm">{displayName(c.ballot_name)}{#if pins.includes(c.ballot_name)} <span class="pinmark" title="Pinned">●</span>{/if}</span>
					<span class="sub">{firstLine(c.ballot_name)}{profileOf(c.ballot_name)?.note ? ' · campaign ended' : ''}</span>
					<span class="dots">{#each topicsOf(c.ballot_name) as t (t)}<i style="background:{TOPIC_COLOR[t]}" title={TOPIC[t]}></i>{/each}</span>
				</button>
			</li>
		{/each}
	</ul>
</section>

{#if open !== null}
	{@const c = withSite[open]}
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="overlay" onclick={(e) => e.target === e.currentTarget && (open = null)}>
		<div class="sheet" role="dialog" aria-modal="true" aria-label={displayName(c.ballot_name)}>
			<div class="sheetnav sans">
				<button onclick={() => (open = Math.max(0, (open ?? 0) - 1))} disabled={open === 0} aria-label="Previous candidate">‹</button>
				<span>{open + 1} of {withSite.length}</span>
				<button onclick={() => (open = Math.min(withSite.length - 1, (open ?? 0) + 1))} disabled={open === withSite.length - 1} aria-label="Next candidate">›</button>
				<button class="close" onclick={() => (open = null)} aria-label="Close">✕</button>
			</div>
			{#key open}
				<StoryCard
					person={c}
					profile={profileOf(c.ballot_name)}
					promises={data.promises.filter((p) => p.candidate === c.ballot_name)}
					index={open + 1}
					total={withSite.length}
					sources={data.recordSources}
					pinned={pins.includes(c.ballot_name)}
					onpin={() => togglePin(c.ballot_name)}
				/>
			{/key}
		</div>
	</div>
{/if}

<section class="stop wrap" use:stop={3}>
	<h2 class="head"><span class="stopno sans">Stop 4 · Also on your ballot</span>{without.length} more names you'll see</h2>
	<p class="lede sans">These candidates didn't list a campaign website with the City. Here's what they did list, and any public record.</p>
	<ul class="also sans">
		{#each without as c (c.ballot_name)}
			<li>
				<b>{displayName(c.ballot_name)}</b>
				{#each data.alsoRecords[c.ballot_name] ?? [] as r (r.text)}<span class="rec">{r.text} <a href={data.recordSources[r.src]?.url} target="_blank" rel="noopener">proof ↗</a></span>{/each}
				{#each c.social as s (s)}<a href={s} target="_blank" rel="noopener">{s.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]} ↗</a>{/each}
			</li>
		{/each}
	</ul>
	<p class="src sans"><a href={data.official?.source.url} target="_blank" rel="noopener">Proof: the City Clerk's certified list of candidates ↗</a></p>
</section>

<section class="stop wrap exit" use:stop={4}>
	<h2 class="head"><span class="stopno sans">Stop 5 · Last stop</span>Before you vote</h2>
	{#if pins.length}
		<div class="mywalk sans"><b>You pinned:</b> {pins.map(displayName).join(' · ')}<br /><span class="hint">Pins stay in this browser. Nothing is sent anywhere.</span></div>
	{/if}
	<ul class="checklist sans">
		<li><b>When:</b> Monday, October 26, 10 a.m. to 8 p.m.</li>
		<li><b>Who can vote:</b> Canadian citizens, 18 or older, who live in Toronto or own or rent property here. Students: vote in your home ward.</li>
		<li><b>Bring:</b> one piece of ID with your name and Toronto address.</li>
	</ul>
	<div class="cta sans">
		<a href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Where and when to vote (City of Toronto) ↗</a>
		<a href="https://www.toronto.ca/city-government/elections/voter-information/who-can-vote/" target="_blank" rel="noopener">Who can vote ↗</a>
		<a href="/vote/mayor/">All {mayor.length} candidates on one page</a>
	</div>
	<p class="next sans"><b>Next stop: Scarborough.</b> Your ward's councillor and school trustee candidates, who they are and what they stand for. Coming this week.</p>
	<button class="share sans" onclick={share}>Share the walk</button> <span class="hint sans">{shared}</span>
	<p class="method sans">
		How we made this: on {data.scan?.date ?? 'October 13'}, we read every mayoral campaign website on the City Clerk's certified candidate list. Quotes are copied word for word and link to the exact sentence on the candidate's own site, with a saved copy. Past results come from the City's official declaration. We don't use news reports or opponents' claims, and we don't predict what any promise would do.
		Spotted a mistake? <a href="/sources/#corrections">Tell us</a>.
	</p>
</section>

<style>
	.hall { margin-top: 28px; }
	.head { display: flex; flex-direction: column; gap: 2px; }
	.stopno { font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #da251d; }

	.kicker { color: #2f5d9b; }
	h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.04; margin: 10px 0 14px; letter-spacing: -1px; }
	h1 span { color: #2f5d9b; }
	h2 { font-size: clamp(28px, 4.5vw, 38px); margin: 6px 0 6px; letter-spacing: -0.5px; }
	.dek { font-size: 20px; line-height: 1.45; color: var(--ink-2); margin: 0; }
	.lede { font-size: 17px; color: var(--ink-2); margin: 0 0 6px; }
	.proofnote { font-size: 13px; color: var(--mute); margin: 12px 0 0; }
	.stop { padding-top: 40px; scroll-margin-top: 130px; }
	.quiz h2 { font-size: clamp(24px, 3.5vw, 30px); margin: 0 0 4px; }
	@media (max-width: 600px) { .quiz { padding-top: 28px; } }
	.meet { padding-top: 40px; }
	.bills { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 16px 0 6px; }
	.bill { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px; display: flex; flex-direction: column; gap: 2px; border-top: 5px solid #d9822b; }
	.yr { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: var(--mute); }
	.amt { font-family: var(--serif); font-size: 30px; font-weight: 700; }
	.chg { font-size: 13px; color: var(--ink-2); }
	.cap { font-size: 12.5px; color: var(--mute); margin: 0 0 14px; }
	.facts2 { display: grid; gap: 8px; font-size: 14px; background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px; margin-bottom: 12px; }
	.legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--mute); margin: 10px 0 12px; }
	.legend i, .dots i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: 0; }
	.tiles { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
	.tile { font: inherit; width: 100%; height: 100%; text-align: left; display: grid; grid-template-columns: 42px 1fr; grid-template-rows: auto auto auto; column-gap: 10px; align-items: center; background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 12px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s; }
	.tile:hover, .tile:focus-visible { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08); border-color: #bdb8ad; }
	.ini { grid-row: 1 / 4; width: 42px; height: 42px; border-radius: 50%; background: #2b2b2b; color: #fff; display: grid; place-items: center; font-weight: 700; font-size: 15px; letter-spacing: 0.5px; }
	.nm { font-weight: 700; font-size: 15px; line-height: 1.2; }
	.pinmark { color: #da251d; font-size: 10px; }
	.sub { font-size: 12px; color: var(--mute); }
	.dots { display: flex; gap: 2px; margin-top: 3px; min-height: 9px; }
	.dots i { margin: 0; }
	.overlay { position: fixed; inset: 0; z-index: 50; background: rgba(20, 20, 20, 0.45); backdrop-filter: blur(3px); display: grid; place-items: center; padding: 16px; animation: fade 0.2s ease; }
	@keyframes fade { from { opacity: 0; } }
	.sheet { width: min(480px, 100%); max-height: calc(100vh - 32px); overflow-y: auto; }
	.sheetnav { display: flex; align-items: center; gap: 10px; color: #fff; font-size: 13px; margin-bottom: 8px; }
	.sheetnav button { font: inherit; font-size: 18px; width: 36px; height: 36px; border-radius: 50%; border: 0; background: rgba(255, 255, 255, 0.92); cursor: pointer; }
	.sheetnav button:disabled { opacity: 0.35; cursor: default; }
	.sheetnav .close { margin-left: auto; font-size: 15px; }
	.sheet :global(.card) { max-width: none; }
	@media (max-width: 600px) { .tiles { grid-template-columns: 1fr 1fr; gap: 8px; } .tile { grid-template-columns: 1fr; padding: 10px; } .ini { grid-row: auto; width: 34px; height: 34px; font-size: 13px; margin-bottom: 6px; } .nm { font-size: 14px; } }
	@media (prefers-reduced-motion: reduce) { .tile, .overlay { transition: none; animation: none; } }
	.also { list-style: none; padding: 0; margin: 12px 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; font-size: 13px; }
	.also li { background: #fff; border: 1px solid var(--rule); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 3px; overflow-wrap: anywhere; }
	.also b { font-size: 15px; }
	.also a, .rec a { font-size: 12px; color: var(--mute); }
	.rec { color: var(--ink-2); }
	.src { font-size: 12px; }
	.exit { padding-bottom: 60px; }
	.checklist { font-size: 15px; line-height: 1.5; padding-left: 18px; }
	.mywalk { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 12px 14px; font-size: 14px; margin: 10px 0; }
	.cta { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0; }
	.cta a { font-size: 14px; font-weight: 600; border: 1.5px solid; border-radius: 999px; padding: 10px 16px; text-decoration: none; }
	.cta a:nth-child(1) { background: #2f5d9b; border-color: #2f5d9b; color: #fff; }
	.cta a:nth-child(2) { border-color: #d9822b; color: #a65d14; }
	.cta a:nth-child(3) { border-color: #4a8c5c; color: #356b45; }
	.next { font-size: 15px; background: #e7f1ea; border-radius: 12px; padding: 12px 14px; }
	.share { font: inherit; font-weight: 600; font-size: 14px; background: var(--ink); color: #fff; border: 0; border-radius: 999px; padding: 10px 18px; cursor: pointer; }
	.hint { font-size: 12px; color: var(--mute); }
	.method { font-size: 12.5px; color: var(--mute); margin-top: 24px; line-height: 1.5; }
	@media (max-width: 600px) {
		.bills { grid-template-columns: 1fr; }
		.amt { font-size: 26px; }
	}
</style>
