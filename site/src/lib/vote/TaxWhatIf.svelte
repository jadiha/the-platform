<script lang="ts">
	// Arithmetic only: this year's average bill, with each stated rule applied to 2027.
	import type { CampaignPromise } from '#lib/types.ts';
	import { displayName } from './links.ts';
	let { bill, promises }: { bill: number; promises: CampaignPromise[] } = $props();
	let inflation = $state(2);
	function next(p: CampaignPromise): number | null {
		if (p.rule.type === 'freeze') return bill;
		if (p.rule.type === 'percent' && typeof p.rule.value === 'number') return bill * (1 + p.rule.value / 100);
		return null;
	}
	const rows = $derived([
		{ label: '2026 bill (actual)', v: bill, ref: true },
		...promises.map((p) => ({ label: displayName(p.candidate), v: next(p), ref: false })).filter((r) => r.v != null),
		{ label: `For comparison: rising with inflation (${inflation.toFixed(1)}%)`, v: bill * (1 + inflation / 100), ref: true }
	] as { label: string; v: number; ref: boolean }[]);
	const max = $derived(Math.max(...rows.map((r) => r.v)) * 1.04);
	const fmt = (v: number) => `$${Math.round(v).toLocaleString('en-CA')}`;
</script>

{#if rows.some((r) => !r.ref)}
<div class="whatif">
	<div class="wh sans">WHAT IF THEY DO IT?</div>
	<h3>The average home's city tax bill in 2027, under each mayoral tax promise</h3>
	<label class="sans">Inflation, for the comparison bar <input type="range" min="0" max="5" step="0.1" bind:value={inflation} /> <b>{inflation.toFixed(1)}%</b></label>
	<div class="bars sans">
		{#each rows as r (r.label)}
			<div class="bar" class:ref={r.ref}>
				<span>{r.label}</span>
				<div class="track"><div class="fill" style="width:{(r.v / max) * 100}%"></div></div>
				<b>{fmt(r.v)}</b>
			</div>
		{/each}
	</div>
	<p class="fine sans">Arithmetic on each promise exactly as the campaign worded it, applied to this year's average bill. It doesn't predict whether a promise is kept, or what would change in city services. The exact words and links are below.</p>
</div>
{/if}
