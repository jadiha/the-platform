<script lang="ts">
	import { GLOSSARY } from '#lib/glossary.ts';

	const terms = Object.entries(GLOSSARY).sort(([, a], [, b]) => a.term.localeCompare(b.term));
</script>

<svelte:head>
	<title>Glossary · The 6ix Votes</title>
	<meta name="description" content="Budget jargon explained in plain language." />
</svelte:head>

<div class="wrap page">
	<p class="kicker">Glossary</p>
	<h1>Budget words, in plain language</h1>
	<p class="dek">Government budgets use a lot of jargon. Here is what each term means, with an everyday comparison where we can.</p>

	<dl>
		{#each terms as [id, t] (id)}
			<div class="entry" {id}>
				<dt>{t.term}</dt>
				<dd>
					<p>{t.short}</p>
					{#if t.more}<p class="more">{t.more}</p>{/if}
					{#if t.source}<p class="src sans">Source: <a href={t.source.url} target="_blank" rel="noopener">{t.source.title}</a></p>{/if}
				</dd>
			</div>
		{/each}
	</dl>
</div>

<style>
	.page { margin-top: 48px; }
	h1 { font-size: clamp(32px, 5vw, 46px); margin: 8px 0 12px; }
	.dek { color: var(--ink-2); font-size: 20px; }
	dl { margin: 32px 0 0; }
	.entry { border-top: 1px solid var(--rule); padding: 16px 0; scroll-margin-top: 80px; }
	.entry:target { background: var(--paper-2); }
	dt { font-family: var(--sans); font-weight: 700; font-size: 17px; }
	dd { margin: 4px 0 0; }
	dd p { margin: 0 0 6px; }
	.more { color: var(--ink-2); font-size: 17px; }
	.src { font-size: 12px; color: var(--mute); }
</style>
