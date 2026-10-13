<script lang="ts">
	// Animated horizontal bars. Values are in $M unless `format` is given.
	import { money } from '#lib/format.ts';

	export interface BarRow { label: string; value: number; color?: string; highlight?: boolean; note?: string; hatch?: boolean }
	let {
		rows,
		format = (v: number) => money(v, 'short'),
		max
	}: { rows: BarRow[]; format?: (v: number) => string; max?: number } = $props();

	const top = $derived(max ?? Math.max(...rows.map((r) => r.value), 1));
	let shown = $state(false);
	$effect(() => {
		rows; // re-animate when the data changes
		shown = false;
		const id = requestAnimationFrame(() => requestAnimationFrame(() => (shown = true)));
		return () => cancelAnimationFrame(id);
	});
</script>

<div class="bars sans" role="list">
	{#each rows as r (r.label)}
		<div class="row" class:hl={r.highlight} role="listitem" title={r.note ?? `${r.label}: ${format(r.value)}`}>
			<span class="label">{r.label}</span>
			<span class="track">
				<span
					class="fill"
					class:hatch={r.hatch}
					style="width:{shown ? Math.max(0.5, (r.value / top) * 100) : 0}%;--c:{r.color ?? 'var(--c-other)'}"
				></span>
			</span>
			<span class="val">{format(r.value)}</span>
		</div>
	{/each}
</div>

<style>
	.bars { display: grid; gap: 7px; font-size: 13px; }
	.row { display: grid; grid-template-columns: minmax(90px, 34%) 1fr auto; align-items: center; gap: 10px; }
	.label { color: var(--ink-2); line-height: 1.2; }
	.row.hl .label { color: var(--ink); font-weight: 600; }
	.track { height: 16px; background: #f0ede6; }
	.fill { display: block; height: 100%; background: var(--c); transition: width 0.9s cubic-bezier(0.3, 0.7, 0.2, 1); }
	.fill.hatch { background: repeating-linear-gradient(45deg, var(--c) 0 5px, transparent 5px 9px); }
	.val { font-variant-numeric: tabular-nums; font-weight: 600; min-width: 58px; text-align: right; }
</style>
