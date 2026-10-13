<script lang="ts">
	// Zoomable treemap, one level at a time: tap a tile to open it, use the breadcrumb to go back.
	// The list under the map holds the same data for screen readers and small phones.
	import { hierarchy, treemap, treemapSquarify } from 'd3-hierarchy';
	import { categoryColor } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { BudgetNode } from '#lib/types.ts';
	import type { PageProps } from './$types';
	import { siteData } from '#lib/context.ts';
	import Fact from '#lib/components/Fact.svelte';

	let { data }: PageProps = $props();
	const { facts } = siteData();
	// Where Toronto's operating money comes from, straight from the City's Budget Summary (Figure 1).
	const fv = (id: string) => Number(facts[id]?.value ?? 0);
	const tor = fv('toronto.operating.2026.gross');
	const sources = [
		['property-tax', 'Property taxes', '#d9822b'],
		['fed-prov', 'Province and Ottawa', '#2f5d9b'],
		['rate-programs', 'Water, garbage and parking bills', '#3f7f74'],
		['reserves', 'City savings (reserves)', '#7a5c99'],
		['transit-fares', 'TTC fares', '#da251d'],
		['other', 'Other', '#b9b3a6'],
		['user-fees', 'User fees and fines', '#4a8c5c'],
		['land-transfer-tax', 'Land transfer tax', '#c9a227'],
		['investment-income', 'Investment income', '#8a857b']
	].map(([k, label, color]) => ({ id: `toronto.revenue.2026.${k}`, label, color, v: fv(`toronto.revenue.2026.${k}`) }));

	// svelte-ignore state_referenced_locally
	let levelKey = $state(data.trees[0]?.key ?? 'toronto');
	const level = $derived(data.trees.find((t) => t.key === levelKey) ?? data.trees[0]);
	let path = $state<BudgetNode[]>([]);
	const root = $derived(level?.tree as BudgetNode);
	const current = $derived(path.at(-1) ?? root);
	const category = $derived([...path].reverse().find((n) => n.category)?.category);

	function choose(key: string) {
		levelKey = key;
		path = [];
		leafNote = null;
	}
	let mapEl: HTMLDivElement | undefined = $state();
	// A box with nothing inside: say so, instead of a tap that seems broken.
	let leafNote = $state<BudgetNode | null>(null);
	function open(n: BudgetNode, fromList = false) {
		if (!n.children?.length) { leafNote = n; return; }
		leafNote = null;
		path = [...path, n];
		if (fromList) mapEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
	}
	const back = (i: number) => { path = path.slice(0, i); leafNote = null; };

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
	<meta name="description" content="Tap through Toronto's and Ontario's budgets, from the big categories down to individual programs." />
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

		{#if levelKey === 'toronto' && !path.length && tor}
			<div class="comes sans">
				<p class="ct">Where Toronto's <Fact id="toronto.operating.2026.gross" /> comes from</p>
				<div class="stack">
					{#each sources as x (x.id)}<span style="width:{(x.v / tor) * 100}%;background:{x.color}" title={x.label}></span>{/each}
				</div>
				<ul class="keys">
					{#each sources as x (x.id)}<li><i style="background:{x.color}"></i>{x.label} <Fact id={x.id} /> <span>({Math.round((x.v / tor) * 100)}%)</span></li>{/each}
				</ul>
				<p class="cn">Property taxes pay for under a third of it. The boxes below show where it all goes. Source: City of Toronto 2026 Budget Summary, p. 10.</p>
			</div>
		{/if}

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
		{#if leafNote}
			<p class="leafnote sans" aria-live="polite"><b>{leafNote.name}</b>: {money(leafNote.gross)}. That's as detailed as the published budget gets for this one, so there's nothing smaller inside it.{#if leafNote.source} <a href={leafNote.source.url} target="_blank" rel="noopener">See the source ↗</a>{/if}</p>
		{/if}
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
	.tile.leaf { cursor: help; }
	.comes { background: #fff; border: 1px solid var(--rule); border-radius: 12px; padding: 12px 16px; margin: 0 0 14px; }
	.ct { margin: 0 0 8px; font-weight: 700; font-size: 14.5px; }
	.stack { display: flex; height: 18px; border-radius: 8px; overflow: hidden; gap: 2px; }
	.keys { list-style: none; padding: 0; margin: 8px 0 0; display: flex; flex-wrap: wrap; gap: 4px 18px; font-size: 13px; }
	.keys i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; }
	.keys span, .cn { color: var(--mute); }
	.cn { font-size: 12.5px; margin: 6px 0 0; }
	.leafnote { margin: 10px 0 0; font-size: 14px; background: #fff; border: 1px solid var(--rule); border-left: 4px solid var(--ink); border-radius: 8px; padding: 10px 14px; }
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
