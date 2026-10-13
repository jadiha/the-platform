<script lang="ts">
	import Fact from '#lib/components/Fact.svelte';
	import { siteData } from '#lib/context.ts';
	import { categoryLabel } from '#lib/categories.ts';
	import { formatDate, formatFact, STATUS_LABEL } from '#lib/format.ts';
	import type { FactStatus } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { facts } = siteData();

	const STATUSES: FactStatus[] = ['verified', 'single', 'disagree', 'reported'];
	let filter = $state<FactStatus | 'all'>('all');
	const factRows = $derived(
		Object.entries(facts)
			.filter(([, f]) => filter === 'all' || f.status === filter)
			.sort(([a], [b]) => a.localeCompare(b))
	);
	const counts = $derived(Object.fromEntries(STATUSES.map((s) => [s, Object.values(facts).filter((f) => f.status === s).length])));

	// Corrections log: newest first. Add an entry whenever a published number changes.
	const CORRECTIONS: { date: string; what: string }[] = [];
</script>

<svelte:head>
	<title>Sources and methods · The 6ix Votes</title>
	<meta name="description" content="Every dataset behind The 6ix Votes, how we grouped spending into categories, and what we know we can't show yet." />
</svelte:head>

<div class="wrap page">
	<p class="kicker">Sources and methods</p>
	<h1>Where every number comes from</h1>
	<p class="dek">
		We only use official government documents and open data as the source of a number. News reports are used only to double-check them.
		Everything here, including the code, is public so anyone can check our work.
	</p>

	<h2>How we rate each number</h2>
	<ul class="rules sans">
		<li><strong class="st-verified">{STATUS_LABEL.verified}</strong>: from an official source, and an independent source agrees.</li>
		<li><strong class="st-single">{STATUS_LABEL.single}</strong>: from an official source; we haven't found an independent check yet.</li>
		<li><strong class="st-disagree">{STATUS_LABEL.disagree}</strong>: official sources give different numbers. We show both and explain why.</li>
		<li><strong class="st-reported">{STATUS_LABEL.reported}</strong>: reported in the news but not in any official document. Never presented as fact.</li>
	</ul>
	<p>
		We also say whether each number is a <strong>budget</strong> (a plan) or an <strong>actual</strong> (what was really spent), and whether it is
		<strong>gross</strong> (the total cost) or <strong>net</strong> (the part the government pays itself). Charts show gross unless they say otherwise.
	</p>
</div>

<div class="wide page">
	<h2>Datasets</h2>
	<p class="sans small">Downloaded unchanged by our pipeline. The fingerprint (SHA-256) lets anyone confirm we used the same file.</p>
	<div class="scroll">
		<table class="sans">
			<thead><tr><th>Dataset</th><th>Downloaded</th><th>Fingerprint</th></tr></thead>
			<tbody>
				{#each data.sources as s (s.id)}
					<tr>
						<td><a href={s.url} target="_blank" rel="noopener">{s.title}</a></td>
						<td class="nowrap">{formatDate(s.fetchedAt.slice(0, 10))}</td>
						<td class="mono" title={s.sha256}>{s.sha256?.slice(0, 12)}…</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<h2 id="facts">Every number in the story</h2>
	<div class="filters sans" role="group" aria-label="Filter by status">
		<button aria-pressed={filter === 'all'} onclick={() => (filter = 'all')}>All ({Object.keys(facts).length})</button>
		{#each STATUSES as s}
			<button aria-pressed={filter === s} onclick={() => (filter = s)}>{STATUS_LABEL[s]} ({counts[s]})</button>
		{/each}
	</div>
	<div class="scroll">
		<table class="sans">
			<thead><tr><th>What</th><th>Value</th><th>Status</th><th>Official source</th></tr></thead>
			<tbody>
				{#each factRows as [id, f] (id)}
					<tr {id}>
						<td>{f.label}{#if f.basis}<span class="basis">{f.basis}</span>{/if}</td>
						<td class="nowrap num">{formatFact(f)}</td>
						<td class="nowrap st-{f.status}">{STATUS_LABEL[f.status]}</td>
						<td>
							<a href={f.primary.url} target="_blank" rel="noopener">{f.primary.title}</a>{#if f.primary.locator}<span class="basis">{f.primary.locator}</span>{/if}
							{#if f.note}<span class="note">{f.note}</span>{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<div class="wrap page">
	<h2 id="categories">How we grouped spending</h2>
	<p>
		Toronto and Ontario organize their budgets differently. To compare them, we put every budget line into one shared set of categories.
		These are our choices, so here they are in full. If you think a line belongs somewhere else, tell us.
	</p>
	{#each [['toronto', 'City of Toronto programs'], ['ontario', 'Ontario ministries']] as [key, title] (key)}
		<details>
			<summary class="sans">{title} ({data.mappings[key as 'toronto' | 'ontario'].length} lines)</summary>
			<table class="sans compact">
				<thead><tr><th>Budget line</th><th>Our category</th><th>Notes</th></tr></thead>
				<tbody>
					{#each data.mappings[key as 'toronto' | 'ontario'] as m (m.original_line)}
						<tr>
							<td>{m.original_line}</td>
							<td class="nowrap">{m.category === 'EXCLUDE' ? 'Not counted' : categoryLabel(m.category)}</td>
							<td class="basis-cell">{m.notes}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</details>
	{/each}

	<h2 id="gaps">What we can't show (yet)</h2>
	<ul class="gaps">
		<li>
			<strong>Most city building money can't be traced to a neighbourhood.</strong> About <Fact id="scarborough.capital.city-wide-share" /> of Toronto's 10-year capital plan is coded
			“City Wide” (TTC vehicles, water mains, police systems). Scarborough benefits from that money, but nobody publishes how much.
		</li>
		<li>
			<strong>Toronto's 2026 spending by detailed line isn't in Open Data yet.</strong> We use the 2026 Budget Summary PDF for 2026,
			and the Open Data files for earlier years. The two don't use exactly the same totals, so we never put them in the same chart.
		</li>
		<li>
			<strong>Per-school data</strong> (repair backlogs, new builds, closures) is planned for a later version.
		</li>
		<li><strong>Contracts, lobbying and full council voting records</strong> are a separate future project.</li>
	</ul>
	{#if data.trendNotes.length}
		<details>
			<summary class="sans">Notes on the five-year trend charts</summary>
			<ul class="small">
				{#each data.trendNotes as n}<li>{n}</li>{/each}
			</ul>
		</details>
	{/if}

	<h2 id="corrections">Corrections</h2>
	<p>
		Spot a mistake? Tell us. We fix errors quickly and list every change here with the date.
	</p>
	{#if CORRECTIONS.length}
		<ul class="sans small">
			{#each CORRECTIONS as c}<li><strong>{formatDate(c.date)}:</strong> {c.what}</li>{/each}
		</ul>
	{:else}
		<p class="sans small muted">No corrections yet.</p>
	{/if}
</div>

<style>
	.page { margin-top: 44px; }
	h1 { font-size: clamp(32px, 5vw, 46px); margin: 8px 0 12px; }
	h2 { font-size: 26px; margin: 44px 0 12px; scroll-margin-top: 80px; }
	.dek { color: var(--ink-2); font-size: 20px; }
	.rules { font-size: 15px; display: grid; gap: 6px; padding-left: 18px; }
	.small { font-size: 13px; }
	.muted { color: var(--mute); }
	.scroll { overflow-x: auto; }
	table { width: 100%; border-collapse: collapse; font-size: 13px; }
	th { text-align: left; border-bottom: 1px solid var(--ink); padding: 6px 8px; font-weight: 600; }
	td { border-bottom: 1px solid var(--rule); padding: 7px 8px; vertical-align: top; }
	tr:target { background: var(--paper-2); }
	.compact { font-size: 12px; margin: 10px 0; }
	.nowrap { white-space: nowrap; }
	.num { font-variant-numeric: tabular-nums; font-weight: 600; }
	.mono { font-family: ui-monospace, monospace; font-size: 11.5px; color: var(--mute); }
	.basis, .note { display: block; color: var(--mute); font-size: 11.5px; margin-top: 2px; }
	.note { color: var(--ink-2); }
	.basis-cell { color: var(--ink-2); }
	.st-verified { color: var(--ok); }
	.st-disagree { color: var(--warn); }
	.st-reported { color: #b02a37; }
	.filters { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
	.filters button { font: inherit; font-size: 12.5px; border: 1px solid var(--rule); background: none; padding: 4px 10px; cursor: pointer; }
	.filters button[aria-pressed='true'] { border-color: var(--ink); background: var(--ink); color: #fff; }
	details { margin: 12px 0; border-top: 1px solid var(--rule); padding-top: 8px; }
	summary { cursor: pointer; font-weight: 600; font-size: 15px; }
	.gaps { display: grid; gap: 10px; padding-left: 18px; }
</style>
