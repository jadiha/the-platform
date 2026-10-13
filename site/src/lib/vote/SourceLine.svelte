<script lang="ts">
	// A visible "where this number comes from" line under a fact. PDFs open at the cited page.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	let { id }: { id: string } = $props();
	const { facts } = siteData();
	const f = $derived(facts[id]);
</script>

{#if f}
	<a class="src sans" href={pdfPageLink(f.primary.url, f.primary.locator)} target="_blank" rel="noopener">
		Proof: {f.primary.title}{#if f.primary.locator}, {f.primary.locator}{/if} ↗
	</a>
{/if}

<style>
	.src { display: inline-block; font-size: 11.5px; color: var(--mute); text-decoration: underline; text-decoration-color: var(--rule); margin-top: 4px; }
	.src:hover { color: var(--ink); }
</style>
