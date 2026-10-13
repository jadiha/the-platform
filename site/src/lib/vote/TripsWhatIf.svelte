<script lang="ts">
	// Trips you'd pay for in one week, under each fare rule as stated. No dollar amounts:
	// it's the rule itself, applied to the number of trips you pick.
	import type { CampaignPromise } from '#lib/types.ts';
	import type { Snippet } from 'svelte';
	import { displayName } from './links.ts';
	let { promises, children }: { promises: CampaignPromise[]; children?: Snippet } = $props();
	let trips = $state(14);
	const rows = $derived(
		promises.flatMap((p) => {
			const name = displayName(p.candidate);
			if (p.rule.type === 'weekly-cap' && p.rule.trips) return [{ name, paid: Math.min(trips, p.rule.trips), note: `free after ${p.rule.trips} paid trips a week` }];
			if (p.rule.type === 'fare-free') return [{ name, paid: 0, note: 'free TTC' }];
			if (p.rule.type === 'fare-free-phased') return [{ name, paid: 0, note: 'if you are in the first phase: low-income, youth, seniors' }];
			return [];
		})
	);
</script>

{#if rows.length}
	<div class="whatif">
		<div class="wh sans">WHAT IF THEY DO IT?</div>
		<h3>If you take <b>{trips}</b> TTC trips this week, how many would you pay for?</h3>
		<label class="sans">Trips this week <input type="range" min="0" max="25" bind:value={trips} /></label>
		<div class="bars sans">
			{#each rows as r (r.name + r.note)}
				<div class="bar">
					<span>{r.name}<small>{r.note}</small></span>
					<div class="track"><div class="fill" style="width:{trips ? (r.paid / 25) * 100 : 0}%"></div></div>
					<b>{r.paid}</b>
				</div>
			{/each}
		</div>
		{@render children?.()}
		<p class="fine sans">Each rule applied exactly as the campaign worded it. It doesn't predict whether a promise is kept or how it would be paid for. Exact words and links are below.</p>
	</div>
{/if}
