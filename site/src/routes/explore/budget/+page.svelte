<script lang="ts">
	// Toronto reads as a story (money in, money out), then Part 3 ranks every line; Ontario is the ranked list alone.
	import { tick } from 'svelte';
	import { SvelteSet } from 'svelte/reactivity';
	import Ranked from '#lib/components/Ranked.svelte';
	import { categoryColor } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { BudgetNode } from '#lib/types.ts';
	import type { PageProps } from './$types';
	import { siteData } from '#lib/context.ts';
	import Fact from '#lib/components/Fact.svelte';

	let { data }: PageProps = $props();
	const { facts } = siteData();
	// Where Toronto's operating money comes from, straight from the City's Budget Summary (Figure 1).
	// Lower-case a label mid-sentence, but keep acronyms like TTC.
	const lc = (t: string) => (/^[A-Z][A-Z]/.test(t) ? t : t[0].toLowerCase() + t.slice(1));
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
	// Money-flow: the five biggest sources plus 'smaller sources', each a block on the left whose
	// ribbon runs into one bar for the whole budget. Only property taxes get a colour.
	const FH = 250, TOP = 40;
	const BAR = { x0: 470, x1: 500 };
	const SHADES = ['#d9822b', '#41566e', '#5f7891', '#7d93a8', '#9caebf', '#bcc8d3'];
	const top5 = sources.slice(0, 5);
	const flowRest = sources.slice(5);
	// Money in: the five biggest sources plus 'smaller sources', ribbons into the City bar.
	const flowRows = (() => {
		const items = [...top5.map((x) => ({ id: x.id, label: x.label, v: x.v })), { id: 'smaller', label: 'Smaller sources', v: flowRest.reduce((a, x) => a + x.v, 0) }];
		const gap = 8, usable = FH - gap * (items.length - 1);
		let y = TOP, yR = TOP;
		return items.map((it, i) => {
			const h = (it.v / tor) * usable, hR = (it.v / tor) * FH;
			const row = { ...it, color: SHADES[i], hi: i === 0, per: Math.round((it.v / tor) * 100), y, h,
				ribbon: `M272 ${y} C380 ${y} 380 ${yR} ${BAR.x0} ${yR} L${BAR.x0} ${yR + hR} C380 ${yR + hR} 380 ${y + h} 272 ${y + h} Z` };
			y += h + gap; yR += hR;
			return row;
		});
	})();

	// svelte-ignore state_referenced_locally
	let levelKey = $state(data.trees[0]?.key ?? 'toronto');
	const level = $derived(data.trees.find((t) => t.key === levelKey) ?? data.trees[0]);
	const root = $derived(level?.tree as BudgetNode);
	// Money out: the City's top spending areas (same colours as the boxes below), ribbons out of the bar.
	const outRows = $derived.by(() => {
		if (levelKey !== 'toronto' || !root?.children) return [];
		const kids = root.children.filter((c) => c.gross > 0).sort((a, b) => b.gross - a.gross);
		const tot = kids.reduce((a, c) => a + c.gross, 0);
		const shown = kids.slice(0, 7);
		const items: { node?: BudgetNode; label: string; v: number; color: string }[] = [
			...shown.map((n) => ({ node: n, label: n.name, v: n.gross, color: categoryColor(n.category) })),
			{ label: 'Everything else', v: kids.slice(7).reduce((a, c) => a + c.gross, 0), color: '#c9c4b9' }
		];
		const gap = 6, usable = FH - gap * (items.length - 1);
		let y = TOP, yL = TOP;
		return items.map((it) => {
			const h = (it.v / tot) * usable, hL = (it.v / tot) * FH;
			const row = { ...it, per: Math.round((it.v / tot) * 100), y, h,
				ribbon: `M${BAR.x1} ${yL} C600 ${yL} 600 ${y} 700 ${y} L700 ${y + h} C600 ${y + h} 600 ${yL + hL} ${BAR.x1} ${yL + hL} Z` };
			y += h + gap; yL += hL;
			return row;
		});
	});

	function choose(key: string) {
		levelKey = key;
		opened.clear();
	}
	let mapEl: HTMLElement | undefined = $state();
	// Toronto reads as one story: part 1 (money in), part 2 (money out), part 3 (the boxes).
	const storyOn = $derived(levelKey === 'toronto' && !!tor);
	// One stream lit at a time ('in:<id>' or 'out:<label>'): the rest of its chart dims, and the City bar reads out its amount.
	let hot = $state<string | null>(null);
	const hotIn = $derived(flowRows.find((r) => `in:${r.id}` === hot));
	const hotOut = $derived(outRows.find((r) => `out:${r.label}` === hot));
	const dim = (key: string, base: number) => (hot === key ? 0.85 : hot?.[0] === key[0] ? 0.12 : base);
	let reduceMotion = $state(false);
	$effect(() => { reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches; });
	// Each chart pours its money in the first time it scrolls into view.
	function reveal(node: Element) {
		const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { node.classList.add('seen'); io.disconnect(); } }, { threshold: 0.2 });
		io.observe(node);
		return { destroy: () => io.disconnect() };
	}
	// For the story text: the biggest spending areas and what they add up to.
	const top3 = $derived(outRows.filter((r) => r.node).slice(0, 3));
	const top3per = $derived(Math.round(top3.reduce((a, r) => a + r.v, 0) / outRows.reduce((a, r) => a + r.v, 0) * 100));
	// Rows opened in Part 3. The story's spending areas open their row there and scroll to it.
	const opened = new SvelteSet<string>();
	async function open(n: BudgetNode, fromList = false) {
		opened.add(n.id);
		if (!fromList) return;
		await tick();
		document.getElementById(`row-${n.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
	}
</script>


<svelte:head>
	<title>Explore the budget · The Platform</title>
	<meta name="description" content="Tap through Toronto's and Ontario's budgets, from the big categories down to individual programs." />
</svelte:head>

<div class="wide page">
	<div class="top">
		{#if storyOn}
			<!-- The Toronto story opens with its number, in the same row as the tabs. -->
			<div class="hl">
				<p class="kicker">Toronto · 2026 budget</p>
				<h1 class="rest">Following Toronto's money</h1>
				<p class="dek sans">The City plans to spend <b class="mega"><Fact id="toronto.operating.2026.gross" short /></b> this year. Here's where it comes from, and where it goes.</p>
			</div>
		{:else}
			<div>
				<p class="kicker">Explore the budget</p>
				<h1>Open up the budget yourself</h1>
			</div>
		{/if}
		{#if level}
			<div class="tabs sans" role="tablist">
				{#each data.trees as t (t.key)}
					<button role="tab" aria-selected={levelKey === t.key} onclick={() => choose(t.key)}>{t.label}</button>
				{/each}
			</div>
		{/if}
	</div>

	{#if !level}
		<p class="sans">Budget data is being prepared.</p>
	{:else}


		{#if storyOn}
			<!-- One big number, then part 1 (money in) and part 2 (money out), then the boxes. -->
			<article class="story">

				<section class="part warm" id="from">
					<div class="phead">
						<span class="chip">Part 1</span>
						<h3>Where it comes from</h3>
						<p>For every dollar the City brings in, here's who chips in.</p>
					</div>
					<div class="stickers sans">
						{#each flowRows.slice(0, 3) as r (r.id)}
							{@const k = `in:${r.id}`}
							<button class="stk" class:on={hot === k} style="--c:{r.color}" onmouseenter={() => (hot = k)} onmouseleave={() => (hot = null)} onfocus={() => (hot = k)} onblur={() => (hot = null)} onclick={() => (hot = hot === k ? null : k)}>
								<b>{r.per}¢</b><span>{r.label}</span><small>{money(r.v, 'short')}</small>
							</button>
						{/each}
					</div>
					<figure class="chart" use:reveal>
						<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
						<svg viewBox="-20 0 740 {FH + TOP + 8}" role="group" aria-label="Where the City of Toronto's 2026 operating money comes from" onmouseleave={() => (hot = null)}>
							<defs>
								<!-- Soft stripes that slide along a lit stream, so the money looks like it's moving. -->
								<pattern id="moving" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="skewX(-30)">
									<rect width="6" height="22" fill="#fff" opacity="0.28" />
									{#if !reduceMotion}<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="22 0" dur="0.8s" repeatCount="indefinite" additive="sum" />{/if}
								</pattern>
							</defs>
							<text x="250" y="16" class="col" text-anchor="end">Sources</text>
							<text x={(BAR.x0 + BAR.x1) / 2} y="16" class="col strong" text-anchor="middle">The City</text>
							{#each flowRows as r, i (r.id)}
								{@const k = `in:${r.id}`}
								<!-- Tapping a source lights it on touch screens; the same numbers are in the list for keyboards. -->
								<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
								<g class="src" class:on={hot === k} style="--i:{i}" onmouseenter={() => (hot = k)} onclick={() => (hot = hot === k ? null : k)}>
									<path d={r.ribbon} fill={r.color} opacity={dim(k, r.hi ? 0.55 : 0.3)} class="rib in" />
									{#if hot === k}<path d={r.ribbon} fill="url(#moving)" class="flowing" />{/if}
									<rect x="260" y={r.y} width="12" height={r.h} rx="3" fill={r.color} />
									<text x="250" y={r.y + r.h / 2} class="lbl" class:hi={r.hi} text-anchor="end" dominant-baseline="middle">{r.label}<tspan class="amt" dx="6">{r.per}¢</tspan></text>
								</g>
							{/each}
							<rect x={BAR.x0} y={TOP} width={BAR.x1 - BAR.x0} height={FH} rx="6" fill="#1f2a37" />
							<g class="readout" aria-live="polite" transform="translate({BAR.x1 + 18} {TOP + FH / 2})">
								<path d="M0 0 l10 -9 v18 Z" class="tip" style="--rc:{hotIn?.color ?? '#1f2a37'}" />
								<rect x="9" y="-28" width="150" height="56" rx="12" style="--rc:{hotIn?.color ?? '#1f2a37'}" />
								<text x="84" y="-3" class="big" text-anchor="middle">{money(hotIn?.v ?? tor, 'short')}</text>
								<text x="84" y="16" class="small" text-anchor="middle">{hotIn ? `${hotIn.per}¢ of every dollar` : 'comes in each year'}</text>
							</g>
						</svg>
						<ul class="flowlist">{#each flowRows as r (r.id)}<li class:hi={r.hi}><i style="background:{r.color}"></i><span>{r.label}</span><b>{r.per}¢</b></li>{/each}</ul>
						<figcaption class="cn">Cents of every dollar. {#each flowRest as x, i (x.id)}{i ? ', ' : 'Smaller sources: '}{lc(x.label)} {Math.round((x.v / tor) * 100)}¢{/each}. Source: <a href={facts['toronto.revenue.2026.property-tax']?.primary.url} target="_blank" rel="noopener">City Budget Summary, p. 10 ↗</a></figcaption>
					</figure>
					<a class="next" href="#to">Next · <b>Part 2: Where it goes</b> <span aria-hidden="true">↓</span></a>
				</section>

				<section class="part cool" id="to">
					<div class="phead">
						<span class="chip">Part 2</span>
						<h3>Where it goes</h3>
						<p>For every dollar the City spends, here's where it lands.</p>
					</div>
					<div class="stickers sans">
						{#each top3 as r (r.label)}
							{@const k = `out:${r.label}`}
							{@const n = r.node!}
							<button class="stk" class:on={hot === k} style="--c:{r.color}" onmouseenter={() => (hot = k)} onmouseleave={() => (hot = null)} onfocus={() => (hot = k)} onblur={() => (hot = null)} onclick={() => open(n, true)}>
								<b>{r.per}¢</b><span>{r.label}</span><small>{money(r.v, 'short')}</small><i aria-hidden="true">›</i>
							</button>
						{/each}
					</div>
					<figure class="chart" use:reveal>
						<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
						<svg viewBox="255 0 820 {FH + TOP + 8}" role="group" aria-label="Where the City of Toronto's 2026 operating money goes" onmouseleave={() => (hot = null)}>
							<text x={(BAR.x0 + BAR.x1) / 2} y="16" class="col strong" text-anchor="middle">The City</text>
							<text x="712" y="16" class="col go">Spending areas · tap one</text>
							{#each outRows as r, i (r.label)}
								{@const k = `out:${r.label}`}
								<path d={r.ribbon} fill={r.color} opacity={dim(k, 0.45)} class="rib out-rib" style="--i:{i}" role="presentation" onmouseenter={() => (hot = k)} />
								{#if hot === k}<path d={r.ribbon} fill="url(#moving)" class="flowing" />{/if}
								{#if r.node}
									{@const n = r.node}
									<g
										class="out" class:on={hot === k} role="button" tabindex="0" aria-label="{r.label}, {r.per} cents of every dollar. Open it."
										onclick={() => open(n, true)}
										onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(n, true); } }}
										onmouseenter={() => (hot = k)} onfocus={() => (hot = k)} onblur={() => (hot = null)}
									>
										<rect x="718" y={r.y + r.h / 2 - Math.min(14, r.h / 2 + 2)} width={r.label.length * 7.6 + 74} height={Math.min(28, r.h + 4)} rx={Math.min(14, r.h / 2 + 2)} class="pill" />
										<rect x="700" y={r.y} width="12" height={r.h} rx="3" fill={r.color} />
										<text x="730" y={r.y + r.h / 2} class="lbl" dominant-baseline="middle">{r.label}<tspan class="amt" dx="6">{r.per}¢</tspan><tspan class="arrow" dx="6">›</tspan></text>
									</g>
								{:else}
									<!-- svelte-ignore a11y_no_static_element_interactions -->
									<g class="out still" class:on={hot === k} onmouseenter={() => (hot = k)}>
										<rect x="700" y={r.y} width="12" height={r.h} rx="3" fill={r.color} />
										<text x="730" y={r.y + r.h / 2} class="lbl" dominant-baseline="middle">{r.label}<tspan class="amt" dx="6">{r.per}¢</tspan></text>
									</g>
								{/if}
							{/each}
							<rect x={BAR.x0} y={TOP} width={BAR.x1 - BAR.x0} height={FH} rx="6" fill="#1f2a37" />
							<g class="readout" aria-live="polite" transform="translate({BAR.x0 - 18} {TOP + FH / 2})">
								<path d="M0 0 l-10 -9 v18 Z" class="tip" style="--rc:{hotOut?.color ?? '#1f2a37'}" />
								<rect x="-159" y="-28" width="150" height="56" rx="12" style="--rc:{hotOut?.color ?? '#1f2a37'}" />
								<text x="-84" y="-3" class="big" text-anchor="middle">{money(hotOut?.v ?? tor, 'short')}</text>
								<text x="-84" y="16" class="small" text-anchor="middle">{hotOut ? `${hotOut.per}¢ of every dollar` : 'goes out each year'}</text>
							</g>
						</svg>
						<ul class="flowlist">
							{#each outRows as r (r.label)}
								{#if r.node}
									{@const n = r.node}
									<li><button class="tap" onclick={() => open(n, true)}><i style="background:{r.color}"></i><span>{r.label}</span><b>{r.per}¢ ›</b></button></li>
								{:else}
									<li><i style="background:{r.color}"></i><span>{r.label}</span><b>{r.per}¢</b></li>
								{/if}
							{/each}
						</ul>
						<figcaption class="cn">Cents of every dollar the City spends, by spending area.</figcaption>
					</figure>
					<a class="next" href="#boxes">Next · <b>Part 3: Every program, ranked</b> <span aria-hidden="true">↓</span></a>
				</section>

			</article>
		{/if}

		<section class="explore" class:part={storyOn} id="boxes">
		{#if storyOn}
			<div class="phead">
				<span class="chip">Part 3</span>
				<h3>Every program, ranked</h3>
				<p>Biggest first. Tap a row to see the programs inside it.</p>
			</div>
		{/if}
		{#if !storyOn}
			<p class="lvlsub sans">{root.name} · {money(root.gross, 'short')} · {root.basis}{root.basis?.includes(root.year ?? '') ? '' : `, ${root.year}`}</p>
		{/if}
		{#if root.note}<p class="note sans">{root.note}</p>{/if}
		<div class="ranked" bind:this={mapEl}><Ranked parent={root} {opened} /></div>
		{#if root.source}
			<p class="src sans">
				Source: <a href={root.source.url} target="_blank" rel="noopener">{root.source.title}</a>{#if root.source.locator}, {root.source.locator}{/if}.
				How we grouped lines into categories: <a href="/sources/#categories">sources and methods</a>.
			</p>
		{/if}
		</section>
	{/if}
</div>

<style>
	.page { margin-top: 16px; }
	.top { display: flex; justify-content: space-between; align-items: center; gap: 12px 24px; flex-wrap: wrap; padding-bottom: 4px; margin-bottom: 14px; }
	.top .kicker { margin: 0; }
	h1 { font-size: clamp(24px, 3vw, 32px); margin: 4px 0 0; }
	.tabs { display: flex; gap: 2px; background: #fff; border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); border-radius: 999px; padding: 3px; }
	.tabs button { font: inherit; font-size: 14px; font-weight: 700; background: none; border: 0; border-radius: 999px; padding: 5px 16px; cursor: pointer; color: var(--ink-2); }
	.tabs button[aria-selected='true'] { color: #fff; background: var(--ink); }
	.explore.part { background: #fff; scroll-margin-top: 70px; }
	.ranked { margin-top: 8px; }
	.lvlsub { margin: 8px 0 0; font-size: 13.5px; color: var(--mute); }
	.explore .phead { margin-bottom: 12px; }
	/* The way on to the next part, at the bottom of each panel. */
	.next { display: flex; align-items: center; justify-content: center; gap: 6px; margin: 14px auto 0; width: fit-content; font-family: var(--sans); font-size: 14px; color: var(--ink); text-decoration: none; background: #fff; border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); border-radius: 999px; padding: 6px 16px; }
	.next:hover { color: var(--ink); border-color: var(--ink); }
	.next span { color: var(--red); font-weight: 800; display: inline-block; animation: nudge 1.4s ease-in-out infinite; }
	/* The house style (see app.css): display headings, thin outlines, small hard shadows, tinted panels. */
	.story { font-family: var(--sans); max-width: 1080px; margin: 0 auto 40px; }
	/* The Toronto opener: the number and its sentence, sharing the top row with the tabs. */
	.hl { display: flex; flex-direction: column; gap: 2px; }
	.hl .kicker { margin: 0; }
	.rest { font-size: clamp(30px, 4.2vw, 42px); line-height: 1.08; margin: 6px 0 0; }
	.dek { color: var(--ink-2); font-size: 18px; margin: 8px 0 0; }
	.mega { color: var(--ink); white-space: nowrap; }
	.mega :global(.value) { color: inherit; border: 0; }
	.part { scroll-margin-top: 80px; margin-top: 20px; padding: clamp(16px, 2.4vw, 24px); border: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); border-radius: 20px; }
	/* The parts are stops on one line: a short red track joins each panel to the next. */
	.story .part, .explore.part { position: relative; margin-top: 40px; }
	.story .part::before, .explore.part::before { content: ''; position: absolute; left: 50%; top: -41px; width: 4px; height: 40px; margin-left: -2px; background: var(--red); border-radius: 2px; }
	.story .part:first-child::before { display: none; }
	.part.warm { background: var(--warm); }
	.part.cool { background: var(--cool); }
	.phead { display: flex; flex-wrap: wrap; align-items: center; column-gap: 12px; }
	.chip { display: inline-block; font-family: var(--sans); background: var(--ink); color: #fff; border-radius: 999px; padding: 3px 12px; font-weight: 700; font-size: 13px; }
	.phead h3 { font-size: clamp(22px, 2.6vw, 28px); margin: 0; }
	.phead p { flex: 0 0 100%; font-family: var(--sans); font-size: 14.5px; color: var(--ink-2); margin: 4px 0 0; line-height: 1.45; }
	/* The three biggest, as one row of chips; the chart below shows the rest. */
	.stickers { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 10px; }
	.stk { font: inherit; display: flex; align-items: baseline; gap: 8px; color: var(--ink); background: color-mix(in srgb, var(--c) 22%, #fff); border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); border-radius: 999px; padding: 4px 12px; text-align: left; transition: transform 0.15s, box-shadow 0.15s, background 0.15s; cursor: pointer; }
	.stk:hover, .stk.on, .stk:focus-visible { border-color: var(--ink); background: color-mix(in srgb, var(--c) 40%, #fff); outline: none; }
	.stk b { font-size: 17px; font-weight: 800; line-height: 1; }
	.stk span { font-size: 13.5px; font-weight: 700; }
	.stk small { font-family: var(--sans); font-size: 12px; color: var(--ink-2); }
	.stk i { font-style: normal; font-weight: 700; color: var(--red); }
	.chart { margin: 0; background: #fff; border-radius: 14px; padding: 10px 16px 8px; }
	.chart svg { width: 100%; height: auto; display: block; max-height: 42vh; max-width: 680px; margin: 0 auto; }
	.chart .lbl { font-size: 15px; font-weight: 600; fill: var(--ink-2); transition: opacity 0.2s; }
	.chart .lbl.hi { fill: #b5631a; font-weight: 800; font-size: 16px; }
	.chart .amt { font-size: 12.5px; fill: var(--mute); }
	.chart .col { font-size: 11.5px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; fill: var(--mute); }
	.chart .col.strong { fill: var(--ink); font-size: 13px; }
	.chart .col.go { fill: #da251d; }
	.chart svg:has(.on) .src:not(.on) .lbl, .chart svg:has(.on) .out:not(.on) .lbl { opacity: 0.4; }
	.chart .src, .chart .out { cursor: pointer; }
	.chart .out.still { cursor: default; }
	.chart .pill { fill: #f4f1ea; stroke: #e2ddd2; transition: fill 0.15s; }
	.chart .out.on .pill { fill: #1f2a37; stroke: #1f2a37; }
	.chart .out.on .lbl, .chart .out.on .amt, .chart .out.on .arrow { fill: #fff; }
	.chart .out.still.on .lbl, .chart .out.still.on .amt { fill: var(--ink); }
	.chart .out:focus { outline: none; }
	.chart .out:focus-visible .pill { stroke: #da251d; stroke-width: 2.5; }
	.chart .arrow { font-size: 16px; font-weight: 700; fill: var(--ink-2); }
	.chart .rib { transition: opacity 0.2s; }
	.chart .flowing, .readout { pointer-events: none; }
	.readout rect { fill: #1f2a37; stroke: var(--rc); stroke-width: 2; transition: stroke 0.2s; }
	.readout .tip { fill: var(--rc); transition: fill 0.2s; }
	.readout .big { fill: #fff; font-size: 21px; font-weight: 800; font-variant-numeric: tabular-nums; }
	.readout .small { fill: #c9d1da; font-size: 12px; font-weight: 600; }
	/* Each chart's streams pour out from the City side the first time you scroll to it. */
	@media (prefers-reduced-motion: no-preference) {
		.chart .rib { transform-box: view-box; }
		.chart .rib.in { transform-origin: 272px 0; }
		.chart .out-rib { transform-origin: 500px 0; }
		.chart:not(:global(.seen)) .rib { transform: scaleX(0); }
		.chart:global(.seen) .rib { animation: pour 0.8s cubic-bezier(0.3, 0.7, 0.3, 1) both; animation-delay: calc(var(--i) * 80ms); }
		.chart:not(:global(.seen)) .readout { opacity: 0; }
		.chart:global(.seen) .readout { animation: pop 0.4s 0.5s both; }
	}
	@keyframes pour { from { transform: scaleX(0); } }
	@keyframes pop { from { opacity: 0; } }
	.cn { font-size: 12.5px; color: var(--mute); margin: 8px 0 0; line-height: 1.5; }
	.cn a { color: inherit; }
	@keyframes nudge { 50% { transform: translateY(4px); } }
	@media (prefers-reduced-motion: reduce) { .next span { animation: none; } }
	.flowlist { display: none; list-style: none; padding: 0; margin: 0; gap: 6px; }
	@media (max-width: 640px) {
		.stickers { flex-wrap: nowrap; overflow-x: auto; margin-right: -16px; padding-right: 16px; scrollbar-width: none; }
		.stk { flex: none; padding: 4px 11px; }
		.stk b { font-size: 15px; } .stk span { font-size: 13px; white-space: nowrap; }
		.chart svg { display: none; }
		.flowlist { display: grid; }
		.flowlist li { display: grid; grid-template-columns: 12px 1fr auto; gap: 8px; align-items: center; font-size: 14px; }
		.flowlist li.hi { font-weight: 800; color: #b5631a; }
		.flowlist i { width: 12px; height: 12px; border-radius: 3px; }
		.flowlist li:has(.tap) { display: block; }
		.flowlist .tap { display: grid; grid-template-columns: 12px 1fr auto; gap: 8px; align-items: center; width: 100%; font: inherit; font-size: 14px; text-align: left; color: inherit; background: #f4f1ea; border: 1px solid #e2ddd2; border-radius: 8px; padding: 7px 10px; cursor: pointer; }
		.chart { padding: 12px; }
		/* Phones: the list repeats the chips, so the chips go; panels use the page margin, and the
		   white box inside each panel drops away, so there's one frame instead of three. */
		.stickers { display: none; }
		.part { margin-left: -8px; margin-right: -8px; padding: 22px 14px; border-radius: 16px; }
		.story .chart { background: none; padding: 6px 0 0; }
		.phead p { font-size: 15px; margin-top: 6px; }
		.flowlist { gap: 10px; }
		.flowlist li { font-size: 15px; }
		.flowlist li:not(:has(.tap)) { padding: 0 15px; }
		.flowlist .tap { font-size: 15px; padding: 12px 14px; background: #fff; border-color: color-mix(in srgb, var(--ink) 10%, transparent); border-radius: 12px; }
		.cn { font-size: 13px; margin-top: 14px; }
		.next { margin-top: 20px; }
	}
	.note { font-size: 13px; color: var(--ink-2); background: var(--paper-2); border-radius: 10px; padding: 8px 12px; margin: 6px 0 0; }
	.go { color: var(--red); font-weight: 700; }
	.amt { grid-area: amt; text-align: right; font-variant-numeric: tabular-nums; font-weight: 700; }
	.src { font-size: 12px; color: var(--mute); margin-top: 18px; }
</style>
