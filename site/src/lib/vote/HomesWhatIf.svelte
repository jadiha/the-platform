<script lang="ts">
	// Each promised number of homes as dots, 100 homes per dot.
	import type { CampaignPromise } from '#lib/types.ts';
	import { displayName } from './links.ts';
	let { promises }: { promises: CampaignPromise[] } = $props();
	const items = $derived(promises.filter((p) => p.rule.type === 'homes' && p.rule.count));
	let pick = $state(0);
	const cur = $derived(items[pick]);
	const total = $derived(Math.ceil(Math.max(...items.map((p) => p.rule.count!), 1) / 100));
	const lit = $derived(cur ? Math.round(cur.rule.count! / 100) : 0);
</script>

{#if items.length}
	<div class="whatif">
		<div class="wh sans">WHAT IF THEY DO IT?</div>
		<h3>Homes promised, as stated. Each dot is 100 homes.</h3>
		<div class="chips sans">
			{#each items as p, i (p.candidate + p.text)}
				<button aria-pressed={pick === i} onclick={() => (pick = i)}>{displayName(p.candidate)}: {p.rule.count!.toLocaleString('en-CA')}, {p.rule.by}</button>
			{/each}
		</div>
		<div class="dots" aria-label="{lit * 100} homes">
			{#each { length: total } as _, k (k)}<span class:lit={k < lit} style="transition-delay:{Math.min(k, 120) * 6}ms"></span>{/each}
		</div>
		<p class="fine sans">Lit dots show the promise as the campaign stated it. It doesn't predict whether the homes get built. Exact words and links are below.</p>
	</div>
{/if}
