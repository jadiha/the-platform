<script lang="ts">
	// A candidate as a tap-through story: who they are, what they stand for, their numbers, links.
	// Every candidate gets the same panels in the same order. No colour comes from the candidate.
	import type { CampaignPromise, MayorProfile, OfficialCandidate } from '#lib/types.ts';
	import { displayName, highlightLink, pdfPageLink } from './links.ts';
	import { siteData } from '#lib/context.ts';

	let {
		person, profile, promises, index, total, sources, pinned, onpin
	}: {
		person: OfficialCandidate;
		profile?: MayorProfile;
		promises: CampaignPromise[];
		index: number;
		total: number;
		sources: Record<string, { title: string; url: string }>;
		pinned: boolean;
		onpin: () => void;
	} = $props();

	const { facts } = siteData();
	const dev = import.meta.env.DEV;
	const TOPIC = { tax: 'Taxes', transit: 'Getting around', housing: 'Housing', safety: 'Safety', money: 'City money', other: 'Also' } as const;
	const TOPIC_COLOR = { tax: '#d9822b', transit: '#2f5d9b', housing: '#4a8c5c', safety: '#7a5c99', money: '#3f7f74', other: '#8a857b' } as const;

	const hasNumbers = $derived(promises.length > 0);
	const panels = $derived(['Who they are', 'What they stand for', ...(hasNumbers ? ['Their numbers'] : []), 'Links']);
	let at = $state(0);
	const go = (d: number) => (at = Math.max(0, Math.min(panels.length - 1, at + d)));
	const panel = $derived(panels[at]);
	const name = $derived(displayName(person.ballot_name));
	const host = (u: string) => u.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
	const bill = $derived(Number(facts['toronto.property-tax.2026.avg-bill']?.value));
	const monthCap = $derived(Number(facts['toronto.ttc.fare-cap.2026']?.value));
	const money = (n: number) => '$' + Math.round(n).toLocaleString('en-CA');
	const years = (n?: number) => (n === 1 ? '1 year' : `${n} years`);
	// One plain sentence per promise: the campaign's own rule, applied to today's numbers. No forecasts.
	function plain(p: CampaignPromise): string | null {
		const r = p.rule;
		if (r.type === 'freeze') return `The average home's city tax bill would stay at ${money(bill)}, this year's amount, for ${years(r.years)}.`;
		if (r.type === 'percent' && typeof r.value === 'number') return `The average home's city tax bill would go from ${money(bill)} to ${money(bill * (1 + r.value / 100))}.`;
		if (r.type === 'fare-freeze') return "TTC fares would stay at today's prices.";
		if (r.type === 'fare-free') return 'Riding the TTC would cost nothing.';
		if (r.type === 'fare-free-phased') return `The TTC would become free, starting with ${((r.first as string[] | undefined) ?? []).join(', ').replace(/, ([^,]*)$/, ' and $1')} riders.`;
		if (r.type === 'weekly-cap') return `After ${r.trips} paid TTC rides in a week, the rest of that week would be free. Today it's free after ${monthCap} paid rides in a month.`;
		return null;
	}

	// svelte-ignore state_referenced_locally
	let status = $state(profile?.status ?? 'checked');
	async function approve() {
		const r = await fetch('/__review', { method: 'POST', body: JSON.stringify({ file: 'profiles', candidate: person.ballot_name }) });
		if (r.ok) status = 'checked';
	}
	function onkey(e: KeyboardEvent) {
		if (e.key === 'ArrowRight') go(1);
		if (e.key === 'ArrowLeft') go(-1);
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<article class="card sans" aria-label="{name}, candidate {index} of {total}" tabindex="-1" onkeydown={onkey}>
	<div class="bars" aria-hidden="true">
		{#each panels as p, i (p)}<span class:on={i <= at}></span>{/each}
	</div>
	<div class="top">
		<span class="count">CANDIDATE {index} OF {total}</span>
		<button class="pin" aria-pressed={pinned} onclick={onpin}>{pinned ? 'Pinned' : 'Pin'}</button>
	</div>
	<h3 class="name">{name}</h3>
	<div class="ptitle">{panel}</div>

	<div class="body">
		{#if panel === 'Who they are'}
			{#if profile?.note}<p class="note">{profile.note}</p>{/if}
			{#each profile?.record ?? [] as r (r.text)}
				<p class="rec">{r.text} {#if sources[r.src]}<a href={sources[r.src].url} target="_blank" rel="noopener">proof ↗</a>{/if}</p>
			{/each}
			{#if profile?.about}
				<q>{profile.about.text}</q>
				<a class="hl" href={highlightLink(profile.about.url, profile.about.text)} target="_blank" rel="noopener">In their words, highlighted on their site ↗</a>
			{:else if profile?.unreadable}
				<p class="none">{profile.unreadable}</p>
			{:else if profile?.withheld}
				<p class="none">Their own words are being checked against their site. Back soon.</p>
			{/if}
			{#if !profile?.record?.length && !profile?.about}<p class="none">No previous mayoral run or City office on record.</p>{/if}
		{:else if panel === 'What they stand for'}
			{#if profile?.priorities?.length}
				<ul class="pri">
					{#each profile.priorities as p (p.text)}
						<li style="--tc:{TOPIC_COLOR[p.topic]}">
							<span class="tag">{TOPIC[p.topic]}</span>
							<q>{p.text}</q>
							<a href={highlightLink(p.url, p.text)} target="_blank" rel="noopener">see it on their site ↗</a>
						</li>
					{/each}
				</ul>
			{:else if profile?.withheld}
				<p class="none">Being checked word for word against their site. Back soon.</p>
			{:else}
				<p class="none">We didn't find a platform or list of priorities on their campaign site when we read it on October 13. Check their links.</p>
			{/if}
		{:else if panel === 'Their numbers'}
			<ul class="nums">
				{#each promises as p (p.text)}
					{@const t = (p.room in TOPIC_COLOR ? p.room : 'other') as keyof typeof TOPIC_COLOR}
					<li style="--c:{TOPIC_COLOR[t]}">
						<span class="tp">{TOPIC[t]}</span>
						{#if plain(p)}<b class="plain">{plain(p)}</b>{/if}
						<q class="small">{p.text}</q>
						{#if p.cost_text}<q class="small">{p.cost_text}</q>{/if}
						<a class="hl" href={highlightLink(p.url, p.text)} target="_blank" rel="noopener">see it on their site ↗</a>
					</li>
				{/each}
			</ul>
			<p class="fine">In plain terms: the campaign's own rule applied to today's numbers. It doesn't predict whether a promise is kept or what it would change.</p>
		{:else}
			<ul class="links">
				{#if person.website}<li><a href={person.website} target="_blank" rel="noopener">{host(person.website)} ↗</a></li>{:else}<li class="none">No campaign website on the City's list</li>{/if}
				{#each person.social as s (s)}<li><a href={s} target="_blank" rel="noopener">{host(s)} ↗</a></li>{/each}
			</ul>
			{#if profile?.archive}
				<p class="small">Saved copies of the pages we quoted: {#each Object.values(profile.archive) as a, i (a)}<a href={a} target="_blank" rel="noopener">copy {i + 1}</a>{' '}{/each}</p>
			{/if}
		{/if}
	</div>

	<div class="nav">
		<button onclick={() => go(-1)} disabled={at === 0} aria-label="Previous">‹ Back</button>
		<button class="next" onclick={() => go(1)} disabled={at === panels.length - 1} aria-label="Next">{at === panels.length - 1 ? 'Done' : 'Next ›'}</button>
	</div>
	{#if dev && profile && status === 'draft'}
		<div class="review">DRAFT: open each "see it" link, check the words, then <button onclick={approve}>Approve this card</button></div>
	{/if}
</article>

<style>
	.card { background: #fff; border: 1px solid var(--rule); border-radius: 18px; padding: 14px 16px 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06); max-width: 460px; margin: 0 auto; min-height: 430px; display: flex; flex-direction: column; outline: none; }
	.bars { display: flex; gap: 4px; margin-bottom: 10px; }
	.bars span { flex: 1; height: 3px; border-radius: 3px; background: #e6e2d9; transition: background 0.3s; }
	.bars span.on { background: var(--ink); }
	.top { display: flex; justify-content: space-between; align-items: center; }
	.count { font-size: 11px; letter-spacing: 1.5px; font-weight: 600; color: var(--mute); }
	.pin { font: inherit; font-size: 11px; border: 1px solid var(--rule); background: #fff; border-radius: 999px; padding: 3px 10px; cursor: pointer; }
	.pin[aria-pressed='true'] { background: var(--ink); color: #fff; }
	.name { font-family: var(--serif); font-size: 30px; margin: 4px 0 0; letter-spacing: -0.5px; }
	.ptitle { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--mute); margin: 2px 0 10px; }
	.body { flex: 1; font-size: 14px; }
	q { display: block; font-family: var(--serif); font-style: italic; font-size: 18px; line-height: 1.4; margin: 6px 0; }
	q.small { font-size: 14px; }
	.rec { margin: 0 0 6px; font-weight: 600; }
	.rec a, .hl, .pri a, .small a { font-weight: 400; font-size: 11.5px; color: var(--mute); }
	.note { background: #fff6d6; padding: 6px 8px; border-radius: 6px; font-size: 12.5px; }
	.none { color: var(--mute); }
	.pri { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
	.pri li { border-left: 3px solid var(--tc); padding-left: 10px; }
	.pri q { font-size: 16px; margin: 2px 0; }
	.tag { font-size: 10.5px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--tc); }
	.links { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; font-size: 15px; overflow-wrap: anywhere; }
	.small { font-size: 12px; color: var(--mute); }
	.nums { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
	.nums li { border-left: 4px solid var(--c); background: #faf8f4; border-radius: 0 12px 12px 0; padding: 10px 14px; display: flex; flex-direction: column; gap: 4px; }
	.tp { font-family: var(--sans); font-size: 11px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; color: var(--c); }
	.plain { font-family: var(--sans); font-size: 16px; line-height: 1.35; }
	.nums q.small { color: var(--ink-2); font-style: italic; }
	.fine { font-family: var(--sans); font-size: 11.5px; color: var(--mute); margin: 10px 0 0; }
	.nav { display: flex; justify-content: space-between; margin-top: 12px; }
	.nav button { font: inherit; font-size: 14px; font-weight: 600; border: 0; background: none; cursor: pointer; padding: 8px 4px; }
	.nav .next { background: var(--ink); color: #fff; border-radius: 999px; padding: 8px 18px; }
	.nav button:disabled { opacity: 0.3; cursor: default; }
	.review { margin-top: 8px; font-size: 12px; background: #fff6d6; padding: 6px 8px; border-radius: 6px; }
	.review button { font: inherit; font-weight: 600; cursor: pointer; }
</style>
