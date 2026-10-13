<script lang="ts">
	// "Whose job is it?" Tap City, Province or Federal; the answer and its proof appear right away.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	import type { WhoseJobCard } from '#lib/types.ts';

	let { cards }: { cards: WhoseJobCard[] } = $props();
	const { facts } = siteData();
	const LABEL = { city: 'City', province: 'Province', federal: 'Federal' } as const;
	let picks = $state<Record<number, keyof typeof LABEL>>({});
	const done = $derived(Object.keys(picks).length);
	const right = $derived(Object.entries(picks).filter(([i, a]) => cards[+i].answer === a).length);
	const proof = (c: WhoseJobCard) => {
		if (c.proof) return c.proof;
		const f = c.fact ? facts[c.fact] : undefined;
		return f ? { title: f.primary.title + (f.primary.locator ? `, ${f.primary.locator}` : ''), url: pdfPageLink(f.primary.url, f.primary.locator) } : null;
	};
</script>

<div class="game sans">
	<div class="score" aria-live="polite">{done ? `${right} of ${done} right` : `${cards.length} quick questions`}</div>
	<ol>
		{#each cards as c, i (c.thing)}
			{@const pick = picks[i]}
			<li class:answered={pick} class:right={pick && pick === c.answer}>
				<p class="thing">{c.thing}</p>
				<div class="choices" role="group" aria-label="Who decides: {c.thing}">
					{#each Object.entries(LABEL) as [k, label] (k)}
						<button
							class="choice {k}"
							class:is-answer={pick && k === c.answer}
							class:is-wrong={pick === k && k !== c.answer}
							disabled={!!pick}
							onclick={() => (picks = { ...picks, [i]: k as keyof typeof LABEL })}>{label}</button
						>
					{/each}
				</div>
				{#if pick}
					{@const p = proof(c)}
					<p class="answer">
						<b>{pick === c.answer ? 'Yes!' : `It's the ${LABEL[c.answer]}.`}</b>
						{c.explain}
						{#if p}<a href={p.url} target="_blank" rel="noopener">Proof: {p.title} ↗</a>{/if}
					</p>
				{/if}
			</li>
		{/each}
	</ol>
	{#if done === cards.length}
		<p class="wrap-up">The mayor and council control the City items, which is a lot of what you use every day. Now meet who wants the job.</p>
	{/if}
</div>

<style>
	.game { margin-top: 14px; }
	.score { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--mute); margin-bottom: 8px; }
	ol { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
	li { background: #fff; border: 1px solid var(--rule); border-radius: 14px; padding: 14px; transition: border-color 0.3s, transform 0.3s; }
	li.answered { border-color: #bdb8ad; }
	li.right { border-color: #4a8c5c; }
	.thing { font-family: var(--serif); font-size: 18px; line-height: 1.3; margin: 0 0 10px; font-weight: 600; }
	.choices { display: flex; gap: 6px; }
	.choice { flex: 1; font: inherit; font-size: 13px; font-weight: 600; padding: 9px 4px; border-radius: 999px; border: 1.5px solid var(--ink); background: #fff; cursor: pointer; transition: all 0.25s; }
	.choice:disabled { cursor: default; opacity: 0.45; }
	.choice.is-answer { opacity: 1; color: #fff; }
	.choice.city.is-answer { background: #2f5d9b; border-color: #2f5d9b; }
	.choice.province.is-answer { background: #d9822b; border-color: #d9822b; }
	.choice.federal.is-answer { background: #4a8c5c; border-color: #4a8c5c; }
	.choice.is-wrong { opacity: 1; text-decoration: line-through; }
	.answer { font-size: 13px; line-height: 1.45; margin: 10px 0 0; color: var(--ink-2); }
	.answer a { display: block; margin-top: 4px; font-size: 11.5px; color: var(--mute); }
	.wrap-up { font-size: 15px; margin-top: 14px; font-weight: 600; }
	@media (prefers-reduced-motion: reduce) { li, .choice { transition: none; } }
</style>
