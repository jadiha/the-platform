<script lang="ts">
	import { onMount } from 'svelte';
	import scrollama from 'scrollama';
	import Fact from '#lib/components/Fact.svelte';
	import Term from '#lib/components/Term.svelte';
	import Bars, { type BarRow } from '#lib/components/Bars.svelte';
	import People from '#lib/components/People.svelte';
	import Trends from '#lib/components/Trends.svelte';
	import RepLookup from '#lib/components/RepLookup.svelte';
	import StoryMap from '#lib/story/StoryMap.svelte';
	import { siteData } from '#lib/context.ts';
	import { categoryColor } from '#lib/categories.ts';
	import { money } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const { facts, people } = siteData();

	let step = $state(0);
	let stepsEl: HTMLElement;

	onMount(() => {
		const s = scrollama();
		s.setup({ step: stepsEl.querySelectorAll('.step') as unknown as string, offset: 0.6 }).onStepEnter(
			({ index }) => (step = index)
		);
		const onResize = () => s.resize();
		window.addEventListener('resize', onResize);
		return () => {
			window.removeEventListener('resize', onResize);
			s.destroy();
		};
	});

	const v = (id: string) => (typeof facts[id]?.value === 'number' ? (facts[id].value as number) : NaN);
	const has = (...ids: string[]) => ids.every((id) => Number.isFinite(v(id)));
	const pct = (x: number) => `${x.toFixed(0)}%`;

	// ---- Charts for each stop, built only from pipeline data and the fact registry ----
	const charts = $derived.by(() => {
		const out: { title: string; sub: string; rows: BarRow[]; format?: (n: number) => string; foot?: string }[] = [];

		// 0 Home: where the city's money comes from
		const gross = v('toronto.operating.2026.gross');
		const tax = v('toronto.revenue.2026.property-tax');
		const gov = v('toronto.revenue.2026.fed-prov');
		out[0] = {
			title: 'Where Toronto’s money comes from',
			sub: '2026 operating budget, $ (gross)',
			rows: has('toronto.operating.2026.gross', 'toronto.revenue.2026.property-tax', 'toronto.revenue.2026.fed-prov')
				? [
						{ label: 'Property tax', value: tax, color: 'var(--c-housing)', highlight: true },
						{ label: 'Province + federal government', value: gov, color: 'var(--c-transit)' },
						{ label: 'Everything else: fares, fees, water & other rates, reserves', value: gross - tax - gov }
					]
				: []
		};

		// 1 Kennedy: TTC total cost vs what the city pays
		const ttcG = v('toronto.ttc.2026.gross');
		const ttcN = v('toronto.ttc.2026.net');
		out[1] = {
			title: 'Who pays for the TTC',
			sub: '2026 operating budget, conventional + Wheel-Trans',
			rows: has('toronto.ttc.2026.gross', 'toronto.ttc.2026.net')
				? [
						{ label: 'Total cost (gross)', value: ttcG, color: 'var(--c-transit)', highlight: true },
						{ label: 'Paid by the city (net)', value: ttcN, color: 'var(--c-transit)' },
						{ label: 'Covered by fares & other sources', value: ttcG - ttcN, color: 'var(--c-other)' }
					]
				: []
		};

		// 2 School: TDSB provincial funding, three years
		const yrs: [string, string][] = [
			['2024-25 (actual)', 'schools.tdsb.core-ed.2024-25'],
			['2025-26 (revised)', 'schools.tdsb.core-ed.2025-26'],
			['2026-27 (projected)', 'schools.tdsb.core-ed.2026-27']
		];
		out[2] = {
			title: 'Provincial funding for TDSB',
			sub: 'Core Education Funding, $ per year',
			rows: yrs.filter(([, id]) => has(id)).map(([label, id], i) => ({
				label, value: v(id), color: 'var(--c-education)', highlight: i === 2
			})),
			format: (n) => money(n, 'short'),
			foot: 'Paid 100% by the Province. The city contributes nothing to school operating budgets.'
		};

		// 3 Rec centre: ward-tagged capital per resident
		const wards = data.wards?.wards ?? [];
		out[3] = {
			title: 'City building money tagged to each ward, per resident',
			sub: `10-year capital plan ${data.wards?.capitalPlan ?? ''}. Scarborough wards in green.`,
			rows: [...wards]
				.sort((a, b) => b.perResident10yr - a.perResident10yr)
				.map((w) => ({
					label: `${w.ward} ${w.name}`,
					value: w.perResident10yr,
					color: w.scarborough ? 'var(--c-housing)' : 'var(--c-other)',
					highlight: w.scarborough
				})),
			format: (n) => `$${Math.round(n).toLocaleString('en-CA')}`,
			foot: data.wards
				? `Only ${pct((1 - data.wards.cityWide.share) * 100)} of the plan is tagged to a ward. The other ${pct(data.wards.cityWide.share * 100)} (TTC, police, citywide systems) can’t be split by neighbourhood, so this is not the whole picture.`
				: undefined
		};

		// 4 City Hall: Toronto by category
		out[4] = {
			title: 'Where Toronto’s money goes',
			sub: `2026 operating budget, gross${data.toronto?.basis ? ` · ${data.toronto.basis}` : ''}`,
			rows: (data.toronto?.children ?? [])
				.toSorted((a, b) => b.gross - a.gross)
				.map((c) => ({ label: c.name, value: c.gross, color: categoryColor(c.category) }))
		};

		// 5 Queen's Park: Ontario by sector
		out[5] = {
			title: 'Where Ontario’s money goes',
			sub: '2026-27 plan, by category (see Sources for how ministries were grouped)',
			rows: (data.ontario?.children ?? [])
				.toSorted((a, b) => b.gross - a.gross)
				.map((c) => ({ label: c.name, value: c.gross, color: categoryColor(c.category), highlight: c.category === 'education' }))
		};
		return out;
	});

	const chart = $derived(charts[step]);
	const SCARB_COUNCIL = people.filter((p) => p.level === 'city' && /Scarborough/.test(p.ward_or_riding ?? '')).map((p) => p.id);
	const SCARB_MPPS = people.filter((p) => p.level === 'province' && /Scarborough/.test(p.ward_or_riding ?? '')).map((p) => p.id);
</script>

<svelte:head>
	<title>The Platform · where Scarborough’s money goes</title>
	<meta name="description" content="A walk through Scarborough showing how the City of Toronto and the Province of Ontario spend public money, and who decides. Every number is sourced." />
</svelte:head>

<header class="hero wrap">
	<p class="kicker" style="color:var(--c-education)">A walk through your money · 2026</p>
	<h1>Where Scarborough’s money goes, one stop at a time</h1>
	<p class="dek">
		Three governments spend money on your street, your bus and your school. Take a walk through the neighbourhood to see who pays for what, and who decides.
	</p>
	<p class="how sans">
		<span class="u-ok">Underlined numbers</span> are checked against official sources. Tap one to see where it came from.
		<span class="u-term">Dotted words</span> explain the jargon.
	</p>
</header>

<div class="scrolly wide">
	<div class="graphic" aria-hidden={step >= 6}>
		<div class="map"><StoryMap {step} wards={data.wards} /></div>
		{#if chart && chart.rows.length}
			<div class="chart">
				<p class="ctitle sans">{chart.title}</p>
				<p class="csub sans">{chart.sub}</p>
				<Bars rows={chart.rows} format={chart.format} />
				{#if chart.foot}<p class="cfoot sans">{chart.foot}</p>{/if}
			</div>
		{/if}
		<p class="mapnote sans">* Home, school and rec centre are representative spots, not exact addresses.</p>
	</div>

	<div class="steps" bind:this={stepsEl}>
		<!-- 1 · HOME -->
		<section class="step" class:active={step === 0}>
			<p class="kicker" style="color:var(--c-housing)">Stop 1 · Home</p>
			<h2>It starts at your front door</h2>
			<p>
				Every home in Scarborough pays <Term id="property-tax" /> to the City of Toronto. In 2026 the average home’s bill is
				<Fact id="toronto.property-tax.2026.avg-bill" />, up <Fact id="toronto.property-tax.2026.increase" /> from last year.
			</p>
			<p>
				But property tax is only part of how the city pays its bills. Its <Term id="operating-budget" /> this year is
				<Fact id="toronto.operating.2026.gross" />. The rest comes from fares, fees, and money
				<Term id="transfers">transferred</Term> from the Province and Ottawa.
			</p>
			<p class="decides sans"><strong>Who decides:</strong> City Council, every winter. The 2026 budget passed on Feb 10, 2026.</p>
		</section>

		<!-- 2 · KENNEDY -->
		<section class="step" class:active={step === 1}>
			<p class="kicker" style="color:var(--c-transit)">Stop 2 · Kennedy Station</p>
			<h2>Your bus is the city’s biggest single cost</h2>
			<p>
				Running the TTC costs <Fact id="toronto.ttc.2026.gross" /> this year. Fares cover a big part, and the city pays
				<Fact id="toronto.ttc.2026.net" /> itself. That gap between <Term id="gross">total cost</Term> and
				<Term id="net">what the city pays</Term> shows up everywhere in budgets.
			</p>
			<p>
				Right here, three different projects are changing how Scarborough gets around:
			</p>
			<ul class="projects sans">
				<li><strong>Scarborough Busway:</strong> opened <Fact id="scarborough.busway.opened" />, on the old SRT line.</li>
				<li>
					<strong>Scarborough Subway Extension:</strong> run by the Province (Metrolinx). Ottawa is putting in about
					<Fact id="federal.sse.contribution" />. Opening has been <Fact id="scarborough.sse.opening-reported" />.
				</li>
				<li>
					<strong>Eglinton East LRT:</strong> estimated at <Fact id="scarborough.eelrt.cost-estimate" /> and still unfunded. In April 2026 the city asked
					the Province and Ottawa to each pay a third. The Province called it “a municipally-led project.”
				</li>
			</ul>
			<p class="decides sans"><strong>Who decides:</strong> City Council and the TTC board run buses. The Province decides on the subway. Big transit needs all three governments.</p>
		</section>

		<!-- 3 · SCHOOL -->
		<section class="step" class:active={step === 2}>
			<p class="kicker" style="color:var(--c-education)">Stop 3 · Your school</p>
			<h2>Surprise: the city pays nothing here</h2>
			<p>
				Schools are funded by the <strong>Province of Ontario</strong>, not the city. The Toronto District School Board gets
				<Fact id="schools.tdsb.core-ed.2026-27" /> this year, a <Fact id="schools.tdsb.core-ed.change" /> change from last year, while
				enrolment is also falling.
			</p>
			<p>
				And TDSB isn’t run by the trustees you elect right now. Since <Fact id="schools.tdsb.supervision-start" />, it has been run by a
				<Term id="supervisor">provincial supervisor</Term>.
			</p>
			<div class="callout sans">
				<strong>What the watchdog says:</strong> Ontario’s independent <Term id="fao">FAO</Term> projects that education funding will fall short of
				rising costs by <Fact id="schools.fao.shortfall-2028-29" /> by 2028-29.
			</div>
			<People ids={['tdsb-supervisor', 'ontario-education-minister']} />
		</section>

		<!-- 4 · REC CENTRE -->
		<section class="step" class:active={step === 3}>
			<p class="kicker" style="color:var(--c-housing)">Stop 4 · Rec centre</p>
			<h2>Does Scarborough get its fair share?</h2>
			<p>
				The city’s <Term id="capital-budget" /> plans <Fact id="toronto.capital.2026-2035.total" /> of building and repairs over ten years.
				Of that, <Fact id="scarborough.capital.2026-2035.ward-tagged" /> is tagged to Scarborough’s six <Term id="ward">wards</Term>, home to
				<Fact id="scarborough.population.2021" /> people.
			</p>
			<p>
				The honest answer is <em>we can’t fully tell</em>. Most of the money is <Term id="city-wide" /> and isn’t tagged to any neighbourhood.
				One project, a new long-term care home on Finch Ave E, makes up <Fact id="scarborough.capital.finch-ltc" /> of Scarborough’s total.
			</p>
		</section>

		<!-- 5 · CITY HALL -->
		<section class="step" class:active={step === 4}>
			<p class="kicker">Stop 5 · City Hall</p>
			<h2>Who decides Toronto’s budget</h2>
			<p>
				The mayor proposes the budget under <Term id="strong-mayor" />, and the 25 <Term id="councillor">councillors</Term> can change it.
				Police get <Fact id="toronto.police.2026.gross" /> this year. Shelter and support services get
				<Fact id="toronto.shelter.2026.gross" />.
			</p>
			<People ids={['chow-olivia', 'budget-chief', ...SCARB_COUNCIL]} title="Who decides: Mayor, budget chief, Scarborough councillors" />
		</section>

		<!-- 6 · QUEEN'S PARK -->
		<section class="step" class:active={step === 5}>
			<p class="kicker" style="color:var(--c-education)">Stop 6 · Queen’s Park</p>
			<h2>Zoom out: Ontario spends <Fact id="ontario.expense.2026-27.total" short /></h2>
			<p>
				That’s about thirteen times Toronto’s budget. Health and education are the two biggest pieces. Ontario plans a
				<Term id="deficit" /> of <Fact id="ontario.deficit.2026-27" /> this year.
			</p>
			<People ids={['ford-doug', 'ontario-finance-minister', ...SCARB_MPPS]} title="Who decides: Premier, Finance Minister, Scarborough MPPs" />
		</section>

		<!-- 7 · TRENDS -->
		<section class="step full" class:active={step === 6}>
			<p class="kicker">Stop 7 · What changed</p>
			<h2>Five years of spending, side by side</h2>
			<Trends trends={data.trends} />
		</section>

		<!-- 8 · YOU -->
		<section class="step full" class:active={step === 7}>
			<p class="kicker" style="color:var(--c-transit)">Stop 8 · You</p>
			<h2>Who represents you?</h2>
			<p>Enter your postal code to find your councillor, MPP and MP, and what they’ve done on budgets.</p>
			<RepLookup />
			<p class="next sans">
				<a href="/explore/budget/">Explore the full budget yourself →</a>
			</p>
		</section>
	</div>
</div>

<style>
	.hero { margin: 56px auto 40px; }
	h1 { font-size: clamp(36px, 6vw, 56px); margin: 10px 0 16px; }
	.dek { font-size: clamp(17px, 2.2vw, 21px); color: var(--ink-2); margin: 0; }
	.how { font-size: 13px; color: var(--mute); border-top: 1px solid var(--rule); margin-top: 22px; padding-top: 10px; }
	.u-ok { border-bottom: 2px solid var(--ok); color: var(--ink); }
	.u-term { border-bottom: 1.5px dotted var(--ink); color: var(--ink); }

	.scrolly { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 48px; position: relative; }
	.graphic {
		position: sticky; top: 64px; height: calc(100vh - 80px);
		display: flex; flex-direction: column; justify-content: center; gap: 8px;
	}
	.map { flex: 1 1 auto; min-height: 0; }
	.chart { border-top: 1px solid var(--ink); padding-top: 10px; }
	.ctitle { font-weight: 600; font-size: 14px; margin: 0; }
	.csub { color: var(--mute); font-size: 12px; margin: 0 0 10px; }
	.cfoot { font-size: 12px; color: var(--ink-2); background: var(--paper-2); padding: 8px 10px; margin: 10px 0 0; }
	.chart :global(.bars) { max-height: 34vh; overflow-y: auto; }
	.mapnote { font-size: 10.5px; color: var(--mute); margin: 0; }

	.steps { padding: 20vh 0 30vh; }
	.step {
		min-height: 80vh; margin-bottom: 30vh; padding: 4px 0 4px 20px;
		border-left: 3px solid var(--rule); transition: opacity 0.4s, border-color 0.4s; opacity: 0.35;
	}
	.step.active { opacity: 1; border-left-color: var(--ink); }
	.step.full { min-height: auto; }
	.step h2 { font-size: 32px; margin: 6px 0 14px; }
	.decides { font-size: 13.5px; color: var(--ink-2); border-top: 1px solid var(--rule); padding-top: 10px; }
	.projects { font-size: 15px; padding-left: 18px; display: grid; gap: 8px; }
	.callout { background: #fdf1e4; border-left: 3px solid var(--c-education); padding: 10px 14px; font-size: 14.5px; margin: 16px 0; }
	.next { margin-top: 30px; font-weight: 600; }

	/* Stops 7–8 take the whole width; hide the map so they have room. */
	.graphic[aria-hidden='true'] { visibility: hidden; }

	@media (max-width: 900px) {
		.scrolly { grid-template-columns: 1fr; gap: 0; }
		.graphic { top: 0; height: 58vh; z-index: 5; background: var(--paper); padding: 6px 0; border-bottom: 1px solid var(--rule); }
		.chart :global(.bars) { max-height: 18vh; }
		.steps { padding-top: 10vh; }
		.step { background: color-mix(in srgb, var(--paper) 96%, transparent); min-height: 60vh; }
		.graphic[aria-hidden='true'] { display: none; }
	}
</style>
