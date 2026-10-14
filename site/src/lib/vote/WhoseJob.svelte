<script lang="ts">
	// Lower-case the first letter mid-sentence, but keep acronyms like TTC.
	const lc = (t: string) => (/^[A-Z][A-Z]/.test(t) ? t : t[0].toLowerCase() + t.slice(1));
	// "Whose job is it?": tap the building that decides it (City Hall, Queen's Park or Parliament
	// Hill). The right postcard lights up, and the answer with its proof appears beside them.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	import type { WhoseJobCard } from '#lib/types.ts';

	// 'done' tells the page the quiz is over, so its Next stop button can go back to red.
	let { cards, done = $bindable(false) }: { cards: WhoseJobCard[]; done?: boolean } = $props();
	const { facts } = siteData();
	const LEVELS = ['city', 'province', 'federal'] as const;
	type Level = (typeof LEVELS)[number];
	// Plain names first; the building is only a picture. 'who' says which government it is.
	const PLACE: Record<Level, { name: string; level: string; who: string }> = {
		city: { name: 'City Hall', level: 'City', who: "Toronto's government" },
		province: { name: "Queen's Park", level: 'Province', who: "Ontario's government" },
		federal: { name: 'Parliament Hill', level: 'Federal', who: "Canada's government" }
	};

	const SKY: Record<Level, string> = { city: '#dce8f5', province: '#f6e6d6', federal: '#dfeee3' };
	let idx = $state(0);
	let picks = $state<Level[]>([]);
	const card = $derived(cards[idx]);
	const pick = $derived(picks[idx]);
	const finished = $derived(idx >= cards.length);
	$effect(() => { done = finished; });
	const score = $derived(picks.filter((p, i) => p === cards[i].answer).length);
	const still = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;

	function choose(l: Level) {
		if (pick) return;
		picks = [...picks.slice(0, idx), l];
	}
	const next = () => { idx += 1; };
	const restart = () => { picks = []; idx = 0; };
	const proof = (c: WhoseJobCard) => {
		if (c.proof) return c.proof;
		const f = c.fact ? facts[c.fact] : undefined;
		return f ? { title: f.primary.title + (f.primary.locator ? `, ${f.primary.locator}` : ''), url: pdfPageLink(f.primary.url, f.primary.locator) } : null;
	};
</script>

{#snippet building(l: Level)}
	<svg viewBox="0 0 300 210" preserveAspectRatio="xMidYMax meet" aria-hidden="true">
		<rect width="300" height="210" fill={SKY[l]} />
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
{/snippet}

<div class="game sans">
	<!-- One quiet row: which question you're on, with a dot per question (green right, orange missed). -->
	<div class="progress" aria-label="Question {Math.min(idx + 1, cards.length)} of {cards.length}">
		<span class="num">{finished ? 'Done' : `Question ${idx + 1} of ${cards.length}`}</span>
		{#each cards as c, i (c.thing)}<i class={picks[i] ? (picks[i] === c.answer ? 'ok' : 'miss') : i === idx ? 'cur' : ''}></i>{/each}
	</div>

	{#if !finished}
		<p class="ask">
			<span class="thing">Who decides {lc(card.thing)}?</span>
			<span class="hint">{pick ? '' : 'Tap who decides it.'}</span>
		</p>

		<div class="play" class:answered={!!pick}>
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
						{@render building(l)}
						<span class="cap"><b>{PLACE[l].level}</b><small>{PLACE[l].who}</small></span>
					</button>
				{/each}
			</div>
			<div class="side" aria-live="polite">
				{#if pick}
					{@const p = proof(card)}
					<div class="answer lv-{card.answer}">
						<div class="arow"><span class="badge {card.answer}">{PLACE[card.answer].level}</span><span class="verdict">{pick === card.answer ? 'Correct.' : `Not quite. It's ${PLACE[card.answer].who}.`}</span></div>
						<p class="explain">{card.explain}</p>
						{#if p}<a class="proof" href={p.url} target="_blank" rel="noopener">Proof: {p.title} ↗</a>{/if}
						<button class="go" onclick={next}>{idx === cards.length - 1 ? 'See your score' : 'Next question →'}</button>
					</div>
				{:else}
					<div class="waiting">Tap who decides it: the <b>City</b> (Toronto), the <b>Province</b> (Ontario) or the <b>Federal</b> government (Canada).</div>
				{/if}
			</div>
		</div>

	{:else}
		<div class="results">
			<div class="rhead">
				<p class="scorebig">You got <b>{score}</b> of {cards.length}</p>
				<p class="explain">Here's who decides what. <b>Everything under City Hall is what the mayor and council you elect on October 26 control.</b></p>
			</div>
			<div class="rcols">
				{#each LEVELS as l (l)}
					<div class="rcol {l}">
						<div class="rart">{@render building(l)}</div>
						<div class="rcap"><b>{PLACE[l].level}</b><small>{PLACE[l].who}</small>{#if l === 'city'}<span class="ballot-tag">On your ballot Oct 26</span>{/if}</div>
						<ul>
							{#each cards.map((c, i) => ({ c, i })).filter((x) => x.c.answer === l) as x (x.c.thing)}
								<li class:got={picks[x.i] === l}><span class="mark" aria-label={picks[x.i] === l ? 'You got this' : 'You missed this'}>{picks[x.i] === l ? '✓' : '·'}</span>{x.c.thing}</li>
							{/each}
						</ul>
					</div>
				{/each}
			</div>
			<button class="again" onclick={restart}>Ride again</button>
		</div>
	{/if}
</div>

<style>
	.game { margin-top: 16px; }
	/* Sits on the section flag's line, at the right, like a page number. */
	.progress { display: flex; justify-content: flex-end; align-items: center; gap: 5px; margin: -33px 0 16px auto; width: fit-content; }
	.progress .num { margin-right: 6px; }
	.progress i { width: 9px; height: 9px; border-radius: 50%; background: #e2ddd2; transition: background 0.3s, transform 0.3s; }
	.progress .cur { background: var(--ink); transform: scale(1.25); }
	.progress .ok { background: #4a8c5c; }
	.progress .miss { background: #d9822b; }
	.ask { margin: 0 0 10px; display: flex; flex-direction: column; gap: 2px; }
	.num { font-size: 13px; font-weight: 600; color: var(--mute); }
	/* On narrow screens there's no room beside the stop title, so the counter drops below it. */
	@media (max-width: 640px) { .progress { margin: -4px 0 12px 0; } }
	.thing { font-family: var(--display); font-size: clamp(28px, 4vw, 40px); font-weight: 700; line-height: 1.1; letter-spacing: 0; }
	.hint { font-size: 13px; color: var(--mute); min-height: 1em; }
	/* Three postcards, one per government. Each fits a third of the play area, so the question,
	   the buildings and the answer all fit on one screen. */
	.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; width: 100%; height: clamp(200px, min(calc(100vh - 470px), 26cqw), 340px); }
	.card { font: inherit; padding: 0; border: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); border-radius: 16px; background: #fff; overflow: hidden; cursor: pointer; display: flex; flex-direction: column; box-shadow: 0 2px 6px rgb(0 0 0 / 0.06); transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s, opacity 0.3s; }
	.card svg { display: block; width: 100%; flex: 1; min-height: 0; }
	.card.city { background: #dce8f5; } .card.province { background: #f6e6d6; } .card.federal { background: #dfeee3; }
	.cap { background: #fff; }
	.cap { display: flex; flex-direction: column; align-items: center; padding: 8px 6px 10px; line-height: 1.2; }
	.cap b { font-size: 18px; } .cap small { font-size: 13px; color: var(--mute); }
	.card.city .cap b { color: #2f5d9b; } .card.province .cap b { color: #b56a1c; } .card.federal .cap b { color: #3d7a4e; }
	.card:not(:disabled):hover, .card:focus-visible { transform: translateY(-3px); box-shadow: 0 10px 22px rgb(0 0 0 / 0.12); }
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
	.waiting { align-self: center; font-size: 15px; line-height: 1.5; color: var(--ink-2); border-left: 3px solid var(--rule); padding: 4px 0 4px 16px; width: 100%; }
	.arow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
	.arow .verdict { margin: 0; }
	.results { animation: pop 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); }
	.rhead { display: flex; align-items: baseline; gap: 6px 22px; flex-wrap: wrap; margin-bottom: 14px; }
	.scorebig { font-family: var(--display); font-weight: 700; font-size: 30px; margin: 0; }
	.scorebig b { font-size: 44px; color: #da251d; }
	.rhead .explain { margin: 0; font-size: 15px; flex: 1; min-width: 260px; }
	.rcols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 940px; }
	.rcol { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: var(--pop); border: var(--line); }
	.rcol.city { border-color: #2f5d9b; }
	.rart { height: 64px; } .rart :global(svg) { width: 100%; height: 100%; display: block; }
	.rcol.city .rart { background: #dce8f5; } .rcol.province .rart { background: #f6e6d6; } .rcol.federal .rart { background: #dfeee3; }
	.rcap { display: flex; flex-direction: column; align-items: center; padding: 6px 10px 2px; line-height: 1.2; }
	.rcap b { font-size: 15px; } .rcap small { font-size: 11.5px; color: var(--mute); }
	.rcol.city .rcap b { color: #2f5d9b; } .rcol.province .rcap b { color: #b56a1c; } .rcol.federal .rcap b { color: #3d7a4e; }
	.ballot-tag { margin-top: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; background: #2f5d9b; color: #fff; border-radius: 999px; padding: 3px 10px; }
	.rcol ul { list-style: none; margin: 0; padding: 6px 12px 12px; display: grid; gap: 4px; font-size: 13px; line-height: 1.3; }
	.rcol li { display: flex; gap: 8px; color: var(--ink-2); }
	.mark { flex: none; width: 16px; height: 16px; border-radius: 50%; display: grid; place-items: center; font-size: 11px; font-weight: 800; background: #ece8df; color: var(--mute); margin-top: 1px; }
	.got .mark { background: #4a8c5c; color: #fff; }
	.again { font: inherit; font-weight: 700; font-size: 14px; background: #fff; border: var(--line); border-radius: 999px; padding: 8px 18px; cursor: pointer; margin-top: 14px; box-shadow: 2px 2px 0 var(--ink); }
	.answer { margin-top: 14px; background: #fff; border-radius: 18px; padding: 18px 20px; border: var(--line); box-shadow: var(--pop); animation: pop 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); }
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
	/* Mid-quiz this is the main button (the page's Next stop goes quiet until the score shows), so it's solid. */
	.go { font: inherit; font-weight: 700; font-size: 15px; background: var(--ink); color: #fff; border: var(--line); border-radius: 999px; padding: 9px 20px; cursor: pointer; box-shadow: 2px 2px 0 var(--ink); transition: transform 0.15s, box-shadow 0.15s; }
	.go:hover { transform: translate(-1px, -1px); box-shadow: var(--pop); }
	.hint { display: none; }
	@media (max-width: 860px) { .play { grid-template-columns: 1fr; } .waiting { display: none; } .hint { display: block; } }
	@media (max-width: 600px) {
		.cards { gap: 6px; height: auto; } .card svg { flex: none; height: auto; }
		.card { border-radius: 12px; }
		.cap { padding: 5px 2px 7px; } .cap b { font-size: 13px; } .cap small { font-size: 9.5px; }
		.rcols { grid-template-columns: 1fr; } .rart { display: none; }
		/* Phones: once you've answered, the pictures fold down to their labels so the answer and
		   'Next question' fit on the screen without scrolling. */
		.thing { font-size: 24px; }
		.answered .card svg { display: none; }
		.answer { margin-top: 10px; padding: 14px 16px; }
		.explain { font-size: 15px; margin: 6px 0; }
		.proof { margin-bottom: 10px; }
		/* Full width on phones: easy for either thumb, and unlike the Skip pill below it. */
		.go { display: block; width: 100%; padding: 12px 20px; }
	}
	@media (prefers-reduced-motion: reduce) { .card, .answer { transition: none; animation: none; } }
</style>
