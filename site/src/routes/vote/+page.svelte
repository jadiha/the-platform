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
	import TorontoWardMap from '#lib/vote/TorontoWardMap.svelte';
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

	// One stop per screen. The streetcar bar shows where you are; "Next stop" moves you along.
	const stops = [
		{ label: 'Hop on', big: true },
		{ label: 'Stop 1: whose job is it?', big: true },
		{ label: 'Stop 2: City Hall', big: true },
		{ label: 'Stop 3: meet the candidates', big: true },
		{ label: 'Stop 4: also on your ballot', big: true },
		{ label: 'Stop 5: your ward', big: true },
		{ label: 'Stop 6: before you vote', big: true }
	];
	let step = $state(0);
	// Keep the stop in the address bar so Back works and a stop can be shared.
	$effect(() => {
		const read = () => { const m = location.hash.match(/^#stop-(\d)$/); step = m ? Math.min(stops.length - 1, +m[1]) : 0; };
		read();
		addEventListener('hashchange', read);
		return () => removeEventListener('hashchange', read);
	});
	function go(i: number) {
		const n = Math.max(0, Math.min(stops.length - 1, i));
		if (n === step) return;
		history.pushState(null, '', n ? `#stop-${n}` : location.pathname);
		step = n;
		scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
	}
	const jump = go;
	const active = $derived(step);
	// Scenery only on the welcome screen; later stops have their own pictures and stay uncluttered.
	const scene = $derived(step === 0 ? 0 : -1);

	// City Hall stop: numbers for the charts come from the fact registry (each tap shows proof).
	const num = (id: string) => Number(facts[id]?.value ?? 0);
	const billYears = [
		{ year: 2024, bill: 'toronto.property-tax.2024.avg-bill', inc: 'toronto.property-tax.2024.increase' },
		{ year: 2025, bill: 'toronto.property-tax.2025.avg-bill', inc: 'toronto.property-tax.2025.increase' },
		{ year: 2026, bill: 'toronto.property-tax.2026.avg-bill', inc: 'toronto.property-tax.2026.increase' }
	].map((y) => ({ ...y, v: num(y.bill) }));
	const billMax = Math.max(...billYears.map((y) => y.v));
	const billMin = Math.min(...billYears.map((y) => y.v));
	const bigBudgets = [
		{ id: 'toronto.ttc.2026.gross', label: 'TTC', color: '#2f5d9b' },
		{ id: 'toronto.police.2026.gross', label: 'Police', color: '#7a5c99' },
		{ id: 'toronto.shelter.2026.gross', label: 'Shelters', color: '#4a8c5c' },
		{ id: 'toronto.transportation.2026.gross', label: 'Roads & traffic', color: '#3f7f74' }
	].map((b) => ({ ...b, v: num(b.id) }));
	const bigMax = Math.max(...bigBudgets.map((b) => b.v));

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
		return 'First run';
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
			if (navigator.share) return await navigator.share({ title: 'Next Stop: Ballot', text, url });
			await navigator.clipboard.writeText(`${text} ${url}`);
			shared = 'Link copied.';
		} catch { /* dismissed */ }
	}
</script>

<svelte:head>
	<title>Who's running for mayor, and what the City controls · Toronto votes October 26 · Next Stop: Ballot</title>
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

{#key step}
<div class="screenwrap">
{#if step === 0}
<section class="hall wrap screen">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>The <span><Fact id="toronto.operating.2026.gross" plain /></span> question</h1>
	<p class="dek">
		Every year the mayor and council decide how <Fact id="toronto.operating.2026.gross" /> gets spent. This fall, {mayor.length} people are
		on the ballot for mayor. Hop on the streetcar for a ride through the city: first, what the City actually controls; then, everyone running, in their own words.
	</p>
	<p class="proofnote sans">Every number and every quote links to its proof. Nothing here tells you who to vote for.</p>
	<button class="hop sans" onclick={() => go(1)}>Hop on →</button>
	<p class="howto sans">Six stops, about five minutes.</p>
</section>
{:else if step === 1}
<section class="stop wide quiz">
	<h2 class="head"><span class="stopno sans">Stop 1</span>Whose job is it?</h2>
	<WhoseJob cards={data.whoseJob} />
</section>
{:else if step === 2}
<section class="stop wide cityhall">
	<h2 class="head"><span class="stopno sans">Stop 2 · City Hall</span>Did it change anything?</h2>
	<p class="lede">Yes. The mayor and council set your tax bill and the City's biggest budgets every year. The mayor you choose leads these decisions for the next four years.</p>
	<div class="charts sans">
		<figure class="chart">
			<figcaption>The City tax bill on an average Toronto home</figcaption>
			<div class="stairs">
				{#each billYears as y, i (y.year)}
					<div class="step">
						<span class="val"><Fact id={y.bill} /></span>
						{#if i > 0}<span class="jump">+${(y.v - billYears[i - 1].v).toLocaleString('en-CA')}</span>{/if}
						<div class="bar" style="height:{16 + ((y.v - billMin) / (billMax - billMin)) * 64}px"></div>
						<span class="yr">{y.year}</span>
						<span class="pc">up <Fact id={y.inc} plain /></span>
					</div>
				{/each}
			</div>
			<p class="note">Renters pay it too, inside their rent. Bars don't start at zero.</p>
		</figure>
		<figure class="chart">
			<figcaption>Where the biggest City budgets go, 2026</figcaption>
			<ul class="hbars">
				{#each bigBudgets as b (b.id)}
					<li>
						<span class="lbl">{b.label}</span>
						<div class="track"><div class="fill" style="width:{(b.v / bigMax) * 100}%;background:{b.color}"></div></div>
						<span class="val"><Fact id={b.id} short /></span>
					</li>
				{/each}
			</ul>
			<p class="note">Tap any number for its proof.</p>
		</figure>
	</div>
	<div class="decisions sans">
		<div><span class="tag">Decided</span> TTC fares <Fact id="toronto.ttc.fares.2026" plain /> <a href={facts['toronto.ttc.fares.2026']?.primary.url} target="_blank" rel="noopener">proof ↗</a></div>
		<div><span class="tag">Decided</span> Free after <Fact id="toronto.ttc.fare-cap.2026" plain /> paid TTC trips a month <a href={facts['toronto.ttc.fare-cap.2026']?.primary.url} target="_blank" rel="noopener">proof ↗</a></div>
	</div>
</section>
{:else if step === 3}
<section class="wide meet">
	<h2 class="head"><span class="stopno sans">Stop 3 · Meet the candidates</span>Everyone running for mayor with a campaign website</h2>
	<p class="lede sans">{withSite.length} candidates in ballot order. Tap anyone to open their card.</p>
	<div class="legend sans">{#each Object.entries(TOPIC) as [k, label] (k)}<span><i style="background:{TOPIC_COLOR[k as keyof typeof TOPIC]}"></i>{label}</span>{/each}</div>
	<ul class="tiles sans">
		{#each withSite as c, i (c.ballot_name)}
			<li>
				<button class="tile" onclick={() => (open = i)} aria-label="Open {displayName(c.ballot_name)}">
					<span class="ini">{initials(c.ballot_name)}</span>
					<span class="nm"><span class="full">{displayName(c.ballot_name)}</span><span class="ln">{c.ballot_name.split(',')[0]}</span>{#if pins.includes(c.ballot_name)} <span class="pinmark" title="Pinned">●</span>{/if}</span>
					<span class="sub">{firstLine(c.ballot_name)}{profileOf(c.ballot_name)?.note ? ' · ended' : ''}<span class="dots" aria-hidden="true">{#each topicsOf(c.ballot_name) as t (t)}<i style="background:{TOPIC_COLOR[t]}"></i>{/each}</span></span>
				</button>
			</li>
		{/each}
	</ul>
</section>
{:else if step === 4}
<section class="stop wrap">
	<h2 class="head"><span class="stopno sans">Stop 4 · Also on your ballot</span>{without.length} more names you'll see</h2>
	<p class="lede sans">These candidates didn't list a campaign website with the City. Here's what they did list, and any public record.</p>
	<ul class="also sans">
		{#each without as c (c.ballot_name)}
			{@const rec = data.alsoRecords[c.ballot_name]?.[0]}
			<li>
				<b>{displayName(c.ballot_name)}</b>
				<span class="meta">
					{#if rec}<a href={data.recordSources[rec.src]?.url} target="_blank" rel="noopener">ran in 2023</a>{/if}
					{#each c.social as s (s)}<a href={s} target="_blank" rel="noopener">{s.replace(/^https?:\/\/(www\.)?/, '').split('/')[0].replace('.com', '')}</a>{/each}
					{#if !rec && !c.social.length}<span class="none">no links listed</span>{/if}
				</span>
			</li>
		{/each}
	</ul>
	<p class="src sans"><a href={data.official?.source.url} target="_blank" rel="noopener">Proof: the City Clerk's certified list of candidates ↗</a></p>
</section>
{:else if step === 5}
<section class="stop wide wardstop">
	<h2 class="head"><span class="stopno sans">Stop 5 · Your ward</span>Who's running in your ward?</h2>
	<p class="wardp sans">You also pick a city councillor and a school board trustee for your ward.
		<a href="https://www.toronto.ca/city-government/data-research-maps/neighbourhoods-communities/ward-profiles/" target="_blank" rel="noopener">Not sure of your ward? ↗</a></p>
	<TorontoWardMap listUrl="https://www.toronto.ca/city-government/elections/candidate-list/" chartUrl={data.official?.school_chart.url ?? ''} races={data.races} guided={data.wards.filter((w) => w.scarborough).map((w) => w.ward)} />
</section>
{:else}
<section class="stop wide exit">
	<h2 class="head"><span class="stopno sans">Stop 6 · Last stop</span>Before you vote</h2>
	{#if pins.length}
		<div class="mywalk sans"><b>You pinned:</b> {pins.map(displayName).join(' · ')}<br /><span class="hint">Pins stay in this browser. Nothing is sent anywhere.</span></div>
	{/if}
	<div class="vote3 sans">
		<div><b>When</b>Monday, October 26, 10 a.m. to 8 p.m.</div>
		<div><b>Who</b>Canadian citizens, 18+, living in Toronto (or owning or renting property here). Students: your home ward.</div>
		<div><b>Bring</b>One ID with your name and Toronto address.</div>
	</div>
	<div class="cta sans">
		<a href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Where to vote ↗</a>
		<a href="https://www.toronto.ca/city-government/elections/voter-information/who-can-vote/" target="_blank" rel="noopener">Who can vote ↗</a>
		<a href="/vote/mayor/">All {mayor.length} mayoral candidates</a>
	</div>
	<details class="method sans"><summary>How we made this</summary>
		On {data.scan?.date ?? 'October 13'}, we read every mayoral campaign website on the City Clerk's certified candidate list. Quotes are copied word for word and link to the exact sentence on the candidate's own site, with a saved copy. Past results come from the City's official declaration. We don't use news reports or opponents' claims, and we don't predict what any promise would do.
		Spotted a mistake? <a href="/sources/#corrections">Tell us</a>. An independent, non-partisan community project, not affiliated with any government, party or candidate.
	</details>
</section>
{/if}
{#if step > 0}
<nav class="stepnav {step === 4 ? 'wrap' : 'wide'} sans" aria-label="Move along the ride">
	{#if step < stops.length - 1}
		<button class="fwd" onclick={() => go(step + 1)}>Next stop<span class="full">: {stops[step + 1].label.split(': ')[1]}</span> →</button>
	{:else}
		<button class="fwd" onclick={share}>Share the ride ↗</button>
		<span class="hint">{shared}</span>
	{/if}
	<button class="back" onclick={() => go(step - 1)}>‹ Back</button>
</nav>
{/if}
</div>
{/key}

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


<style>
	.screenwrap { min-height: calc(100vh - 200px); padding-bottom: 48px; animation: slidein 0.45s cubic-bezier(0.2, 0.8, 0.2, 1); }
	@keyframes slidein { from { opacity: 0; transform: translateX(30px); } }
	.hall { margin-top: 8vh; }
	.hop { font: inherit; font-weight: 700; font-size: 18px; background: #da251d; color: #fff; border: 0; border-radius: 999px; padding: 14px 28px; margin-top: 22px; cursor: pointer; }
	.howto { font-size: 13px; color: var(--mute); margin-top: 8px; }
	.stepnav { display: flex; align-items: center; gap: 16px; margin-top: 24px; }
	.stepnav button { font: inherit; font-weight: 700; font-size: 15px; border-radius: 999px; padding: 11px 18px; cursor: pointer; }
	.stepnav .back { background: none; border: 0; padding: 11px 4px; color: var(--mute); font-weight: 600; }
	.stepnav .back:hover { color: var(--ink); }
	.stepnav .back:disabled { opacity: 0.3; cursor: default; }
	.stepnav .fwd { background: #da251d; color: #fff; border: 0; }
	.head { display: flex; flex-direction: column; gap: 2px; }
	.stopno { font-size: 12px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #da251d; }

	.kicker { color: #2f5d9b; }
	h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.04; margin: 10px 0 14px; letter-spacing: -1px; }
	h1 span { color: #2f5d9b; }
	h2 { font-size: clamp(28px, 4.5vw, 38px); margin: 6px 0 6px; letter-spacing: -0.5px; }
	.dek { font-size: 20px; line-height: 1.45; color: var(--ink-2); margin: 0; }
	.lede { font-size: 17px; color: var(--ink-2); margin: 0 0 6px; }
	.proofnote { font-size: 13px; color: var(--mute); margin: 12px 0 0; }
	.stop { padding-top: 32px; }
	.quiz h2 { font-size: clamp(24px, 3.5vw, 30px); margin: 0 0 4px; }
	@media (max-width: 600px) { .quiz { padding-top: 20px; } .hall { margin-top: 4vh; } }
	@media (prefers-reduced-motion: reduce) { .screenwrap { animation: none; } }
	.meet { padding-top: 24px; }
	.meet .legend { margin: 6px 0 12px; }
	.charts { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; margin: 16px 0 10px; }
	.chart { margin: 0; background: #fff; border: 1px solid var(--rule); border-radius: 16px; padding: 14px 16px 10px; }
	figcaption { font-size: 13px; font-weight: 700; margin-bottom: 10px; }
	.stairs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; align-items: end; }
	.step { display: flex; flex-direction: column; justify-content: flex-end; align-items: center; }
	.step .bar { width: 70%; background: linear-gradient(#e89a4e, #d9822b); border-radius: 8px 8px 0 0; min-height: 8px; }
	.step .val { font-family: var(--serif); font-weight: 700; font-size: 20px; margin-bottom: 4px; }
	.step .jump { font-size: 11px; font-weight: 700; color: #a65d14; background: #fbefe2; border-radius: 999px; padding: 1px 7px; margin-bottom: 4px; }
	.step .yr { font-size: 12px; font-weight: 700; margin-top: 6px; }
	.step .pc { font-size: 11px; color: var(--mute); }
	.hbars { list-style: none; padding: 0; margin: 4px 0 0; display: grid; gap: 12px; }
	.hbars li { display: grid; grid-template-columns: 110px 1fr 64px; align-items: center; gap: 10px; font-size: 13px; }
	.hbars .lbl { font-weight: 600; }
	.hbars .track { height: 22px; background: #f1eee7; border-radius: 6px; overflow: hidden; }
	.hbars .fill { height: 100%; border-radius: 6px; }
	.hbars .val { text-align: right; font-weight: 700; }
	.note { font-size: 11.5px; color: var(--mute); margin: 10px 0 0; }
	.decisions { display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 14px; margin-bottom: 12px; }
	.decisions a { font-size: 11.5px; color: var(--mute); margin-left: 4px; }
	.decisions .tag { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; background: var(--ink); color: #fff; border-radius: 4px; padding: 2px 6px; margin-right: 6px; }
	.legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--mute); margin: 10px 0 12px; }
	.legend i, .dots i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: 0; }
	.tiles { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
	.tile { font: inherit; width: 100%; height: 100%; text-align: left; display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto; column-gap: 10px; align-items: center; background: #fff; border: 1px solid var(--rule); border-radius: 12px; padding: 8px 10px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s; }
	.tile:hover, .tile:focus-visible { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08); border-color: #bdb8ad; }
	.ini { grid-row: 1 / 3; width: 34px; height: 34px; border-radius: 50%; background: #2b2b2b; color: #fff; display: grid; place-items: center; font-weight: 700; font-size: 12.5px; letter-spacing: 0.5px; }
	.nm { font-weight: 700; font-size: 14px; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
	.nm .ln { display: none; }
	.pinmark { color: #da251d; font-size: 10px; }
	.sub { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--mute); white-space: nowrap; overflow: hidden; }
	.dots { display: inline-flex; gap: 2px; }
	.dots i { margin: 0; width: 7px; height: 7px; }
	.overlay { position: fixed; inset: 0; z-index: 50; background: rgba(20, 20, 20, 0.45); backdrop-filter: blur(3px); display: grid; place-items: center; padding: 16px; animation: fade 0.2s ease; }
	@keyframes fade { from { opacity: 0; } }
	.sheet { width: min(480px, 100%); max-height: calc(100vh - 32px); overflow-y: auto; }
	.sheetnav { display: flex; align-items: center; gap: 10px; color: #fff; font-size: 13px; margin-bottom: 8px; }
	.sheetnav button { font: inherit; font-size: 18px; width: 36px; height: 36px; border-radius: 50%; border: 0; background: rgba(255, 255, 255, 0.92); cursor: pointer; }
	.sheetnav button:disabled { opacity: 0.35; cursor: default; }
	.sheetnav .close { margin-left: auto; font-size: 15px; }
	.sheet :global(.card) { max-width: none; }
	@media (max-width: 900px) { .tiles { grid-template-columns: repeat(4, 1fr); } }
	@media (max-width: 600px) {
		.tiles { grid-template-columns: repeat(5, 1fr); gap: 6px; }
		.tile { grid-template-columns: 1fr; justify-items: center; text-align: center; padding: 8px 2px; row-gap: 4px; }
		.ini { grid-row: auto; width: 32px; height: 32px; font-size: 12px; }
		.nm { font-size: 11px; max-width: 100%; }
		.nm .full { display: none; } .nm .ln { display: inline; }
		.sub { font-size: 0; justify-content: center; }
		.meet .legend { gap: 8px; font-size: 11px; margin: 4px 0 8px; }
		.meet h2 { font-size: 24px; }
		.meet .lede { font-size: 15px; }
	}
	@media (prefers-reduced-motion: reduce) { .tile, .overlay { transition: none; animation: none; } }
	.also { list-style: none; padding: 0; margin: 12px 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 6px; font-size: 13px; }
	.also li { background: #fff; border: 1px solid var(--rule); border-radius: 10px; padding: 8px 10px; display: flex; flex-direction: column; gap: 2px; }
	.also b { font-size: 14px; }
	.also .meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: 11.5px; }
	.also .meta a, .also .none { color: var(--mute); }
	.src { font-size: 12px; }
	.exit { padding-bottom: 60px; }
	.mywalk { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 12px 14px; font-size: 14px; margin: 10px 0; }
	.cta { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0; }
	.cta a { font-size: 14px; font-weight: 600; border: 1.5px solid; border-radius: 999px; padding: 10px 16px; text-decoration: none; }
	.cta a:nth-child(1) { background: #2f5d9b; border-color: #2f5d9b; color: #fff; }
	.cta a:nth-child(2) { border-color: #d9822b; color: #a65d14; }
	.cta a:nth-child(3) { border-color: #4a8c5c; color: #356b45; }
	.vote3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; font-size: 14px; line-height: 1.4; }
	.vote3 div { background: #fff; border: 1px solid var(--rule); border-radius: 12px; padding: 10px 12px; }
	.vote3 b { display: block; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase; color: #da251d; margin-bottom: 2px; }
	.wardp { font-size: 15px; color: var(--ink-2); margin: 4px 0 8px; }
	.wardstop { padding-top: 20px; }
	.wardp a { font-size: 12px; color: var(--mute); }
	.method summary { cursor: pointer; }
	.hint { font-size: 12px; color: var(--mute); }
	.method { font-size: 12.5px; color: var(--mute); margin-top: 24px; line-height: 1.5; }
	@media (max-width: 600px) {
		.vote3 { grid-template-columns: 1fr; }
		.stepnav .full { display: none; }
		.charts { grid-template-columns: 1fr; }
		.hbars li { grid-template-columns: 84px 1fr 54px; }
	}
</style>
