<script lang="ts">
	// The Toronto journey (spec §11): a streetcar ride with stops for "Whose job is it?",
	// "What the mayor and council decide" (City Hall), every mayoral candidate in ballot order, and the exit.
	import { tick } from 'svelte';
	import '#lib/vote/vote.css';
	import Fact from '#lib/components/Fact.svelte';
	import SourceLine from '#lib/vote/SourceLine.svelte';
	import LineStreet from '#lib/vote/LineStreet.svelte';
	import WhoseJob from '#lib/vote/WhoseJob.svelte';
	import StoryCard from '#lib/vote/StoryCard.svelte';
	import Scenery from '#lib/vote/Scenery.svelte';
	import FallLeaves from '#lib/vote/FallLeaves.svelte';
	import SubwayTrain from '#lib/vote/SubwayTrain.svelte';
	import { TOPIC, TOPIC_COLOR } from '#lib/vote/topics.ts';
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
	// Stop 4: anyone with a link or a public record first, then 'no links'; ballot order within each group.
	const hasLinks = (c: { ballot_name: string; social: string[] }) => !!data.alsoRecords[c.ballot_name]?.[0] || c.social.length > 0;
	const withoutSorted = $derived([...without.filter(hasLinks), ...without.filter((c) => !hasLinks(c))]);

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
	// Stop 1: until the quiz is finished, Next stop reads 'Skip to next stop' so it isn't mistaken for Next question.
	let quizDone = $state(false);
	let whyOpen = $state(false);
	// Hop on: let the harbour slide past for a moment, then open Stop 1 (straight away with reduced motion).
	let departing = $state(false);
	function hopOn() {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches) return go(1);
		departing = true;
		// Stay 'departing' until the harbour has faded out, so it doesn't snap back to the start mid-fade.
		setTimeout(() => { go(1); setTimeout(() => (departing = false), 700); }, 1400);
	}
	// Keep the stop in the address bar so Back works and a stop can be shared.
	$effect(() => {
		const read = () => { const m = location.hash.match(/^#stop-(\d)$/); step = m ? Math.min(stops.length - 1, +m[1]) : 0; };
		read();
		addEventListener('hashchange', read);
		return () => removeEventListener('hashchange', read);
	});
	async function go(i: number) {
		const n = Math.max(0, Math.min(stops.length - 1, i));
		if (n === step) return;
		history.pushState(null, '', n ? `#stop-${n}` : location.pathname);
		step = n;
		// Every stop opens at its top. Jump (not smooth-scroll) once the new stop is on the page:
		// a smooth scroll started mid-swap gets cancelled on phones and leaves you at the bottom.
		await tick();
		scrollTo({ top: 0, behavior: 'instant' });
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
	// Colours people already link to each service: TTC red, police navy, asphalt grey, shelter brown.
	const bigBudgets = [
		{ id: 'toronto.ttc.2026.gross', label: 'TTC', color: '#da251d' },
		{ id: 'toronto.police.2026.gross', label: 'Police', color: '#1f3a68' },
		{ id: 'toronto.shelter.2026.gross', label: 'Shelters', color: '#8b5e3c' },
		{ id: 'toronto.transportation.2026.gross', label: 'Roads & traffic', color: '#6b7078' }
	].map((b) => ({ ...b, v: num(b.id) }));
	const bigMax = Math.max(...bigBudgets.map((b) => b.v));

	// Every candidate is a tile; tapping one opens their full story card on top of the page.
	let open = $state<number | null>(null);
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
	// Up to three pins, so the comparison box at the top of Stop 3 stays readable.
	const MAX_PINS = 3;
	let pinFull = $state(false);
	function togglePin(b: string) {
		if (!pins.includes(b) && pins.length >= MAX_PINS) { pinFull = true; return; }
		pinFull = false;
		pins = pins.includes(b) ? pins.filter((k) => k !== b) : [...pins, b];
		try { localStorage.setItem(PIN_KEY, JSON.stringify(pins)); } catch { /* blocked storage: pins last this visit */ }
	}

	let shared = $state('');
	let how = $state(false);
	async function share() {
		const text = "I walked through who's running for mayor of Toronto, and what the City actually controls. Election day is Monday, October 26.";
		const url = location.origin + '/vote/';
		try {
			if (navigator.share) return await navigator.share({ title: 'The Platform', text, url });
			await navigator.clipboard.writeText(`${text} ${url}`);
			shared = 'Link copied.';
		} catch { /* dismissed */ }
	}
</script>

<svelte:head>
	<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@500;700&family=VT323&display=swap" />
	<title>Who's running for mayor, and what the City controls · Toronto votes October 26 · The Platform</title>
	<meta name="description" content="Ride a streetcar through Toronto's mayoral race: what the City controls, what changed, and every candidate in their own words, with proof." />
	<meta property="og:title" content="The {headline} question" />
	<meta property="og:description" content="Toronto votes Monday, October 26. Meet every mayoral candidate in their own words, with every number linked to its proof." />
	<meta property="og:type" content="website" />
	<!-- Full addresses: some apps (iMessage, LinkedIn) won't load a preview image from a relative path. -->
	<meta property="og:site_name" content="The Platform" />
	<meta property="og:url" content="https://www.torontoyourvotecounts.space/vote/" />
	<meta property="og:image" content="https://www.torontoyourvotecounts.space/og-vote-2.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:image" content="https://www.torontoyourvotecounts.space/og-vote-2.png" />
</svelte:head>

<svelte:window onkeydown={onKey} />
<!-- The ride strip appears once you hop on; the opening screen has its own Hop on button. -->
{#if step > 0}
	<LineStreet {stops} {active} onjump={jump} />
{/if}
<Scenery {scene} {departing} />

{#key step}
<div class="screenwrap">
{#if step === 0}
<section class="hall wrap screen">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>The <span><Fact id="toronto.operating.2026.gross" plain /></span> question</h1>
	<p class="dek">
		The mayor and city council set Toronto's <Fact id="toronto.operating.2026.gross" /> yearly budget, which pays for things like the TTC, police, shelters and roads.
		On October 26 you pick who they are. This short ride shows what the City is in charge of, and who the {mayor.length} people running for mayor are, in their own words where they've published them.
	</p>
	<p class="proofnote sans">Every number and every quote links to its proof. Nothing here tells you who to vote for.</p>
	<div class="hoprow sans">
		<button class="hop" onclick={hopOn} disabled={departing}>Hop on →</button>
		<span class="howto">Six stops · about five minutes</span>
	</div>
</section>
{:else if step === 1}
<section class="stop wide quiz">
	<!-- Newspaper-style section flag: a rule, the section name, and room on the right for details. -->
	<h2 class="flag">Stop 1 · Whose job is it?</h2>
	<WhoseJob cards={data.whoseJob} bind:done={quizDone} />
</section>
{:else if step === 2}
<section class="stop wide cityhall">
	<p class="flag">Stop 2 · City Hall</p>
	<h2 class="head">What the mayor and council decide</h2>
	<p class="lede">Your property tax bill, and how the City's biggest budgets are split.</p>
	<div class="charts sans">
		<figure class="chart">
			<figcaption>The City tax bill on an average Toronto home</figcaption>
			<div class="stairs">
				{#each billYears as y, i (y.year)}
					<div class="step">
						<span class="val"><Fact id={y.bill} /></span>
						{#if i > 0}<span class="jump">+${(y.v - billYears[i - 1].v).toLocaleString('en-CA')}</span>{/if}
						<div class="bar" style="height:{(y.v / billMax) * 26}px"></div>
						<span class="yr">{y.year}</span>
						<span class="pc">up <Fact id={y.inc} plain /></span>
					</div>
				{/each}
			</div>
			<p class="note">Renters pay it too, inside their rent.</p>
		</figure>
		<figure class="chart">
			<figcaption>Four big City budgets, 2026</figcaption>
			<ul class="hbars">
				{#each bigBudgets as b (b.id)}
					<li style="--c:{b.color}">
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
		<!-- On phones this folds to its heading (tap to open) so the stop fits the screen; desktop always shows it. -->
		<div class="why tax-accent" class:shut={!whyOpen}>
			<b class="whyhead">Why it went up</b>
			<button class="whytoggle" aria-expanded={whyOpen} onclick={() => (whyOpen = !whyOpen)}>Why it went up <span aria-hidden="true">{whyOpen ? '−' : '+'}</span></button>
			<ul>
				<li><span>The gap:</span> going into 2024, the City needed <Fact id="toronto.budget.2024.opening-gap" /> more than it had, mostly for <span class="k shelter">shelter space</span> (including for refugee claimants) and because <span class="k ttc">TTC fare revenue</span> was down.</li>
				<li><span>The fix:</span> it found <Fact id="toronto.budget.2024.savings" /> in savings and offsets, got money from the Province and Ottawa, and raised <span class="k tax">property taxes</span>.</li>
				<li><span>Each of the last three years:</span> part of the increase is a <Fact id="toronto.city-building-levy.2024" plain /> City Building Fund levy: an extra slice of your property tax that the City saves only for building transit and housing.</li>
				<li><span>Who decides:</span> the mayor proposes each budget, and City Council votes on it. <a href={facts['toronto.budget.2024.opening-gap']?.primary.url} target="_blank" rel="noopener">proof ↗</a></li>
			</ul>
		</div>
		<p class="ttc-accent"><b>Your TTC fare</b> Fares are <Fact id="toronto.ttc.fares.2026" plain />, and rides are free after <Fact id="toronto.ttc.fare-cap.2026" plain /> paid trips in a month on the same PRESTO card, debit or credit card. <a href={facts['toronto.ttc.fares.2026']?.primary.url} target="_blank" rel="noopener">proof ↗</a></p>
	</div>
</section>
{:else if step === 3}
<section class="wide meet">
	<p class="flag">Stop 3 · The candidates</p>
	<h2 class="head">Everyone running for mayor</h2>
	<p class="lede sans meetlede"><b>Tap a candidate</b> to read what they say they'd do, in their own words. Pin up to 3 to compare them here.</p>
	{#if pins.length}
		<!-- Pinned candidates: a short summary of each, built only from their own published words. -->
		<div class="pinned sans" aria-label="Your pinned candidates">
			{#each pins as b (b)}
				{@const pr = profileOf(b)}
				{@const idx = withSite.findIndex((c) => c.ballot_name === b)}
				<div class="pcard">
					<div class="ptop"><b>{displayName(b)}</b><button class="unpin" onclick={() => togglePin(b)} aria-label="Unpin {displayName(b)}">×</button></div>
					<span class="pline">{firstLine(b)}{pr?.note ? ' · ended campaign' : ''}</span>
					{#if topicsOf(b).length}<span class="ptopics">Talks about: {#each topicsOf(b) as t (t)}<span class="chip" style="--tc:{TOPIC_COLOR[t]}">{TOPIC[t]}</span>{/each}</span>{/if}
					{#if pr?.priorities?.[0] && !pr.withheld}<q>{pr.priorities[0].text}</q><span class="pnote">First priority on their site</span>{/if}
					{#if idx >= 0}<button class="pmore" onclick={() => (open = idx)}>Read their full card →</button>{/if}
				</div>
			{/each}
		</div>
		<hr class="pindiv" />
	{/if}
	{#if pinFull}<p class="pinfull sans" role="status">You can pin up to 3. Unpin one to add another.</p>{/if}
	<!-- The colour key for the dots: which topics each candidate's own campaign site covers. -->
	<div class="legend sans"><span class="what">All {withSite.length} with a campaign website. Dots show the topics their site talks about:</span>{#each Object.entries(TOPIC) as [k, label] (k)}<span><i style="background:{TOPIC_COLOR[k as keyof typeof TOPIC]}"></i>{label}</span>{/each}</div>
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
<section class="stop wide alsostop">
	<p class="flag">Stop 4 · Also on your ballot</p>
	<h2 class="head">{without.length} more names you'll see</h2>
	<p class="lede sans">They didn't list a campaign website with the City. Here's what they did list, and any public record.</p>
	<ul class="also sans">
		{#each withoutSorted as c (c.ballot_name)}
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
	<p class="flag">Stop 5 · Your ward</p>
	<h2 class="head">Who's running in your ward?</h2>
	<p class="wardp sans">You also pick a city councillor and a school board trustee for your ward.
</p>
	<TorontoWardMap listUrl="https://www.toronto.ca/city-government/elections/candidate-list/" chartUrl={data.official?.school_chart.url ?? ''} races={data.races} guided={data.wards.filter((w) => w.scarborough).map((w) => w.ward)} />
</section>
{:else}
<section class="stop wide exit">
	<FallLeaves />
	{#if pins.length}
		<div class="mywalk sans"><b>You pinned:</b> {pins.map(displayName).join(' · ')}</div>
	{/if}
	<div class="platform">
		<div class="board" role="img" aria-label="Next train: Election Day, Monday October 26, 10 a.m. to 8 p.m.">
			<span class="lbl">Next train</span>
			<span class="dest">Election Day</span>
			<span class="when">Mon Oct 26 · 10:00–20:00</span>
		</div>
		<div class="tiles-wall">
			<!-- The station name on the wall, in subway lettering; the train runs past it, then the info appears. -->
			<div class="station"><span class="stopno-sub">Last stop · before you vote</span><h2><span class="visually-hidden">Before you vote: </span><span aria-hidden="true">VOTE</span></h2></div>
			<div class="panels sans">
				<div class="pnl"><b>On your ballot</b><span class="ballot"><i>Mayor</i><i>Councillor</i><i>School trustee</i></span></div>
				<div class="pnl"><b>You can vote if</b><span>You're a Canadian citizen, 18 or older, and live in Toronto (or own or rent property here). Students: vote where your home is.</span></div>
				<div class="pnl"><b>Bring</b><span>One ID with your name and Toronto address.</span></div>
			</div>
			<a class="where sans" href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Find where to vote ↗</a>
		</div>
		<div class="track" aria-hidden="true">
			<div class="edge"></div>
			<div class="pull"><SubwayTrain width={1100} cars={3} facing="right" /></div>
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
<!-- Back and Next sit right after each stop's content; stops are kept short enough that they show without scrolling. -->
<nav class="stepnav wide sans" aria-label="Move along the ride">
	<button class="back" onclick={() => go(step - 1)}>‹ Back</button>
	{#if step === 1 && !quizDone}
		<button class="fwd" onclick={() => go(step + 1)}>Skip to next stop <span aria-hidden="true">→</span></button>
	{:else if step < stops.length - 1}
		<button class="fwd" onclick={() => go(step + 1)}>Next stop<span class="dest">: {stops[step + 1].label.split(': ')[1]}</span> <span aria-hidden="true">→</span></button>
	{:else}
		<button class="fwd" onclick={share}>{shared || 'Share the ride ↗'}</button>
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
					pinsFull={pins.length >= MAX_PINS}
				/>
			{/key}
		</div>
	</div>
{/if}


<style>
	.screenwrap { padding-bottom: 20px; animation: slidein 0.45s cubic-bezier(0.2, 0.8, 0.2, 1); }
	@keyframes slidein { from { opacity: 0; transform: translateX(30px); } }
	.hall { margin-top: 8vh; }
	.hoprow { display: flex; align-items: center; flex-wrap: wrap; gap: 10px 18px; margin-top: 22px; }
	.hop { font-family: var(--sans); font-weight: 700; font-size: 17px; background: var(--red); color: #fff; border: var(--line); border-radius: 999px; padding: 12px 26px; cursor: pointer; box-shadow: var(--pop); transition: transform 0.15s, box-shadow 0.15s; }
	.hop:hover { transform: translate(-2px, -2px); box-shadow: var(--pop-lg); }
	.howto { font-size: 13.5px; color: var(--mute); }
	/* Titles like the Glossary: a small red label, then a big serif headline. */
	.head { display: flex; flex-direction: column; gap: 2px; font-size: clamp(30px, 4.2vw, 42px); line-height: 1.08; margin: 2px 0 6px; }
	.flag, h2.flag, .quiz h2.flag { display: flex; justify-content: space-between; align-items: baseline; margin: 8px 0 4px; font-family: var(--sans); font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--ink); line-height: 1.3; }

	.kicker { color: var(--red); }
	h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.1; margin: 10px 0 14px; }
	h1 span { color: var(--red); }
	h2 { font-size: clamp(26px, 3.4vw, 34px); margin: 4px 0 6px; }
	.dek { font-size: 20px; line-height: 1.45; color: var(--ink-2); margin: 0; }
	.lede { font-size: 15.5px; line-height: 1.45; color: var(--ink-2); margin: 0 0 4px; }
	.proofnote { font-size: 13px; color: var(--mute); margin: 12px 0 0; }
	.stop { padding-top: 6px; }
	.quiz h2 { font-size: clamp(24px, 3.5vw, 30px); margin: 0 0 4px; }
	@media (max-width: 600px) {
		.quiz { padding-top: 6px; }
		/* Phones: a tighter opening so the proof line and Hop on sit clear of the skyline below. */
		.hall { margin-top: 18px; position: relative; z-index: 1; }
		.hall h1 { font-size: 36px; margin: 6px 0 10px; }
		.dek { font-size: 17px; line-height: 1.5; }
		.proofnote { font-size: 13px; margin-top: 10px; }
		.hoprow { margin-top: 16px; }
	}
	@media (prefers-reduced-motion: reduce) { .screenwrap { animation: none; } }
	.meet { padding-top: 0; }
	.meet .legend { margin: 2px 0 12px; gap: 14px; align-items: center; }
	.legend .what { color: var(--ink-2); font-weight: 600; margin-right: 6px; }
	.who { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-top: 0; }
	.who .why { font-size: 13px; line-height: 1.35; color: var(--ink-2); background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 7px 14px; }
	.why ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
	.why li span { font-weight: 700; color: var(--ink); }
	/* Same colour for the same topic everywhere on this stop: tax orange, TTC red, shelters brown. */
	.why .k { font-weight: 600; border-bottom: 2px solid; }
	.why .k.tax { color: #a65d14; border-color: #d9822b; }
	.why .k.ttc { color: #b51d17; border-color: #da251d; }
	.why .k.shelter { color: #7a5032; border-color: #8b5e3c; }
	.who .tax-accent { border-left: 5px solid #d9822b; }
	.who .tax-accent > b { color: #a65d14; }
	.who .ttc-accent { border-left: 5px solid #da251d; }
	.who .ttc-accent b { color: #da251d; }
	.who p { margin: 0; font-size: 13.5px; line-height: 1.4; color: var(--ink-2); background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 7px 14px; }
	.who b, .why > b { display: block; font-size: 10.5px; letter-spacing: 1.4px; text-transform: uppercase; color: #da251d; margin-bottom: 2px; }
	.who a { font-size: 12px; color: var(--mute); margin-left: 4px; }
	.charts { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; margin: 2px 0 8px; }
	.chart { margin: 0; background: #fff; border: 1px solid var(--rule); border-radius: 16px; padding: 12px 16px 8px; }
	figcaption { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
	.stairs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; align-items: end; }
	.step { display: flex; flex-direction: column; justify-content: flex-end; align-items: center; }
	.step .bar { width: 70%; background: linear-gradient(#e89a4e, #d9822b); border-radius: 8px 8px 0 0; min-height: 8px; }
	.step .val { font-family: var(--display); font-weight: 700; font-size: 20px; margin-bottom: 4px; }
	.step .jump { font-size: 11px; font-weight: 700; color: #a65d14; background: #fbefe2; border-radius: 999px; padding: 1px 7px; margin-bottom: 4px; }
	.step .yr { font-size: 12px; font-weight: 700; margin-top: 4px; }
	.step .pc { font-size: 11px; color: var(--mute); }
	.hbars { list-style: none; padding: 0; margin: 4px 0 0; display: grid; gap: 10px; }
	.hbars li { display: grid; grid-template-columns: 110px 1fr 64px; align-items: center; gap: 10px; font-size: 13px; }
	.hbars .lbl { font-weight: 600; }
	.hbars .track { height: 18px; background: #f1eee7; border-radius: 6px; overflow: hidden; }
	.hbars .fill { height: 100%; border-radius: 6px; }
	.hbars .val { text-align: right; font-weight: 700; }
	/* Each amount takes its bar's colour. */
	.hbars .val :global(.value) { color: var(--c); border-bottom-color: var(--c); }
	.note { font-size: 11.5px; color: var(--mute); margin: 10px 0 0; }
	.legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: var(--mute); margin: 10px 0 12px; }
	.legend i, .dots i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; vertical-align: 0; }
	.tiles { list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(5, 1fr); grid-auto-rows: 1fr; gap: 8px 14px; }
	.tile { font: inherit; width: 100%; height: 100%; text-align: left; display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto; column-gap: 10px; row-gap: 3px; align-items: center; background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 5px 12px; cursor: pointer; transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s; }
	.tile:hover, .tile:focus-visible { transform: translate(-2px, -2px); box-shadow: var(--pop); border-color: var(--ink); }
	.ini { grid-row: 1 / 3; width: 34px; height: 34px; border-radius: 50%; background: #2b2b2b; color: #fff; display: grid; place-items: center; font-weight: 700; font-size: 12.5px; letter-spacing: 0.5px; }
	.nm { font-weight: 700; font-size: 15.5px; line-height: 1.2; }
	.nm .ln { display: none; }
	.pinmark { color: #da251d; font-size: 10px; }
	.meetlede { margin: 4px 0 14px; }
	.pinned { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 4px 0 0; }
	.pcard { display: flex; flex-direction: column; gap: 6px; background: #fff; border: 1px solid var(--rule); border-top: 3px solid var(--ink); border-radius: 12px; padding: 12px 14px; font-size: 13.5px; }
	.ptop { display: flex; justify-content: space-between; align-items: start; gap: 8px; }
	.ptop b { font-size: 16px; line-height: 1.25; }
	.unpin { border: 0; background: none; font-size: 20px; line-height: 1; color: var(--mute); cursor: pointer; padding: 0 2px; }
	.pline { color: var(--mute); font-size: 12.5px; }
	.ptopics { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; color: var(--ink-2); font-size: 12.5px; }
	.chip { font-size: 11.5px; font-weight: 600; color: #fff; background: var(--tc); border-radius: 999px; padding: 1px 8px; }
	.pcard q { font-family: var(--serif); font-size: 14.5px; line-height: 1.45; color: var(--ink); }
	.pnote { font-size: 11px; color: var(--mute); margin-top: -4px; }
	.pmore { align-self: flex-start; font: inherit; font-size: 13px; font-weight: 600; background: none; border: 0; padding: 2px 0; color: var(--ink); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; margin-top: auto; }
	.pindiv { border: 0; border-top: 1px solid var(--rule); margin: 18px 0 14px; }
	.pinfull { font-size: 13px; color: #b5631a; margin: 0 0 8px; }
	@media (max-width: 600px) { .pinned { grid-template-columns: 1fr; gap: 8px; } .pcard { padding: 10px 12px; } }
	.sub { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--mute); white-space: nowrap; overflow: hidden; }
	.dots { display: inline-flex; gap: 2px; }
	.dots i { margin: 0; width: 7px; height: 7px; }
	.overlay { position: fixed; inset: 0; z-index: 50; background: rgba(20, 20, 20, 0.45); backdrop-filter: blur(3px); display: grid; place-items: center; padding: 16px; animation: fade 0.2s ease; }
	@keyframes fade { from { opacity: 0; } }
	/* The card always fits the screen: header and Back/Next stay put, only the quotes scroll inside. */
	/* One fixed size for every candidate and every panel, so the card never jumps; long panels scroll inside. */
	.sheet { width: min(520px, 100%); height: min(500px, calc(100dvh - 32px)); display: flex; flex-direction: column; }
	.sheet :global(.card) { flex: 1; min-height: 0; max-height: none; }
	.sheetnav { display: flex; align-items: center; gap: 10px; color: #fff; font-size: 13px; margin-bottom: 8px; }
	.sheetnav button { font: inherit; font-size: 18px; width: 36px; height: 36px; border-radius: 50%; border: 0; background: rgba(255, 255, 255, 0.92); cursor: pointer; }
	.sheetnav button:disabled { opacity: 0.35; cursor: default; }
	.sheetnav .close { margin-left: auto; font-size: 15px; }
	.sheet :global(.card) { max-width: none; width: 100%; margin: 0; }
	@media (max-width: 900px) { .tiles { grid-template-columns: repeat(4, 1fr); } }
	@media (max-width: 600px) {
		/* Three per row on phones, so names have room and nothing touches the card edge. */
		.tiles { grid-template-columns: repeat(3, 1fr); gap: 10px; }
		.tile { grid-template-columns: 1fr; justify-items: center; text-align: center; padding: 12px 6px; row-gap: 5px; }
		.ini { grid-row: auto; width: 32px; height: 32px; font-size: 12px; }
		.nm { font-size: 13px; max-width: 100%; }
		.nm .full { display: none; } .nm .ln { display: inline; }
		.sub { font-size: 0; justify-content: center; }
		.meet .legend { gap: 6px 12px; font-size: 12px; margin: 6px 0 14px; }
		.legend .what { flex-basis: 100%; }
		.meet h2 { font-size: 24px; }
	}
	@media (prefers-reduced-motion: reduce) { .tile, .overlay { transition: none; animation: none; } }
	/* A tidy roll call: name, then whatever they listed, one even row each. */
	.also { list-style: none; padding: 0; margin: 16px 0 12px; columns: 4; column-gap: 28px; font-size: 13px; }
	.also li { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0 8px; padding: 7px 0; border-bottom: 1px solid var(--rule); min-width: 0; break-inside: avoid; }
	.also b { font-size: 14.5px; line-height: 1.3; }
	.also .meta { display: flex; flex-wrap: wrap; gap: 0 7px; font-size: 12px; }
	@media (max-width: 860px) { .also { columns: 2; } }
	@media (max-width: 600px) { .also { columns: 2; column-gap: 18px; } .also li { padding: 8px 0; } .also b { font-size: 14px; } .also .meta { font-size: 12px; } }
	.whytoggle { display: none; }
	@media (max-width: 600px) {
		.whyhead { display: none !important; }
		.whytoggle { display: flex; justify-content: space-between; width: 100%; font: inherit; font-size: 11px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; color: #da251d; background: none; border: 0; padding: 4px 0; cursor: pointer; }
		.whytoggle span { font-size: 18px; line-height: 1; }
		.why.shut ul { display: none; }
	}
	.also .meta a, .also .none { color: var(--mute); }
	.src { font-size: 12px; margin: 16px 0 0; }
	.exit { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; padding-top: 18px; }
	.exit .method { margin-top: 14px; }
	.exit .more { justify-content: center; }
	/* Last stop as a TTC platform: amber arrival board, cream Vitrolite tiles, the station name on
	   a black band in Toronto-Subway-style capitals (Jost stands in for the TTC's own face). */
	.platform { width: 100%; max-width: 820px; border-radius: 14px; overflow: hidden; border: var(--line); box-shadow: var(--pop-lg); }
	.track { position: relative; height: 104px; background: linear-gradient(#3b3f45, #23262a); overflow: hidden; }
	.edge { height: 12px; background: repeating-linear-gradient(90deg, #f2c230 0 14px, #e0b020 14px 16px); box-shadow: 0 2px 0 #9c7d14; }
	/* The train zooms through left to right without stopping and is gone (it ends past the right edge). */
	.pull { position: absolute; bottom: 6px; right: 16px; animation: zoom 1.3s cubic-bezier(0.45, 0, 0.55, 1) 0.1s both; }
	@keyframes zoom { from { transform: translateX(-200%); } to { transform: translateX(110%); } }
	/* As it passes, the info boards light up. */
	.platform .panels, .platform .where { animation: board 0.5s ease-out 1.6s both; }
	.platform .where { animation-delay: 2s; }
	@keyframes board { from { opacity: 0; transform: translateY(10px); } }
	@media (prefers-reduced-motion: reduce) {
		.pull { animation: none; }
		.platform .panels, .platform .where { animation: none; }
	}
	.board { display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap; background: #0d0d0f; border-radius: 10px 10px 0 0; padding: 9px 18px; font-family: 'VT323', ui-monospace, monospace; color: #ffb43a; text-shadow: 0 0 6px rgba(255, 170, 40, 0.6); font-size: 22px; line-height: 1; }
	.board .lbl { color: #ffd48a; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }
	.board .dest { font-size: 27px; text-transform: uppercase; }
	.board .when { margin-left: auto; }
	.tiles-wall { background-color: #efe6c8; background-image: linear-gradient(rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0) 60%), linear-gradient(#d9cda4 2px, transparent 2px), linear-gradient(90deg, #d9cda4 2px, transparent 2px); background-size: 100% 100%, 90px 45px, 90px 45px; padding: 0 0 22px; text-align: center; }
	.station { padding: 12px 20px 0; }
	.station h2 { font-family: 'Jost', var(--sans); font-weight: 700; letter-spacing: 0.22em; text-indent: 0.22em; margin: 0; font-size: clamp(48px, 7vw, 76px); line-height: 1; color: #1b1b1b; }
	.stopno-sub { font-family: 'Jost', var(--sans); font-size: 12px; letter-spacing: 4px; text-transform: uppercase; color: #8a7a45; }
	.panels { display: grid; grid-template-columns: 1fr 1.4fr 1fr; gap: 12px; padding: 14px 22px 0; text-align: left; }
	.pnl { background: rgba(255, 255, 255, 0.92); border-radius: 10px; padding: 10px 12px; font-size: 14px; line-height: 1.45; display: flex; flex-direction: column; gap: 6px; border: 1px solid #d9cda4; }
	.pnl b { font-family: 'Jost', var(--sans); font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #da251d; }
	.ballot { display: flex; flex-wrap: wrap; gap: 6px; }
	.ballot i { font-style: normal; font-weight: 600; font-size: 13px; border: 1.5px solid var(--ink); border-radius: 6px; padding: 2px 9px; }
	.where { display: inline-block; margin-top: 14px; background: #da251d; color: #fff; text-decoration: none; font-weight: 700; font-size: 16px; border-radius: 999px; padding: 12px 26px; border: var(--line); box-shadow: var(--pop); }
	@media (max-width: 700px) {
		.board { font-size: 20px; gap: 6px 12px; padding: 10px 14px; } .board .dest { font-size: 24px; } .board .when { margin-left: 0; }
		.station h2 { font-size: 64px; }
		.panels { grid-template-columns: 1fr; padding: 14px 12px 0; gap: 8px; }
		.pnl { padding: 9px 12px; font-size: 13.5px; }
		.track { height: 80px; } .pull :global(svg) { width: 800px; }
		.where { margin-top: 18px; }
	}

	.mywalk { background: #fff; border: var(--line); border-radius: 14px; padding: 9px 14px; font-size: 14px; margin: 10px 0; }
	.wardp { font-size: 15px; color: var(--ink-2); margin: 8px 0 0; }
	.wardstop { padding-top: 20px; }
	.ballot { display: flex; flex-wrap: wrap; gap: 6px; }
	.ballot i { font-style: normal; font-weight: 600; font-size: 13px; border: 1.5px solid var(--ink); border-radius: 6px; padding: 2px 9px; }
	.more { display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 13px; margin: 14px 0 0; }
	.more a, .how { color: var(--ink-2); }
	.how { font: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; text-underline-offset: 2px; }
	.exit .method { max-width: 860px; text-align: center; }
	@media (max-width: 600px) {
						.exit { min-height: 0; }
						}
	.stepnav { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding-top: 0; padding-bottom: 18px; }
	.back, .fwd { font: inherit; font-weight: 700; font-size: 14.5px; border-radius: 999px; padding: 9px 18px; cursor: pointer; white-space: nowrap; }
	.back { background: #fff; border: 1px solid color-mix(in srgb, var(--ink) 25%, transparent); color: var(--ink-2); }
	.back:hover { color: var(--ink); border-color: var(--ink); }
	.fwd { background: var(--red); color: #fff; border: 1.5px solid var(--ink); box-shadow: 2px 2px 0 var(--ink); }
	.fwd:hover { box-shadow: var(--pop); transform: translate(-1px, -1px); }
	.method { font-size: 12.5px; color: var(--mute); margin-top: 24px; line-height: 1.5; }
	@media (max-width: 600px) {
		.screenwrap { padding-bottom: 12px; }
		.charts { grid-template-columns: 1fr; }
		.who { grid-template-columns: 1fr; gap: 14px; }
		.who .why { font-size: 14px; line-height: 1.5; padding: 12px 14px; }
		.why ul { gap: 8px; }
		.dest { display: none; }
		.stepnav { padding-top: 8px; }
		.hbars li { grid-template-columns: 84px 1fr 54px; }
	}
</style>
