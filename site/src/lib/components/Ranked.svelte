<script lang="ts">
	// Part 3: every line of the budget, biggest first. Tap a row to open what's inside it, right
	// there under the row; lines with nothing inside open their note and source instead.
	import { categoryColor } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { BudgetNode } from '#lib/types.ts';
	import type { SvelteSet } from 'svelte/reactivity';
	import Ranked from './Ranked.svelte';

	let { parent, opened, depth = 0, category }: { parent: BudgetNode; opened: SvelteSet<string>; depth?: number; category?: string } = $props();
	// Long levels show the top few first, so an opened row doesn't push everything off screen.
	const LIMIT = 8;
	let all = $state(false);
	const rows = $derived([...(parent.children ?? [])].sort((a, b) => b.gross - a.gross));
	const shown = $derived(all ? rows : rows.slice(0, LIMIT));
	const top = $derived(Math.max(1, ...rows.map((r) => r.gross)));
	const pct = (x: number) => (x >= 1 ? `${x.toFixed(0)}%` : x > 0 ? '<1%' : '');
	const toggle = (id: string) => (opened.has(id) ? opened.delete(id) : opened.add(id));
</script>

<ol class="rk sans" class:nested={depth > 0}>
	{#each shown as n, i (n.id)}
		{@const cat = n.category ?? category}
		{@const kids = !!n.children?.length}
		{@const info = !kids && !!(n.note || n.source)}
		{@const isOpen = opened.has(n.id)}
		<li id="row-{n.id}" style="--c:{categoryColor(cat)}">
			{#snippet line()}
				<span class="rank">{i + 1}</span>
				<span class="name">{n.name}</span>
				<span class="amt">{money(n.gross, 'short')}</span>
				<span class="pct">{pct(parent.gross ? (n.gross / parent.gross) * 100 : 0)}</span>
				<span class="chev" aria-hidden="true"></span>
				<span class="bar" aria-hidden="true"><i style="width:{(Math.max(0, n.gross) / top) * 100}%"></i></span>
			{/snippet}
			{#if kids || info}
				<button class="row" class:open={isOpen} aria-expanded={isOpen} onclick={() => toggle(n.id)}>{@render line()}</button>
			{:else}
				<div class="row still">{@render line()}</div>
			{/if}
			{#if isOpen && kids}
				<div class="inside"><Ranked parent={n} {opened} depth={depth + 1} category={cat} /></div>
			{:else if isOpen && info}
				<p class="info">
					{#if n.note}{n.note}{/if}
					This is as detailed as the published budget gets.
					{#if n.source}<a href={n.source.url} target="_blank" rel="noopener">Source ↗</a>{/if}
				</p>
			{/if}
		</li>
	{/each}
</ol>
{#if rows.length > LIMIT}
	<button class="all sans" onclick={() => (all = !all)}>{all ? 'Show the top ' + LIMIT : `Show all ${rows.length}`}</button>
{/if}

<style>
	.rk { list-style: none; padding: 0; margin: 0; }
	.rk > li { border-top: 1px solid var(--rule); }
	.rk > li:first-child { border-top: 0; }
	.row {
		display: grid; grid-template-columns: 26px 1fr auto 42px 18px; grid-template-areas: 'rank name amt pct chev' '. bar bar bar .';
		gap: 6px 12px; align-items: baseline; width: 100%; padding: 14px 8px 14px 4px;
		font: inherit; text-align: left; color: inherit; background: none; border: 0; border-radius: 10px;
	}
	button.row { cursor: pointer; }
	button.row:hover, button.row:focus-visible { background: color-mix(in srgb, var(--c) 9%, transparent); outline: none; }
	.rank { grid-area: rank; font-size: 13px; color: var(--mute); font-variant-numeric: tabular-nums; text-align: right; }
	.name { grid-area: name; font-size: 16px; font-weight: 600; line-height: 1.3; }
	.amt { grid-area: amt; font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; text-align: right; }
	.pct { grid-area: pct; font-size: 13px; color: var(--mute); font-variant-numeric: tabular-nums; text-align: right; }
	.chev { grid-area: chev; align-self: center; width: 7px; height: 7px; border-right: 2px solid var(--mute); border-bottom: 2px solid var(--mute); transform: rotate(45deg) translate(-2px, -2px); transition: transform 0.2s; }
	.row.open .chev { transform: rotate(225deg); }
	.still .chev { visibility: hidden; }
	.bar { grid-area: bar; align-self: center; height: 10px; background: color-mix(in srgb, var(--ink) 6%, transparent); border-radius: 5px; overflow: hidden; }
	.bar i { display: block; height: 100%; background: var(--c); border-radius: 5px; animation: grow 0.5s ease-out; transform-origin: left; }
	@keyframes grow { from { transform: scaleX(0); } }
	/* What's inside sits under its row, set in from the left with a thin line in the row's colour. */
	.inside { margin: 0 0 14px 30px; padding-left: 14px; border-left: 2px solid var(--c); animation: open 0.25s ease-out; }
	.nested .name, .nested .amt { font-size: 15px; }
	.nested .row { padding-top: 11px; padding-bottom: 11px; }
	.info { margin: 0 0 14px 42px; font-size: 14px; color: var(--ink-2); line-height: 1.5; max-width: 62ch; animation: open 0.25s ease-out; }
	.all { font: inherit; font-size: 14px; font-weight: 600; color: var(--ink-2); background: none; border: 1px solid var(--rule); border-radius: 999px; padding: 6px 14px; margin: 8px 0 4px 34px; cursor: pointer; }
	.all:hover { color: var(--ink); border-color: var(--ink); }
	@keyframes open { from { opacity: 0; transform: translateY(-4px); } }
	@media (max-width: 600px) {
		.row { grid-template-columns: 20px 1fr auto 16px; grid-template-areas: 'rank name amt chev' '. bar pct .'; gap: 6px 10px; }
		.pct { line-height: 1; }
		.pct { text-align: right; align-self: center; font-size: 12px; }
		.inside { margin-left: 12px; padding-left: 10px; }
		.info { margin-left: 30px; }
		.all { margin-left: 30px; }
	}
	@media (prefers-reduced-motion: reduce) { .bar i, .inside, .info { animation: none; } }
</style>
