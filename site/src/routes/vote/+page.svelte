<script lang="ts">
	// The Toronto walk (spec §11): a Line 2 street with stops for "Whose job is it?",
	// "Did it change anything?" (City Hall), every mayoral candidate in ballot order, and the exit.
	import '#lib/vote/vote.css';
	import Fact from '#lib/components/Fact.svelte';
	import SourceLine from '#lib/vote/SourceLine.svelte';
	import LineStreet from '#lib/vote/LineStreet.svelte';
	import WhoseJob from '#lib/vote/WhoseJob.svelte';
	import StoryCard from '#lib/vote/StoryCard.svelte';
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

	const stops = $derived([
		{ label: 'Start: whose job is it?', big: true },
		{ label: 'City Hall: did it change anything?', big: true },
		...withSite.map((c) => ({ label: displayName(c.ballot_name), big: false })),
		{ label: 'Also on your ballot', big: true },
		{ label: 'Kennedy: before you vote', big: true }
	]);
	let active = $state(0);
	const els: HTMLElement[] = [];
	function stop(node: HTMLElement, i: number) {
		els[i] = node;
		const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && (active = i)), { rootMargin: '-40% 0px -55% 0px' });
		io.observe(node);
		return { destroy: () => io.disconnect() };
	}
	const jump = (i: number) => els[i]?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });

	// Pins stay in this browser only.
	let pins = $state<string[]>([]);
	const PIN_KEY = 'ftb-vote-pins-v2';
	$effect(() => { try { pins = JSON.parse(localStorage.getItem(PIN_KEY) ?? '[]'); } catch { pins = []; } });
	function togglePin(b: string) {
		pins = pins.includes(b) ? pins.filter((k) => k !== b) : [...pins, b];
		try { localStorage.setItem(PIN_KEY, JSON.stringify(pins)); } catch { /* blocked storage: pins last this visit */ }
	}

	let jumpTo = $state('');
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
	<meta name="description" content="Walk Line 2 through Toronto's mayoral race: what the City controls, what changed, and every candidate in their own words, with proof." />
	<meta property="og:title" content="The {headline} question" />
	<meta property="og:description" content="Toronto votes Monday, October 26. Meet every mayoral candidate in their own words, with every number linked to its proof." />
	<meta property="og:type" content="website" />
	<meta property="og:image" content="/og-vote.png" />
	<meta name="twitter:card" content="summary_large_image" />
</svelte:head>

<LineStreet {stops} {active} onjump={jump} />

<section class="hall wrap">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>The <span><Fact id="toronto.operating.2026.gross" plain /></span> question</h1>
	<p class="dek">
		Every year the mayor and council decide how <Fact id="toronto.operating.2026.gross" /> gets spent. This fall, {mayor.length} people are
		on the ballot for mayor. Take a walk along Line 2: first, what the City actually controls; then, everyone running, in their own words.
	</p>
	<p class="proofnote sans">Every number and every quote links to its proof. Nothing here tells you who to vote for.</p>
</section>

<section class="stop wrap" use:stop={0}>
	<p class="kicker k1">Stop 1 · Start</p>
	<h2>Whose job is it?</h2>
	<p class="lede">The mayor can't fix everything. Guess who decides each of these.</p>
	<WhoseJob cards={data.whoseJob} />
</section>

<section class="stop wrap" use:stop={1}>
	<p class="kicker k2">Stop 2 · City Hall</p>
	<h2>Did it change anything?</h2>
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

<section class="wrap meet">
	<p class="kicker k3">Meet the candidates</p>
	<h2>Everyone running for mayor with a campaign website</h2>
	<p class="lede sans">
		{withSite.length} candidates, in ballot order (alphabetical by last name). Tap through each card: who they are, what they stand for, their numbers, their links.
		The {without.length} candidates without a website are at the next stop.
	</p>
	<label class="jump sans">Jump to a candidate
		<select bind:value={jumpTo} onchange={() => { const i = withSite.findIndex((c) => c.ballot_name === jumpTo); if (i >= 0) jump(i + 2); }}>
			<option value="">Choose…</option>
			{#each withSite as c (c.ballot_name)}<option value={c.ballot_name}>{c.ballot_name}</option>{/each}
		</select>
	</label>
</section>

{#each withSite as c, i (c.ballot_name)}
	<section class="cand" use:stop={i + 2}>
		<StoryCard
			person={c}
			profile={profileOf(c.ballot_name)}
			promises={data.promises.filter((p) => p.candidate === c.ballot_name)}
			index={i + 1}
			total={withSite.length}
			sources={data.recordSources}
			pinned={pins.includes(c.ballot_name)}
			onpin={() => togglePin(c.ballot_name)}
		/>
	</section>
{/each}

<section class="stop wrap" use:stop={withSite.length + 2}>
	<p class="kicker k1">Also on your ballot</p>
	<h2>{without.length} more names you'll see</h2>
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

<section class="stop wrap exit" use:stop={withSite.length + 3}>
	<p class="kicker k2">Kennedy · end of the line</p>
	<h2>Before you vote</h2>
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
	.hall { margin-top: 40px; }
	.kicker { color: #2f5d9b; }
	.k1 { color: #d9822b; }
	.k2 { color: #2f5d9b; }
	.k3 { color: #4a8c5c; }
	h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.04; margin: 10px 0 14px; letter-spacing: -1px; }
	h1 span { color: #2f5d9b; }
	h2 { font-size: clamp(28px, 4.5vw, 38px); margin: 6px 0 6px; letter-spacing: -0.5px; }
	.dek { font-size: 20px; line-height: 1.45; color: var(--ink-2); margin: 0; }
	.lede { font-size: 17px; color: var(--ink-2); margin: 0 0 6px; }
	.proofnote { font-size: 13px; color: var(--mute); margin: 12px 0 0; }
	.stop { padding-top: 56px; scroll-margin-top: 120px; }
	.meet { padding-top: 56px; }
	.bills { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 16px 0 6px; }
	.bill { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px; display: flex; flex-direction: column; gap: 2px; border-top: 5px solid #d9822b; }
	.yr { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: var(--mute); }
	.amt { font-family: var(--serif); font-size: 30px; font-weight: 700; }
	.chg { font-size: 13px; color: var(--ink-2); }
	.cap { font-size: 12.5px; color: var(--mute); margin: 0 0 14px; }
	.facts2 { display: grid; gap: 8px; font-size: 14px; background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px; margin-bottom: 12px; }
	.jump { display: flex; gap: 8px; align-items: center; font-size: 14px; margin: 12px 0 0; }
	.jump select { font: inherit; padding: 6px 8px; border-radius: 8px; border: 1px solid var(--ink); background: #fff; max-width: 60vw; }
	.cand { padding: 28px 16px; scroll-margin-top: 110px; }
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
		.cand { padding: 20px 10px; }
	}
</style>
