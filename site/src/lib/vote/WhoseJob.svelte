<script lang="ts">
	// "Whose job is it?": tap the building that decides it (City Hall, Queen's Park or Parliament
	// Hill). The right postcard lights up, and the answer with its proof appears beside them.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	import type { WhoseJobCard } from '#lib/types.ts';

	let { cards }: { cards: WhoseJobCard[] } = $props();
	const { facts } = siteData();
	const LEVELS = ['city', 'province', 'federal'] as const;
	type Level = (typeof LEVELS)[number];
	const PLACE: Record<Level, { name: string; level: string }> = {
		city: { name: 'City Hall', level: 'City' },
		province: { name: "Queen's Park", level: 'Province' },
		federal: { name: 'Parliament Hill', level: 'Federal' }
	};

	let idx = $state(0);
	let picks = $state<Level[]>([]);
	let arrived = $state(false);
	const card = $derived(cards[idx]);
	const pick = $derived(picks[idx]);
	const finished = $derived(idx >= cards.length);
	const score = $derived(picks.filter((p, i) => p === cards[i].answer).length);
	const still = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

	function choose(l: Level) {
		if (pick) return;
		picks = [...picks.slice(0, idx), l];
		arrived = false;
		setTimeout(() => (arrived = true), still() ? 0 : 350);
	}
	const next = () => { idx += 1; arrived = false; };
	const restart = () => { picks = []; idx = 0; arrived = false; };
	const proof = (c: WhoseJobCard) => {
		if (c.proof) return c.proof;
		const f = c.fact ? facts[c.fact] : undefined;
		return f ? { title: f.primary.title + (f.primary.locator ? `, ${f.primary.locator}` : ''), url: pdfPageLink(f.primary.url, f.primary.locator) } : null;
	};
</script>

<div class="game sans">
	<div class="progress" aria-label="Question {Math.min(idx + 1, cards.length)} of {cards.length}">
		{#each cards as c, i (c.thing)}<span class={picks[i] ? (picks[i] === c.answer ? 'ok' : 'miss') : i === idx ? 'cur' : ''}></span>{/each}
	</div>

	{#if !finished}
		<p class="ask">
			<span class="num">Question {idx + 1} of {cards.length}</span>
			<span class="who">Who decides…</span>
			<span class="thing">{card.thing}?</span>
			<span class="hint">{pick ? '' : 'Tap the building that decides it.'}</span>
		</p>

		<div class="play">
			<div class="cards">
				{#each LEVELS as l (l)}
					<button
						class="card {l}"
						class:chosen={pick === l}
						class:correct={pick && l === card.answer}
						class:wrong={pick === l && l !== card.answer}
						disabled={!!pick}
						onclick={() => choose(l)}
						aria-label="{PLACE[l].name}: {PLACE[l].level} government"
					>
						<svg viewBox="0 0 300 210" preserveAspectRatio="xMidYMax meet" aria-hidden="true">
							<rect width="300" height="210" class="sky" />
							<ellipse cx="70" cy="34" rx="34" ry="6" fill="#fff" opacity=".8" /><ellipse cx="236" cy="22" rx="26" ry="5" fill="#fff" opacity=".7" />
							{#if l === 'city'}
								<!-- Toronto City Hall: two curved towers around the council chamber, arches over the pool, CN Tower behind -->
								<g fill="#b4c4d4"><path d="M258 174 L264 54 L268 54 L274 174 Z" /><ellipse cx="266" cy="60" rx="10" ry="6" /><rect x="264.5" y="8" width="3" height="48" /><ellipse cx="266" cy="38" rx="4" ry="2.5" /></g>
								<path d="M118 172 V74 Q118 58 104 56 Q74 60 66 80 V172 Z" fill="#e9ecee" stroke="#8c979f" stroke-width="1.5" />
								<g stroke="#b7c0c6" stroke-width="1">{#each [86, 96, 106, 116, 126, 136, 146, 156] as y (y)}<line x1="70" y1={y} x2="114" y2={y} />{/each}</g>
								<path d="M180 172 V52 Q180 36 196 34 Q228 38 238 62 V172 Z" fill="#e9ecee" stroke="#8c979f" stroke-width="1.5" />
								<g stroke="#b7c0c6" stroke-width="1">{#each [66, 76, 86, 96, 106, 116, 126, 136, 146, 156] as y (y)}<line x1="184" y1={y} x2="234" y2={y} />{/each}</g>
								<rect x="58" y="160" width="188" height="14" fill="#cfd5d9" />
								<ellipse cx="149" cy="156" rx="36" ry="9" fill="#f7f8f9" stroke="#8c979f" stroke-width="1.5" />
								<rect x="138" y="156" width="22" height="8" fill="#cfd5d9" />
								<rect y="174" width="300" height="36" fill="#d9d4c7" />
								<rect x="70" y="182" width="160" height="12" rx="3" fill="#8fc1df" />
								<g fill="none" stroke="#9aa3aa" stroke-width="3">{#each [92, 150, 208] as x (x)}<path d="M{x - 22} 194 Q{x} 166 {x + 22} 194" />{/each}</g>
							{:else if l === 'province'}
								<!-- Queen's Park: pink sandstone legislature, central and corner towers -->
								<rect x="40" y="104" width="220" height="70" fill="#d39a83" stroke="#9a5f4b" stroke-width="1.5" />
								<rect x="40" y="98" width="220" height="8" fill="#b97a64" />
								<rect x="128" y="64" width="44" height="110" fill="#d39a83" stroke="#9a5f4b" stroke-width="1.5" />
								<path d="M124 64 L150 34 L176 64 Z" fill="#8f5a49" />
								<rect x="44" y="80" width="30" height="94" fill="#d39a83" stroke="#9a5f4b" stroke-width="1.5" /><path d="M41 80 L59 60 L77 80 Z" fill="#8f5a49" />
								<rect x="226" y="80" width="30" height="94" fill="#d39a83" stroke="#9a5f4b" stroke-width="1.5" /><path d="M223 80 L241 60 L259 80 Z" fill="#8f5a49" />
								<g fill="#7a4536">{#each [84, 100, 194, 210] as x (x)}<path d="M{x} 132 V120 Q{x + 6} 112 {x + 12} 120 V132 Z" /><path d="M{x} 160 V148 Q{x + 6} 140 {x + 12} 148 V160 Z" />{/each}
									{#each [52, 234] as x (x)}<path d="M{x} 118 V106 Q{x + 7} 98 {x + 14} 106 V118 Z" />{/each}
									<path d="M136 174 V146 Q150 128 164 146 V174 Z" /><circle cx="150" cy="92" r="7" /></g>
								<rect y="174" width="300" height="36" fill="#9cc58e" />
								<path d="M128 174 L172 174 L180 210 L120 210 Z" fill="#d8cdb8" />
							{:else}
								<!-- Parliament Hill: Centre Block with the Peace Tower and copper roofs -->
								<rect x="36" y="118" width="228" height="56" fill="#ddd2b4" stroke="#9a8d6a" stroke-width="1.5" />
								<path d="M36 118 L50 104 L250 104 L264 118 Z" fill="#6fa890" />
								<g fill="#6fa890">{#each [46, 236] as x (x)}<rect {x} y="96" width="18" height="22" fill="#ddd2b4" stroke="#9a8d6a" stroke-width="1.5" /><path d="M{x - 2} 96 L{x + 9} 80 L{x + 20} 96 Z" />{/each}</g>
								<rect x="134" y="54" width="32" height="120" fill="#ddd2b4" stroke="#9a8d6a" stroke-width="1.5" />
								<path d="M130 54 L150 18 L170 54 Z" fill="#6fa890" />
								<line x1="150" y1="18" x2="150" y2="4" stroke="#6b6b6b" stroke-width="1.5" /><rect x="150" y="4" width="12" height="7" fill="#d52b1e" /><rect x="154" y="4" width="4" height="7" fill="#fff" />
								<circle cx="150" cy="72" r="8" fill="#fff" stroke="#9a8d6a" stroke-width="1.5" />
								<g fill="#857650">{#each [58, 78, 98, 186, 206, 226] as x (x)}<path d="M{x} 160 V140 L{x + 6} 132 L{x + 12} 140 V160 Z" />{/each}<path d="M141 174 V150 L150 140 L159 150 V174 Z" /></g>
								<rect y="174" width="300" height="36" fill="#9cc58e" />
								<path d="M140 174 L160 174 L172 210 L128 210 Z" fill="#d8cdb8" />
							{/if}
						</svg>
						<span class="cap"><b>{PLACE[l].level}</b><small>{PLACE[l].name}</small></span>
					</button>
				{/each}
			</div>
			<div class="side" aria-live="polite">
				{#if pick && arrived}
					{@const p = proof(card)}
					<div class="answer lv-{card.answer}">
						<div class="arow"><span class="badge {card.answer}">{PLACE[card.answer].level}</span><span class="verdict">{pick === card.answer ? 'You got it!' : `Not quite. It's ${PLACE[card.answer].name}.`}</span></div>
						<p class="explain">{card.explain}</p>
						{#if p}<a class="proof" href={p.url} target="_blank" rel="noopener">Proof: {p.title} ↗</a>{/if}
						<button class="go" onclick={next}>{idx === cards.length - 1 ? 'See your score' : 'Next question →'}</button>
					</div>
				{:else if pick}
					<div class="waiting">Checking {PLACE[pick].name}…</div>
				{:else}
					<div class="waiting">Tap the building that decides it: <b>City Hall</b>, <b>Queen's Park</b> or <b>Parliament Hill</b>.</div>
				{/if}
			</div>
		</div>

	{:else}
		<div class="answer results">
			<p class="scorebig">{score} / {cards.length}</p>
			<p class="explain">Here's who decides what. <b>Everything at City Hall is what the mayor and council you elect on October 26 control.</b></p>
			<div class="cols">
				{#each LEVELS as l (l)}
					<div class="col">
						<span class="badge {l}">{PLACE[l].level} · {PLACE[l].name}</span>
						<ul>{#each cards.filter((c) => c.answer === l) as c (c.thing)}<li>{c.thing}</li>{/each}</ul>
					</div>
				{/each}
			</div>
			<button class="go" onclick={restart}>Ride again</button>
		</div>
	{/if}
</div>

<style>
	.game { margin-top: 16px; }
	.progress { display: flex; gap: 4px; margin-bottom: 12px; }
	.progress span { flex: 1; height: 5px; border-radius: 5px; background: #e6e2d9; transition: background 0.3s; }
	.progress .cur { background: #9a958b; }
	.progress .ok { background: #4a8c5c; }
	.progress .miss { background: #d9822b; }
	.ask { margin: 0 0 10px; display: flex; flex-direction: column; gap: 2px; }
	.who { font-family: var(--sans); font-size: clamp(18px, 2.4vw, 24px); font-weight: 800; color: #da251d; line-height: 1.1; margin-top: 2px; }
	.num { font-size: 12px; font-weight: 600; letter-spacing: 1.2px; color: var(--mute); text-transform: uppercase; }
	.thing { font-family: var(--serif); font-size: clamp(22px, 3.6vw, 30px); font-weight: 700; line-height: 1.15; letter-spacing: -0.5px; }
	.hint { font-size: 13px; color: var(--mute); min-height: 1em; }
	/* Three postcards, one per government. Each fits a third of the play area, so the question,
	   the buildings and the answer all fit on one screen. */
	.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; width: 100%; height: clamp(220px, min(calc(100vh - 450px), 30cqw), 560px); }
	.card { font: inherit; padding: 0; border: 2px solid transparent; border-radius: 16px; background: #fff; overflow: hidden; cursor: pointer; display: flex; flex-direction: column; box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08); transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s, opacity 0.3s; }
	.card svg { display: block; width: 100%; flex: 1; min-height: 0; }
	.card.city { background: #dce8f5; } .card.province { background: #f6e6d6; } .card.federal { background: #dfeee3; }
	.cap { background: #fff; }
	.card.city .sky { fill: #dce8f5; } .card.province .sky { fill: #f6e6d6; } .card.federal .sky { fill: #dfeee3; }
	.cap { display: flex; flex-direction: column; align-items: center; padding: 8px 6px 10px; line-height: 1.2; }
	.cap b { font-size: 18px; } .cap small { font-size: 13px; color: var(--mute); }
	.card.city .cap b { color: #2f5d9b; } .card.province .cap b { color: #b56a1c; } .card.federal .cap b { color: #3d7a4e; }
	.card:not(:disabled):hover, .card:focus-visible { transform: translateY(-4px); box-shadow: 0 14px 30px rgba(0, 0, 0, 0.12); }
	.card.city:not(:disabled):hover { border-color: #2f5d9b; } .card.province:not(:disabled):hover { border-color: #d9822b; } .card.federal:not(:disabled):hover { border-color: #4a8c5c; }
	.card:disabled { cursor: default; }
	.card:disabled:not(.correct):not(.chosen) { opacity: 0.45; }
	.card.correct.city { border-color: #2f5d9b; } .card.correct.province { border-color: #d9822b; } .card.correct.federal { border-color: #4a8c5c; }
	.card.correct .cap { color: #fff; } .card.correct .cap b, .card.correct .cap small { color: #fff; }
	.card.correct.city .cap { background: #2f5d9b; } .card.correct.province .cap { background: #d9822b; } .card.correct.federal .cap { background: #4a8c5c; }
	.card.wrong { opacity: 0.6; } .card.wrong .cap b { text-decoration: line-through; }
	.play { container-type: inline-size; display: grid; grid-template-columns: minmax(0, 2.5fr) minmax(240px, 1fr); gap: 20px; align-items: center; }
	.side { display: flex; }
	.side .answer { margin: 0; width: 100%; }
	.waiting { align-self: center; font-size: 15px; color: var(--ink-2); background: #fff; border: 1px dashed var(--rule); border-radius: 18px; padding: 18px; width: 100%; }
	.arow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
	.arow .verdict { margin: 0; }
	.answer { margin-top: 14px; background: #fff; border-radius: 18px; padding: 18px 20px; border: 1px solid var(--rule); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.07); animation: pop 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); }
	@keyframes pop { from { transform: translateY(12px); opacity: 0; } to { transform: none; opacity: 1; } }
	.answer.lv-city { border-top: 7px solid #2f5d9b; }
	.answer.lv-province { border-top: 7px solid #d9822b; }
	.answer.lv-federal { border-top: 7px solid #4a8c5c; }
	.verdict { display: block; font-size: 15px; font-weight: 700; }
	.badge { display: inline-block; font-size: 15px; font-weight: 800; color: #fff; padding: 4px 12px; border-radius: 999px; }
	.badge.city { background: #2f5d9b; }
	.badge.province { background: #d9822b; }
	.badge.federal { background: #4a8c5c; }
	.explain { font-size: 16px; line-height: 1.5; color: var(--ink-2); margin: 8px 0; }
	.proof { display: block; font-size: 12px; color: var(--mute); margin-bottom: 14px; }
	.go { font: inherit; font-weight: 700; font-size: 15px; background: #da251d; color: #fff; border: 0; border-radius: 999px; padding: 10px 20px; cursor: pointer; }
	.scorebig { font-family: var(--serif); font-size: 64px; font-weight: 700; margin: 0; line-height: 1; }
	.cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 14px 0 18px; }
	.col ul { padding-left: 16px; margin: 8px 0 0; font-size: 13px; line-height: 1.4; }
	.col .badge { font-size: 12px; }
	.hint { display: none; }
	@media (max-width: 860px) { .play { grid-template-columns: 1fr; } .waiting { display: none; } .hint { display: block; } }
	@media (max-width: 600px) {
		.cards { gap: 6px; height: auto; } .card svg { flex: none; height: auto; }
		.card { border-radius: 12px; }
		.cap { padding: 5px 2px 7px; } .cap b { font-size: 13px; } .cap small { font-size: 9.5px; }
		.cols { grid-template-columns: 1fr; }
	}
	@media (prefers-reduced-motion: reduce) { .card, .answer { transition: none; animation: none; } }
</style>
