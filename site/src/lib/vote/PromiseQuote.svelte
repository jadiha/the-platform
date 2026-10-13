<script lang="ts">
	// One candidate's promise, word for word, with a link that opens their own page with the
	// sentence highlighted. No colour comes from candidate data: every plaque looks the same.
	import type { CampaignPromise } from '#lib/types.ts';
	import { displayName, highlightLink } from './links.ts';
	import { formatDate } from '#lib/format.ts';
	const dev = import.meta.env.DEV;
	let { p, pinned = false, onpin }: { p: CampaignPromise; pinned?: boolean; onpin?: () => void } = $props();
	// svelte-ignore state_referenced_locally
	let status = $state(p.status);
	async function approve() {
		const r = await fetch('/__review', { method: 'POST', body: JSON.stringify({ url: p.url, text: p.text }) });
		if (r.ok) status = 'checked';
	}
</script>

<div class="plaque" class:draft={status === 'draft'}>
	{#if onpin}<button class="pin sans" aria-pressed={pinned} onclick={onpin}>{pinned ? 'Pinned' : 'Pin'}</button>{/if}
	<div class="who sans">{displayName(p.candidate)}</div>
	<q>{p.text}</q>
	{#if p.cost_text}<q class="cost">{p.cost_text}</q>{/if}
	{#if p.note}<p class="note sans">{p.note}</p>{/if}
	<div class="src sans">
		<a href={highlightLink(p.url, p.text)} target="_blank" rel="noopener">See it highlighted on their campaign site ↗</a>
		{#if p.archive}· <a href={p.archive} target="_blank" rel="noopener">saved copy ↗</a>{/if}
		· read {formatDate(p.retrieved)}
	</div>
	{#if dev && status === 'draft'}
		<div class="review sans">DRAFT: open the link, check the words match, then <button onclick={approve}>Approve</button></div>
	{/if}
</div>

<style>
	.plaque { background: #fff; border: 1px solid var(--rule); border-left: 4px solid var(--c, var(--ink)); border-radius: 0 10px 10px 0; padding: 10px 12px; }
	.plaque.draft { outline: 2px dashed #e0a800; }
	.who { font-weight: 600; font-size: 13px; }
	q { display: block; font-style: italic; font-size: 16px; margin: 4px 0; line-height: 1.45; }
	q.cost { font-size: 14px; }
	.note { font-size: 12px; color: var(--ink-2); margin: 4px 0; }
	.src { font-size: 11.5px; color: var(--mute); }
	.src a { color: var(--ink-2); }
	.pin { float: right; font-size: 11px; border: 1px solid var(--rule); background: #fff; border-radius: 999px; padding: 3px 9px; cursor: pointer; }
	.pin[aria-pressed='true'] { background: var(--ink); color: #fff; }
	.review { margin-top: 8px; font-size: 12px; background: #fff6d6; padding: 6px 8px; }
	.review button { font: inherit; font-weight: 600; cursor: pointer; }
</style>
