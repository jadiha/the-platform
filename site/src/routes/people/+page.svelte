<script lang="ts">
	import PersonCard from '#lib/components/PersonCard.svelte';
	import { siteData } from '#lib/context.ts';
	import { formatDate } from '#lib/format.ts';

	const { people } = siteData();
	const LEVELS = [
		['city', 'City of Toronto', 'Sets the city budget: TTC, police, shelters, parks, roads, property tax.'],
		['school', 'Toronto District School Board', 'Spends the money the Province gives for schools.'],
		['province', 'Province of Ontario', 'Funds schools, hospitals and social assistance, and builds the subway extension.'],
		['federal', 'Government of Canada', 'Sends money to the Province and the City through transfers and project funding.']
	] as const;
	const asOf = $derived(people.map((p) => p.as_of).sort().at(-1));
</script>

<svelte:head>
	<title>Who's responsible · Follow the Budget</title>
	<meta name="description" content="The people who decide how Scarborough's public money is spent, with their recorded votes and public statements." />
</svelte:head>

<div class="wrap page">
	<p class="kicker">Who's responsible</p>
	<h1>The people who decide</h1>
	<p class="dek">
		Every person here gets the same treatment: their role, what they decided or voted for, and what they said in public, each linked to the official record.
		We don't rate anyone or tell you how to vote.
	</p>
	{#if asOf}<p class="sans asof">Information as of {formatDate(asOf)}.</p>{/if}
</div>

<div class="wide">
	{#each LEVELS as [level, title, what] (level)}
		{@const list = people.filter((p) => p.level === level)}
		{#if list.length}
			<section>
				<h2>{title}</h2>
				<p class="sans what">{what}</p>
				<div class="grid">
					{#each list as person (person.id)}
						<PersonCard {person} />
					{/each}
				</div>
			</section>
		{/if}
	{/each}
	{#if !people.length}
		<p class="sans pending">We're still compiling the public record for each decision-maker. Check back soon.</p>
	{/if}
</div>

<style>
	.page { margin-top: 44px; }
	h1 { font-size: clamp(32px, 5vw, 46px); margin: 8px 0 12px; }
	.dek { color: var(--ink-2); font-size: 20px; }
	.asof { font-size: 13px; color: var(--mute); }
	section { margin-top: 40px; }
	h2 { font-size: 28px; margin: 0; border-top: 3px double var(--ink); padding-top: 10px; }
	.what { font-size: 14px; color: var(--ink-2); margin: 4px 0 8px; }
	.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px 28px; }
	.grid :global(.card) { scroll-margin-top: 80px; }
	.grid :global(.card:target) { background: var(--paper-2); }
	.pending { color: var(--mute); margin-top: 30px; }
</style>
