<script lang="ts">
	// Zoomable treemap, one level at a time: tap a tile to open it, use the breadcrumb to go back.
	// The list under the map holds the same data for screen readers and small phones.
	import { hierarchy, treemap, treemapSquarify } from 'd3-hierarchy';
	import { categoryColor } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { BudgetNode } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// svelte-ignore state_referenced_locally
	let levelKey = $state(data.trees[0]?.key ?? 'ontario');
	const level = $derived(data.trees.find((t) => t.key === levelKey) ?? data.trees[0]);
	let path = $state<BudgetNode[]>([]);
	const root = $derived(level?.tree as BudgetNode);
	const current = $derived(path.at(-1) ?? root);
	const category = $derived([...path].reverse().find((n) => n.category)?.category);

	function choose(key: string) {
		levelKey = key;
		path = [];
	}
	let mapEl: HTMLDivElement | undefined = $state();
	function open(n: BudgetNode, fromList = false) {
		if (!n.children?.length) return;
		path = [...path, n];
		if (fromList) mapEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
	}
	const back = (i: number) => (path = path.slice(0, i));

	let width = $state(0);
	const height = $derived(width < 600 ? 380 : 480);

	// Treemap areas can't be negative; a few corporate lines are (net savings). They stay in the list.
	const tiles = $derived.by(() => {
		if (!current?.children || width === 0) return [];
		const h = hierarchy<BudgetNode>({ ...current, children: current.children.filter((c) => c.gross > 0) } as BudgetNode)
			.sum((d) => (d.children?.some((c) => c.gross > 0) ? 0 : Math.max(0, d.gross)))
			.sort((a, b) => (b.value ?? 0) - (a.value ?? 0));
		treemap<BudgetNode>().tile(treemapSquarify.ratio(1.4)).size([width, height]).paddingInner(2).round(true)(h);
		return (h.children ?? []).map((c) => {
			const r = c as typeof c & { x0: number; x1: number; y0: number; y1: number };
			return { node: c.data, x: r.x0, y: r.y0, w: r.x1 - r.x0, h: r.y1 - r.y0 };
		});
	});

	const share = (n: BudgetNode) => (current.gross ? (n.gross / current.gross) * 100 : 0);
	const pct = (x: number) => (x >= 1 ? `${x.toFixed(0)}%` : x > 0 ? '<1%' : '');
	const color = (n: BudgetNode) => categoryColor(n.category ?? category);
	// Pale category colours need dark labels to stay readable.
	const LIGHT = new Set(['other', 'social-services', 'parks-rec-culture', 'infrastructure', 'government-debt']);
	const ink = (n: BudgetNode) => (LIGHT.has(n.category ?? category ?? 'other') ? 'var(--ink)' : '#fff');
	const list = $derived([...(current?.children ?? [])].sort((a, b) => b.gross - a.gross));
</script>

<svelte:head>
	<title>Explore the budget · The 6ix Votes</title>
	<meta name="description" content="Tap through Ontario's, Toronto's and Scarborough's budgets, from the big categories down to individual programs." />
</svelte:head>

<div class="wide page">
	<p class="kicker">Explore the budget</p>
	<h1>Open up the budget yourself</h1>
	<p class="dek">Each box is sized by how much money it gets. Tap a box to see what's inside it.</p>

	{#if !level}
		<p class="sans">Budget data is being prepared.</p>
	{:else}
		<div class="tabs sans" role="tablist">
			{#each data.trees as t (t.key)}
				<button role="tab" aria-selected={levelKey === t.key} onclick={() => choose(t.key)}>{t.label}</button>
			{/each}
		</div>

		<div class="head sans">
			<nav class="crumbs" aria-label="Where you are">
				<button onclick={() => back(0)} disabled={!path.length}>{root.name}</button>
				{#each path as n, i (n.id)}
					<span aria-hidden="true">›</span>
					<button onclick={() => back(i + 1)} disabled={i === path.length - 1}>{n.name}</button>
				{/each}
			</nav>
			<p class="total">
				<strong>{money(current.gross)}</strong>
				<span>{root.basis}{root.basis?.includes(root.year ?? '') ? '' : `, ${root.year}`}</span>
			</p>
		</div>

		<div class="map" bind:this={mapEl} bind:clientWidth={width} style="height:{height}px">
			{#each tiles as t (t.node.id)}
				{@const big = t.w > 90 && t.h > 46}
				<button
					class="tile sans"
					class:leaf={!t.node.children?.length}
					style="left:{t.x}px;top:{t.y}px;width:{t.w}px;height:{t.h}px;--c:{color(t.node)};--t:{ink(t.node)}"
					onclick={() => open(t.node)}
					title="{t.node.name}: {money(t.node.gross)} ({pct(share(t.node))})"
					tabindex="-1"
					aria-hidden="true"
				>
					{#if big}
						<span class="tname">{t.node.name}</span>
						<span class="tval">{money(t.node.gross, 'short')} · {pct(share(t.node))}</span>
					{:else if t.w > 44 && t.h > 22}
						<span class="tval">{pct(share(t.node))}</span>
					{/if}
				</button>
			{/each}
		</div>
		{#if root.note && !path.length}<p class="note sans">{root.note}</p>{/if}
		{#if current.note && path.length}<p class="note sans">{current.note}</p>{/if}

		<h2 class="sans listhead">Inside {current.name}</h2>
		<ol class="list sans">
			{#each list as n (n.id)}
				<li style="--c:{color(n)}">
					<div class="row">
						{#if n.children?.length}
							<button class="name link" onclick={() => open(n, true)}>{n.name} <span aria-hidden="true">›</span></button>
						{:else}
							<span class="name">{n.name}</span>
						{/if}
						<span class="amt">{money(n.gross, 'short')}</span>
						<span class="pct">{pct(share(n))}</span>
					</div>
					{#if n.net != null && n.net !== n.gross}
						<p class="sub">Paid by this government itself (net): {money(n.net, 'short')}</p>
					{/if}
					{#if n.note}<p class="sub">{n.note}</p>{/if}
					{#if n.source}
						<p class="sub"><a href={n.source.url} target="_blank" rel="noopener">{n.source.title}</a>{#if n.source.locator}, {n.source.locator}{/if}</p>
					{/if}
				</li>
			{/each}
		</ol>
		{#if root.source}
			<p class="src sans">
				Source: <a href={root.source.url} target="_blank" rel="noopener">{root.source.title}</a>{#if root.source.locator}, {root.source.locator}{/if}.
				How we grouped lines into categories: <a href="/sources/#categories">sources and methods</a>.
			</p>
		{/if}
	{/if}
</div>

<style>
	.page { margin-top: 44px; }
	h1 { font-size: clamp(32px, 5vw, 46px); margin: 8px 0 10px; }
	.dek { color: var(--ink-2); font-size: 20px; margin: 0 0 18px; }
	.tabs { display: flex; border-bottom: 1px solid var(--ink); margin-bottom: 12px; }
	.tabs button { font: inherit; font-size: 15px; font-weight: 600; background: none; border: 0; padding: 8px 16px; cursor: pointer; color: var(--mute); border-bottom: 3px solid transparent; margin-bottom: -1px; }
	.tabs button[aria-selected='true'] { color: var(--ink); border-bottom-color: var(--ink); }
	.head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
	.crumbs { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px; font-size: 14px; }
	.crumbs button { font: inherit; background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; color: var(--ink-2); }
	.crumbs button:disabled { cursor: default; text-decoration: none; color: var(--ink); font-weight: 700; }
	.total { margin: 0; font-size: 13px; color: var(--mute); text-align: right; }
	.total strong { font-size: 22px; color: var(--ink); display: block; }
	.map { position: relative; width: 100%; background: var(--paper-2); }
	.tile {
		position: absolute; overflow: hidden; border: 0; padding: 6px 7px; cursor: pointer; text-align: left;
		background: var(--c); color: var(--t); display: flex; flex-direction: column; justify-content: flex-start; gap: 2px;
		transition: left 0.5s, top 0.5s, width 0.5s, height 0.5s, filter 0.2s;
	}
	.tile.leaf { cursor: default; }
	.tile:hover { filter: brightness(1.1); }
	.tname { font-size: 13px; font-weight: 600; line-height: 1.15; }
	.tval { font-size: 12px; font-variant-numeric: tabular-nums; }
	.note { font-size: 13px; color: var(--ink-2); background: var(--paper-2); padding: 8px 10px; margin: 10px 0 0; }
	.listhead { font-size: 15px; margin: 28px 0 6px; }
	.list { list-style: none; padding: 0; margin: 0; font-size: 14px; }
	.list li { border-top: 1px solid var(--rule); padding: 8px 0 8px 12px; border-left: 4px solid var(--c); }
	.row { display: grid; grid-template-columns: 1fr auto 44px; gap: 10px; align-items: baseline; }
	.name { font-weight: 600; }
	.link { font: inherit; font-weight: 600; text-align: left; background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; color: var(--ink); }
	.amt { font-variant-numeric: tabular-nums; font-weight: 600; }
	.pct { color: var(--mute); text-align: right; font-variant-numeric: tabular-nums; }
	.sub { margin: 3px 0 0; font-size: 12.5px; color: var(--ink-2); }
	.src { font-size: 12px; color: var(--mute); margin-top: 18px; }
</style>
