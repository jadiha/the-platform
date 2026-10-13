<script lang="ts">
	// Renders a number from the fact registry with its verification status and sources.
	// Story copy must never hard-code numbers; scripts/check-content.mjs enforces this.
	import Popover from './Popover.svelte';
	import { siteData } from '#lib/context.ts';
	import { formatDate, formatFact, STATUS_HELP, STATUS_LABEL } from '#lib/format.ts';

	let { id, short = false, plain = false }: { id: string; short?: boolean; plain?: boolean } = $props();
	const { facts } = siteData();
	const fact = $derived(facts[id]);
</script>

{#if !fact}
	<mark class="missing sans" title="Missing fact: {id}">⟦{id}⟧</mark>
{:else if plain}
	{formatFact(fact, short ? 'short' : 'long')}
{:else}
	<Popover label="Source for {fact.label}">
		{#snippet trigger()}
			<span class="value status-{fact.status}">{formatFact(fact, short ? 'short' : 'long')}</span>
		{/snippet}
		<strong class="lbl">{fact.label}</strong>
		{#if fact.basis}<span class="basis">{fact.basis}</span>{/if}
		<span class="status st-{fact.status}">{STATUS_LABEL[fact.status]}</span>
		<span class="help">{STATUS_HELP[fact.status]}</span>
		<span class="src">
			Source: <a href={fact.primary.url} target="_blank" rel="noopener">{fact.primary.title}</a>{#if fact.primary.locator}, {fact.primary.locator}{/if}
		</span>
		{#each fact.crosscheck ?? [] as c}
			<span class="src">
				Checked against: <a href={c.url} target="_blank" rel="noopener">{c.title}</a>{#if c.date} ({formatDate(c.date)}){/if}{#if c.note} · {c.note}{/if}
			</span>
		{/each}
		{#if fact.note}<span class="note">{fact.note}</span>{/if}
		<span class="asof">Checked {formatDate(fact.as_of)}</span>
	</Popover>
{/if}

<style>
	.value {
		font-weight: 600; white-space: nowrap;
		border-bottom: 2px solid var(--ok); padding-bottom: 0;
	}
	.value.status-single { border-bottom-color: var(--rule); border-bottom-style: solid; }
	.value.status-disagree { border-bottom-color: var(--warn); border-bottom-style: dashed; }
	.value.status-reported { border-bottom-color: var(--warn); border-bottom-style: dotted; font-style: italic; }
	.lbl { display: block; font-size: 14px; margin-bottom: 2px; }
	.basis { display: block; color: #bbb; font-size: 12px; margin-bottom: 8px; }
	.status { display: inline-block; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; padding: 1px 6px; border: 1px solid currentColor; }
	.st-verified { color: #7fd99a; }
	.st-single { color: #ddd; }
	.st-disagree, .st-reported { color: #ffb366; }
	.help { display: block; color: #ccc; margin: 4px 0 8px; font-size: 12px; }
	.src, .note, .asof { display: block; margin-top: 4px; }
	.note { color: #ffd9a8; }
	.asof { color: #999; font-size: 11px; margin-top: 8px; }
	.missing { background: #ffe3e3; color: #c92a2a; font-size: 12px; padding: 0 4px; }
</style>
