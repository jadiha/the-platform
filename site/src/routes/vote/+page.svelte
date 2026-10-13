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
	import FallLeaves from '#lib/vote/FallLeaves.svelte';
	import SubwayTrain from '#lib/vote/SubwayTrain.svelte';
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
	let how = $state(false);
	async function share() {
		const text = "I walked through who's running for mayor of Toronto, and what the City actually controls. Election day is Monday, October 26.";
		const url = location.origin + '/vote/';
		try {
			if (navigator.share) return await navigator.share({ title: 'The 6ix Votes', text, url });
			await navigator.clipboard.writeText(`${text} ${url}`);
			shared = 'Link copied.';
		} catch { /* dismissed */ }
	}
</script>

<svelte:head>
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@500;700&family=VT323&display=swap" />
	<title>Who's running for mayor, and what the City controls · Toronto votes October 26 · The 6ix Votes</title>
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
	<div class="hoprow sans">
		<button class="hop" onclick={() => go(1)}>Hop on →</button>
		<span class="howto">Six stops · about five minutes</span>
	</div>
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
						<div class="bar" style="height:{(y.v / billMax) * 70}px"></div>
						<span class="yr">{y.year}</span>
						<span class="pc">up <Fact id={y.inc} plain /></span>
					</div>
				{/each}
			</div>
			<p class="note">Renters pay it too, inside their rent.</p>
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
	<div class="who sans">
		<div class="why"><b>Why it went up</b>
			<ul>
				<li><span>The gap:</span> going into 2024, the City needed <Fact id="toronto.budget.2024.opening-gap" /> more than it had, mostly for shelter space (including for refugee claimants) and because TTC fare revenue was down.</li>
				<li><span>The fix:</span> it found <Fact id="toronto.budget.2024.savings" /> in savings and offsets, and raised property taxes for much of the rest.</li>
				<li><span>Every year:</span> part of the increase is a <Fact id="toronto.city-building-levy.2024" plain /> City Building Fund levy, set aside for transit and housing.</li>
				<li><span>Who decides:</span> the mayor proposes each budget, and City Council votes on it. <a href={facts['toronto.budget.2024.opening-gap']?.primary.url} target="_blank" rel="noopener">proof ↗</a></li>
			</ul>
		</div>
		<p><b>Your TTC fare</b> Fares are <Fact id="toronto.ttc.fares.2026" plain />, and rides are free after <Fact id="toronto.ttc.fare-cap.2026" plain /> paid trips in a month. <a href={facts['toronto.ttc.fares.2026']?.primary.url} target="_blank" rel="noopener">proof ↗</a></p>
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
<section class="stop wide alsostop" style="padding-top:20px">
	<h2 class="head"><span class="stopno sans">Stop 4 · Also on your ballot</span>{without.length} more names you'll see</h2>
	<p class="lede sans">They didn't list a campaign website with the City. Here's what they did list, and any public record.</p>
	<ul class="also sans">
		{#each without as c (c.ballot_name)}
			{@const rec = data.alsoRecords[c.ballot_name]?.[0]}
			<li>
				<b>{displayName(c.ballot_name)}</b>
				<span class="meta">
					{#if rec}<a href={data.recordSources[rec.src]?.url} target="_blank" rel="noopener">ran in 2023</a>{/if}
					{#each c.social as s (s)}<a href={s} target="_blank" rel="noopener">{s.replace(/^https?:\/\/(www\.)?/, '').split('/')[0].replace('.com', '')}</a>{/each}
					{#if !rec && !c.social.length}<span class="none">no links</span>{/if}
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
	<FallLeaves />
	{#if pins.length}
		<div class="mywalk sans"><b>You pinned:</b> {pins.map(displayName).join(' · ')}<br /><span class="hint">Pins stay in this browser. Nothing is sent anywhere.</span></div>
	{/if}
	<div class="platform">
		<div class="board" role="img" aria-label="Next train: Election Day, Monday October 26, 10 a.m. to 8 p.m.">
			<span class="lbl">Next train</span>
			<span class="dest">Election Day</span>
			<span class="when">Mon Oct 26 · 10:00–20:00</span>
		</div>
		<div class="tiles-wall">
			<div class="band"><span class="stopno-sub">Stop 6 · Last stop</span><h2>Before you vote</h2></div>
			<div class="panels sans">
				<div class="pnl"><b>On your ballot</b><span class="ballot"><i>Mayor</i><i>Councillor</i><i>School trustee</i></span></div>
				<div class="pnl"><b>You can vote if</b><span>You're a Canadian citizen, 18 or older, and live in Toronto (or own or rent property here). Students: vote where your home is.</span></div>
				<div class="pnl"><b>Bring</b><span>One ID with your name and Toronto address.</span></div>
			</div>
			<a class="where sans" href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Find where to vote ↗</a>
		</div>
		<div class="track" aria-hidden="true">
			<div class="edge"></div>
			<div class="pull"><SubwayTrain width={760} cars={3} /></div>
		</div>
	</div>
	<p class="more sans">
		<a href="https://www.toronto.ca/city-government/elections/voter-information/who-can-vote/" target="_blank" rel="noopener">Full voting rules ↗</a>
		<a href="/vote/mayor/">All {mayor.length} mayoral candidates</a>
		<button class="how" aria-expanded={how} onclick={() => (how = !how)}>How we made this {how ? '−' : '+'}</button>
	</p>
	{#if how}<p class="method sans">On {data.scan?.date ? new Date(data.scan.date).toLocaleDateString('en-CA', { month: 'long', day: 'numeric', timeZone: 'UTC' }) : 'October 13'}, we read every mayoral campaign website on the City Clerk's certified candidate list. Quotes are copied word for word and link to the exact sentence on the candidate's own site, with a saved copy. Past results come from the City's official declaration. Councillor and school trustee candidates come from the City Clerk's certified list. We don't use news reports or opponents' claims, and we don't predict what any promise would do.
		Spotted a mistake? <a href="/sources/#corrections">Tell us</a>. An independent, non-partisan community project, not affiliated with any government, party or candidate.</p>{/if}
</section>
{/if}
</div>
{/key}
{#if step > 0}
<nav class="stepnav wide sans" aria-label="Move along the ride">
	<button class="back" onclick={() => go(step - 1)}>‹ Back</button>
	<span class="gap"></span>
	{#if step < stops.length - 1}
		<button class="fwd" onclick={() => go(step + 1)}>Next stop<span class="full">: {stops[step + 1].label.split(': ')[1]}</span> →</button>
	{:else}
		<span class="hint">{shared}</span>
		<button class="fwd" onclick={share}>Share the ride ↗</button>
	{/if}
</nav>
{/if}

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
	.screenwrap { min-height: calc(100vh - 200px); padding-bottom: 96px; animation: slidein 0.45s cubic-bezier(0.2, 0.8, 0.2, 1); }
	@keyframes slidein { from { opacity: 0; transform: translateX(30px); } }
	.hall { margin-top: 8vh; }
	.hoprow { display: flex; align-items: center; flex-wrap: wrap; gap: 10px 18px; margin-top: 22px; }
	.hop { font-family: var(--sans); font-weight: 700; font-size: 17px; background: #da251d; color: #fff; border: 0; border-radius: 999px; padding: 13px 26px; cursor: pointer; }
	.howto { font-size: 13.5px; color: var(--mute); }
	/* Back and Next float in the same spot on every stop (no bar behind them). */
	.stepnav { position: fixed; left: 0; right: 0; bottom: 20px; z-index: 8; display: flex; align-items: center; gap: 16px; pointer-events: none; }
	.stepnav > * { pointer-events: auto; }
	.stepnav .gap { flex: 1; }
	.stepnav button { font: inherit; font-weight: 700; font-size: 15px; border-radius: 999px; padding: 11px 18px; cursor: pointer; }
	.stepnav .back { background: color-mix(in srgb, var(--paper) 90%, transparent); backdrop-filter: blur(4px); border: 1px solid var(--rule); padding: 10px 16px; color: var(--ink-2); font-weight: 600; }
	.stepnav .back:hover { color: var(--ink); }
	.stepnav .back:disabled { opacity: 0.3; cursor: default; }
	.stepnav .fwd { background: #da251d; color: #fff; border: 0; box-shadow: 0 8px 20px rgba(218, 37, 29, 0.3); }
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
	.meet .legend { margin: 8px 0 18px; gap: 16px; }
	.who { display: grid; grid-template-columns: 1.7fr 1fr; gap: 10px; margin-top: 2px; }
	.who .why { font-size: 13.5px; line-height: 1.4; color: var(--ink-2); background: #fff; border: 1px solid var(--rule); border-radius: 12px; padding: 10px 14px; }
	.why ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 3px; }
	.why li span { font-weight: 700; color: var(--ink); }
	.who p { margin: 0; font-size: 14px; line-height: 1.45; color: var(--ink-2); background: #fff; border: 1px solid var(--rule); border-radius: 12px; padding: 10px 14px; }
	.who b, .why > b { display: block; font-size: 10.5px; letter-spacing: 1.4px; text-transform: uppercase; color: #da251d; margin-bottom: 2px; }
	.who a { font-size: 12px; color: var(--mute); margin-left: 4px; }
	.charts { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; margin: 10px 0 10px; }
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
	.legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--mute); margin: 10px 0 12px; }
	.legend i, .dots i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: 0; }
	.tiles { list-style: none; padding: 0; margin: 4px 0 0; display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px 14px; }
	.tile { font: inherit; width: 100%; height: 100%; text-align: left; display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto; column-gap: 12px; row-gap: 3px; align-items: center; background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 9px 14px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s; }
	.tile:hover, .tile:focus-visible { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08); border-color: #bdb8ad; }
	.ini { grid-row: 1 / 3; width: 34px; height: 34px; border-radius: 50%; background: #2b2b2b; color: #fff; display: grid; place-items: center; font-weight: 700; font-size: 12.5px; letter-spacing: 0.5px; }
	.nm { font-weight: 700; font-size: 14px; line-height: 1.2; }
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
	.also { list-style: none; padding: 0; margin: 10px 0 6px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px 8px; font-size: 13px; }
	.also li { background: #fff; border: 1px solid var(--rule); border-radius: 10px; padding: 4px 10px; display: flex; flex-direction: column; gap: 0; min-width: 0; }
	.also b { font-size: 13.5px; }
	.also .meta { display: flex; flex-wrap: wrap; gap: 0 7px; font-size: 11px; }
	@media (max-width: 900px) { .also { grid-template-columns: repeat(2, 1fr); } }
	@media (max-width: 600px) { .also { grid-template-columns: repeat(3, 1fr); gap: 4px; } .also li { padding: 4px 6px; } .also b { font-size: 11.5px; line-height: 1.2; } .also .meta { font-size: 9.5px; gap: 0 5px; } .alsostop { padding-top: 16px; } .alsostop .lede { font-size: 13px; margin: 0; } .alsostop h2 { font-size: 22px; } .alsostop .src { margin: 0; } }
	.also .meta a, .also .none { color: var(--mute); }
	.src { font-size: 12px; }
	.exit { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; min-height: calc(100vh - 300px); justify-content: center; padding-top: 8px; }
	.exit .method { margin-top: 14px; }
	.exit .more { justify-content: center; }
	/* Last stop as a TTC platform: amber arrival board, cream Vitrolite tiles, the station name on
	   a black band in Toronto-Subway-style capitals (Jost stands in for the TTC's own face). */
	.platform { width: 100%; max-width: 1000px; border-radius: 14px; overflow: hidden; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.14); }
	.track { position: relative; height: 92px; background: linear-gradient(#3b3f45, #23262a); overflow: hidden; }
	.edge { height: 12px; background: repeating-linear-gradient(90deg, #f2c230 0 14px, #e0b020 14px 16px); box-shadow: 0 2px 0 #9c7d14; }
	.pull { position: absolute; left: 50%; bottom: 6px; transform: translateX(-50%); animation: arrive 2.2s cubic-bezier(0.15, 0.7, 0.25, 1) both; }
	@keyframes arrive { from { transform: translateX(60%); } to { transform: translateX(-50%); } }
	@media (prefers-reduced-motion: reduce) { .pull { animation: none; } }
	.board { display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap; background: #0d0d0f; border-radius: 10px 10px 0 0; padding: 12px 22px; font-family: 'VT323', ui-monospace, monospace; color: #ffb43a; text-shadow: 0 0 6px rgba(255, 170, 40, 0.6); font-size: 26px; line-height: 1; }
	.board .lbl { color: #ffd48a; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
	.board .dest { font-size: 32px; text-transform: uppercase; }
	.board .when { margin-left: auto; }
	.tiles-wall { background-color: #efe6c8; background-image: linear-gradient(rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0) 60%), linear-gradient(#d9cda4 2px, transparent 2px), linear-gradient(90deg, #d9cda4 2px, transparent 2px); background-size: 100% 100%, 90px 45px, 90px 45px; padding: 0 0 30px; text-align: center; }
	.band { background: #141414; color: #fff; padding: 14px 20px 16px; border-top: 6px solid #b8a46a; border-bottom: 6px solid #b8a46a; }
	.band h2 { font-family: 'Jost', var(--sans); font-weight: 700; text-transform: uppercase; letter-spacing: 6px; margin: 2px 0 0; font-size: clamp(28px, 5vw, 52px); color: #fff; }
	.stopno-sub { font-family: 'Jost', var(--sans); font-size: 12px; letter-spacing: 4px; text-transform: uppercase; color: #b8a46a; }
	.panels { display: grid; grid-template-columns: 1fr 1.4fr 1fr; gap: 14px; padding: 28px 30px 0; text-align: left; }
	.pnl { background: rgba(255, 255, 255, 0.92); border-radius: 10px; padding: 12px 14px; font-size: 14.5px; line-height: 1.45; display: flex; flex-direction: column; gap: 6px; border: 1px solid #d9cda4; }
	.pnl b { font-family: 'Jost', var(--sans); font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #da251d; }
	.ballot { display: flex; flex-wrap: wrap; gap: 6px; }
	.ballot i { font-style: normal; font-weight: 600; font-size: 13px; border: 1.5px solid var(--ink); border-radius: 6px; padding: 2px 9px; }
	.where { display: inline-block; margin-top: 30px; background: #da251d; color: #fff; text-decoration: none; font-weight: 700; font-size: 16px; border-radius: 999px; padding: 12px 26px; box-shadow: 0 6px 16px rgba(218, 37, 29, 0.3); }
	@media (max-width: 700px) {
		.board { font-size: 20px; gap: 6px 12px; padding: 10px 14px; } .board .dest { font-size: 24px; } .board .when { margin-left: 0; }
		.band h2 { letter-spacing: 3px; }
		.panels { grid-template-columns: 1fr; padding: 14px 12px 0; gap: 8px; }
		.pnl { padding: 9px 12px; font-size: 13.5px; }
		.track { height: 56px; } .pull :global(svg) { width: 440px; }
		.where { margin-top: 18px; }
	}

	.mywalk { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 9px 14px; font-size: 14px; margin: 10px 0; }
	.wardp { font-size: 15px; color: var(--ink-2); margin: 8px 0 0; }
	.wardstop { padding-top: 20px; }
	.wardp a { font-size: 12px; color: var(--mute); }
	.ballot { display: flex; flex-wrap: wrap; gap: 6px; }
	.ballot i { font-style: normal; font-weight: 600; font-size: 13px; border: 1.5px solid var(--ink); border-radius: 6px; padding: 2px 9px; }
	.more { display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 13px; margin: 14px 0 0; }
	.more a, .how { color: var(--ink-2); }
	.how { font: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; text-underline-offset: 2px; }
	.exit .method { max-width: 860px; text-align: center; }
	@media (max-width: 600px) {
						.exit { min-height: 0; }
						}
	.hint { font-size: 12px; color: var(--mute); }
	.method { font-size: 12.5px; color: var(--mute); margin-top: 24px; line-height: 1.5; }
	@media (max-width: 600px) {
			.stepnav .full { display: none; }
		.stepnav { bottom: 12px; }
		.screenwrap { padding-bottom: 80px; }
		.charts { grid-template-columns: 1fr; }
		.who { grid-template-columns: 1fr; }
		.hbars li { grid-template-columns: 84px 1fr 54px; }
	}
</style>
