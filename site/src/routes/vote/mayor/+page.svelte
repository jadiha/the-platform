<script lang="ts">
	// Every name on the mayor ballot, in ballot order, with the links the City Clerk published
	// and any promises from the walk. Same fields for everyone.
	import PromiseQuote from '#lib/vote/PromiseQuote.svelte';
	import { displayName } from '#lib/vote/links.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const ROOM_TITLE = { tax: 'Your tax bill', transit: 'Getting around', housing: 'Rent and housing', build: 'What gets built', safety: 'Safety' } as const;
	const mayor = $derived(data.official?.mayor ?? []);
	const host = (u: string) => u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '');
</script>

<svelte:head>
	<title>Every candidate for mayor · Toronto 2026 · Follow the Budget</title>
	<meta name="description" content="Everyone on Toronto's 2026 mayoral ballot, in ballot order, with their campaign links and published promises." />
</svelte:head>

<div class="wrap page">
	<p class="kicker">Toronto votes · Monday, October 26</p>
	<h1>Everyone running for mayor</h1>
	<p class="dek">
		All {mayor.length} names on the ballot, in the same order as the ballot (alphabetical by last name). Links are the ones each
		candidate gave the City. <a href={data.official?.source.url} target="_blank" rel="noopener">Proof: {data.official?.source.title} ↗</a>
	</p>
	<p class="sans note">Promises shown are the ones with a number or a clear rule on five budget topics, copied word for word from the candidate's own campaign site. For everything else a candidate stands for, follow their links.</p>

	<ol class="list">
		{#each mayor as c (c.ballot_name)}
			{@const ps = data.promises.filter((p) => p.candidate === c.ballot_name)}
			<li>
				<h2>{displayName(c.ballot_name)}</h2>
				<p class="links sans">
					{#if c.website}<a href={c.website} target="_blank" rel="noopener">{host(c.website)} ↗</a>{:else}No campaign website on the City's list{/if}
					{#each c.social as s (s)} · <a href={s} target="_blank" rel="noopener">{host(s).split('/')[0]}</a>{/each}
				</p>
				{#if data.reviewing.length && !ps.length}
					<p class="sans none">Promises are being checked word for word. Follow their links in the meantime.</p>
				{:else if ps.length}
					{#each ps as p (p.text)}<div class="pq"><span class="sans tag">{ROOM_TITLE[p.room]}</span><PromiseQuote {p} /></div>{/each}
				{:else}
					<p class="sans none">No promise with a number or clear rule on these topics found on their campaign site{c.website ? '' : ' (no website listed)'}.</p>
				{/if}
			</li>
		{/each}
	</ol>
</div>

<style>
	.page { margin-top: 44px; }
	h1 { font-size: clamp(32px, 5vw, 46px); margin: 8px 0 10px; }
	.dek { font-size: 18px; color: var(--ink-2); }
	.note { font-size: 13px; color: var(--mute); }
	.list { list-style: none; padding: 0; margin: 24px 0 0; }
	.list li { border-top: 1px solid var(--rule); padding: 14px 0; }
	h2 { font-size: 20px; margin: 0 0 2px; }
	.links { font-size: 13px; color: var(--mute); margin: 0 0 6px; overflow-wrap: anywhere; }
	.none { font-size: 13px; color: var(--mute); margin: 0; }
	.pq { margin-top: 8px; }
	.tag { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--mute); }
</style>
