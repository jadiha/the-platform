<script lang="ts">
	// Public record only: role, recorded decisions, sourced quotes. Same fields for everyone.
	import type { Person } from '#lib/types.ts';
	import { formatDate } from '#lib/format.ts';

	let { person, compact = false }: { person: Person; compact?: boolean } = $props();
	const decisions = $derived((person.decisions ?? []).slice(0, compact ? 2 : undefined));
	const quotes = $derived((person.quotes ?? []).slice(0, compact ? 1 : undefined));
	const VOTE: Record<string, string> = { yes: 'Voted yes', no: 'Voted no', absent: 'Absent', proposed: 'Proposed', 'n/a': '' };
</script>

<article class="card sans" id={person.id}>
	<header>
		<h4>{person.name}</h4>
		<p class="role">
			{person.role}{#if person.party}{' · '}{person.party}{/if}
		</p>
		{#if person.on_ballot_2026}<span class="ballot">On the Oct 26 ballot</span>{/if}
		{#if person.official_url && !compact}<a class="official" href={person.official_url} target="_blank" rel="noopener">Official page</a>{/if}
	</header>

	{#if decisions.length}
		<ul class="decisions">
			{#each decisions as d}
				<li>
					{#if d.vote && VOTE[d.vote]}<span class="vote v-{d.vote}">{VOTE[d.vote]}</span>{/if}
					{d.what}
					<a class="src" href={d.source.url} target="_blank" rel="noopener">{formatDate(d.date)} · {d.source.title}</a>
				</li>
			{/each}
		</ul>
	{/if}

	{#if !compact && !decisions.length && !quotes.length}
		<p class="none">No recorded votes or quotes added yet.</p>
	{/if}

	{#each quotes as q}
		<blockquote>
			“{q.text}”
			<a class="src" href={q.source.url} target="_blank" rel="noopener">{formatDate(q.date)} · {q.source.title}</a>
		</blockquote>
	{/each}

	{#if compact && ((person.decisions?.length ?? 0) > 2 || (person.quotes?.length ?? 0) > 1)}
		<a class="more" href="/people/#{person.id}">Full record →</a>
	{/if}
</article>

<style>
	.card { background: #fff; border: var(--line); border-radius: 14px; box-shadow: var(--pop); padding: 14px 16px; font-size: 13.5px; line-height: 1.45; }
	h4 { margin: 0; font-family: var(--display); font-weight: 700; font-size: 19px; letter-spacing: 0; }
	.role { margin: 2px 0 6px; color: var(--mute); }
	.ballot { display: inline-block; font-size: 11px; font-weight: 600; border: 1px solid var(--ink); padding: 0 6px; }
	ul { list-style: none; padding: 0; margin: 10px 0 0; display: grid; gap: 8px; }
	.vote { font-weight: 700; margin-right: 4px; }
	.v-yes { color: var(--ok); }
	.v-no { color: #b02a37; }
	.v-absent { color: var(--mute); }
	.src { display: block; font-size: 11.5px; color: var(--mute); margin-top: 2px; }
	blockquote { margin: 10px 0 0; padding-left: 10px; border-left: 3px solid var(--rule); font-family: var(--serif); font-size: 15px; font-style: italic; }
	blockquote .src { font-family: var(--sans); font-style: normal; }
	.official { font-size: 12px; margin-left: 6px; }
	.none { color: var(--mute); font-size: 12.5px; margin: 8px 0 0; }
	.more { display: inline-block; margin-top: 8px; font-weight: 600; font-size: 12.5px; }
</style>
