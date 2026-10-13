<script lang="ts">
	// "Whose job is it?" as a deck: one big card at a time. Tap City, Province or Federal, the card
	// flips to the answer and its proof, then the next card slides in. A results card ends the deck.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	import type { WhoseJobCard } from '#lib/types.ts';

	let { cards }: { cards: WhoseJobCard[] } = $props();
	const { facts } = siteData();
	const LEVELS = ['city', 'province', 'federal'] as const;
	type Level = (typeof LEVELS)[number];
	const LABEL: Record<Level, string> = { city: 'City', province: 'Province', federal: 'Federal' };
	const WHO: Record<Level, string> = { city: 'Mayor and council', province: 'Queen’s Park (Ontario)', federal: 'Ottawa (Canada)' };

	let idx = $state(0);
	let picks = $state<Level[]>([]);
	const card = $derived(cards[idx]);
	const pick = $derived(picks[idx]);
	const finished = $derived(idx >= cards.length);
	const score = $derived(picks.filter((p, i) => p === cards[i].answer).length);

	function choose(l: Level) { if (!pick) picks = [...picks.slice(0, idx), l]; }
	const next = () => (idx += 1);
	const restart = () => { picks = []; idx = 0; };
	const proof = (c: WhoseJobCard) => {
		if (c.proof) return c.proof;
		const f = c.fact ? facts[c.fact] : undefined;
		return f ? { title: f.primary.title + (f.primary.locator ? `, ${f.primary.locator}` : ''), url: pdfPageLink(f.primary.url, f.primary.locator) } : null;
	};
</script>

<div class="deck sans">
	<div class="progress" aria-label="Question {Math.min(idx + 1, cards.length)} of {cards.length}">
		{#each cards as c, i (c.thing)}
			<span class={picks[i] ? (picks[i] === c.answer ? 'ok' : 'miss') : i === idx ? 'cur' : ''}></span>
		{/each}
	</div>

	{#if !finished}
		{#key idx}
			<div class="card lv-{pick ? card.answer : 'none'}" class:flipped={!!pick}>
				<div class="face front">
					<span class="num">{idx + 1} / {cards.length}</span>
					<p class="q">Who decides…</p>
					<p class="thing">{card.thing}?</p>
					<div class="choices" role="group" aria-label="Choose who decides">
						{#each LEVELS as l (l)}
							<button class="choice {l}" onclick={() => choose(l)}>
								<span class="big">{LABEL[l]}</span><span class="small">{WHO[l]}</span>
							</button>
						{/each}
					</div>
				</div>
				{#if pick}
					{@const p = proof(card)}
					<div class="face back" aria-live="polite">
						<span class="verdict">{pick === card.answer ? 'You got it' : `Not quite. You said ${LABEL[pick]}.`}</span>
						<span class="badge {card.answer}">{LABEL[card.answer]}</span>
						<p class="thing small">{card.thing}</p>
						<p class="explain">{card.explain}</p>
						{#if p}<a class="proof" href={p.url} target="_blank" rel="noopener">Proof: {p.title} ↗</a>{/if}
						<button class="go" onclick={next}>{idx === cards.length - 1 ? 'See your score' : 'Next question →'}</button>
					</div>
				{/if}
			</div>
		{/key}
	{:else}
		<div class="card results">
			<p class="scorebig">{score} / {cards.length}</p>
			<p class="explain">Here's who decides what. <b>Everything under City is what the mayor and council you elect on October 26 control.</b></p>
			<div class="cols">
				{#each LEVELS as l (l)}
					<div class="col">
						<span class="badge {l}">{LABEL[l]}</span>
						<ul>{#each cards.filter((c) => c.answer === l) as c (c.thing)}<li>{c.thing}</li>{/each}</ul>
					</div>
				{/each}
			</div>
			<button class="again" onclick={restart}>Play again</button>
		</div>
	{/if}
</div>

<style>
	.deck { max-width: 560px; margin: 18px auto 0; }
	.progress { display: flex; gap: 4px; margin-bottom: 12px; }
	.progress span { flex: 1; height: 5px; border-radius: 5px; background: #e6e2d9; transition: background 0.3s; }
	.progress .cur { background: #9a958b; }
	.progress .ok { background: #4a8c5c; }
	.progress .miss { background: #d9822b; }
	.card { position: relative; background: #fff; border-radius: 22px; padding: 22px; min-height: 330px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.08); border: 1px solid var(--rule); animation: slide 0.45s cubic-bezier(0.2, 0.8, 0.2, 1); }
	@keyframes slide { from { transform: translateX(40px) rotate(2deg); opacity: 0; } to { transform: none; opacity: 1; } }
	.card.flipped .front { display: none; }
	.back { animation: flip 0.45s ease; }
	@keyframes flip { from { transform: rotateY(90deg); opacity: 0; } to { transform: none; opacity: 1; } }
	.card.lv-city { border-top: 8px solid #2f5d9b; }
	.card.lv-province { border-top: 8px solid #d9822b; }
	.card.lv-federal { border-top: 8px solid #4a8c5c; }
	.num { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: var(--mute); }
	.q { margin: 18px 0 2px; font-size: 15px; color: var(--mute); }
	.thing { font-family: var(--serif); font-size: clamp(24px, 5vw, 32px); line-height: 1.15; font-weight: 700; margin: 0 0 22px; letter-spacing: -0.5px; }
	.thing.small { font-size: 20px; margin: 10px 0 6px; }
	.choices { display: grid; gap: 8px; }
	.choice { font: inherit; display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-radius: 14px; border: 2px solid var(--ink); background: #fff; cursor: pointer; transition: transform 0.15s, background 0.2s, color 0.2s; text-align: left; }
	.choice:hover, .choice:focus-visible { transform: translateY(-2px); }
	.choice.city:hover { background: #2f5d9b; border-color: #2f5d9b; color: #fff; }
	.choice.province:hover { background: #d9822b; border-color: #d9822b; color: #fff; }
	.choice.federal:hover { background: #4a8c5c; border-color: #4a8c5c; color: #fff; }
	.choice .big { font-size: 18px; font-weight: 700; }
	.choice .small { font-size: 12px; opacity: 0.75; }
	.verdict { display: block; font-size: 14px; font-weight: 600; color: var(--mute); margin-bottom: 10px; }
	.badge { display: inline-block; font-size: 22px; font-weight: 800; color: #fff; padding: 6px 16px; border-radius: 999px; }
	.badge.city { background: #2f5d9b; }
	.badge.province { background: #d9822b; }
	.badge.federal { background: #4a8c5c; }
	.explain { font-size: 16px; line-height: 1.5; color: var(--ink-2); margin: 6px 0 10px; }
	.proof { display: block; font-size: 12px; color: var(--mute); margin-bottom: 18px; }
	.go, .again { font: inherit; font-weight: 700; font-size: 15px; background: var(--ink); color: #fff; border: 0; border-radius: 999px; padding: 12px 22px; cursor: pointer; }
	.results { text-align: left; }
	.scorebig { font-family: var(--serif); font-size: 64px; font-weight: 700; margin: 0; line-height: 1; }
	.cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0 18px; }
	.col ul { padding-left: 16px; margin: 8px 0 0; font-size: 13px; line-height: 1.4; }
	.col .badge { font-size: 13px; padding: 4px 10px; }
	@media (max-width: 560px) { .cols { grid-template-columns: 1fr; } .card { padding: 18px; } }
	@media (prefers-reduced-motion: reduce) { .card, .back { animation: none; } .choice { transition: none; } }
</style>
