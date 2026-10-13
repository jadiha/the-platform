<script lang="ts">
	import type { Snippet } from 'svelte';
	import Popover from './Popover.svelte';
	import { GLOSSARY } from '#lib/glossary.ts';

	let { id, children }: { id: string; children?: Snippet } = $props();
	const t = $derived(GLOSSARY[id]);
</script>

{#if t}
	<Popover label="What does {t.term} mean?">
		{#snippet trigger()}<span class="term">{#if children}{@render children()}{:else}{t.term.toLowerCase()}{/if}</span>{/snippet}
		<strong>{t.term}</strong><br />{t.short}
		{#if t.more}<span class="more">{t.more}</span>{/if}
		<a class="all" href="/glossary/#{id}">All terms →</a>
	</Popover>
{:else}
	<mark title="Missing glossary term: {id}">{@render children?.()}</mark>
{/if}

<style>
	.term { border-bottom: 1.5px dotted currentColor; cursor: help; }
	.more { display: block; margin-top: 6px; color: #ccc; }
	.all { display: block; margin-top: 8px; font-size: 12px; }
</style>
