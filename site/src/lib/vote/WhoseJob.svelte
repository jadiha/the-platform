<script lang="ts">
	// "Whose job is it?": tap the building that decides it (City Hall, Queen's Park or Parliament
	// Hill). It lights up, and the answer with its proof appears beside the scene.
	import { siteData } from '#lib/context.ts';
	import { pdfPageLink } from './links.ts';
	import type { WhoseJobCard } from '#lib/types.ts';

	let { cards }: { cards: WhoseJobCard[] } = $props();
	const { facts } = siteData();
	const LEVELS = ['city', 'province', 'federal'] as const;
	type Level = (typeof LEVELS)[number];
	const PLACE: Record<Level, { name: string; level: string; x: number }> = {
		city: { name: 'City Hall', level: 'City', x: 17 },
		province: { name: "Queen's Park", level: 'Province', x: 50 },
		federal: { name: 'Parliament Hill', level: 'Federal', x: 83 }
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
			<span class="num">{idx + 1} of {cards.length} · Who decides…</span>
			<span class="thing">{card.thing}?</span>
			<span class="hint">{pick ? '' : 'Tap the building that decides it.'}</span>
		</p>

		<div class="play">
			<div class="scene">
				<div class="stage">
			<svg viewBox="0 0 900 380" preserveAspectRatio="xMidYMax meet" aria-hidden="true">
				<defs>
					<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9cc7ef" /><stop offset="1" stop-color="#e8f2fb" /></linearGradient>
				</defs>
				<rect width="900" height="380" fill="url(#sky)" />
				<g fill="#fff" opacity=".7"><ellipse cx="160" cy="60" rx="70" ry="10" /><ellipse cx="640" cy="40" rx="90" ry="9" /></g>
				<!-- far skyline -->
				<g fill="#a9bccd">
					<rect x="20" y="170" width="40" height="140" /><rect x="70" y="200" width="30" height="110" /><rect x="250" y="160" width="36" height="150" />
					<rect x="292" y="190" width="28" height="120" /><rect x="545" y="150" width="34" height="160" /><rect x="585" y="185" width="30" height="125" />
					<rect x="850" y="175" width="40" height="135" /><rect x="820" y="205" width="24" height="105" />
				</g>
				<!-- CN Tower -->
				<g fill="#8fa3b6">
					<path d="M640 310 L652 120 L658 120 L670 310 Z" />
					<ellipse cx="655" cy="128" rx="17" ry="9" />
					<rect x="652" y="40" width="6" height="82" />
					<ellipse cx="655" cy="92" rx="7" ry="4" />
				</g>
				<!-- City Hall: two curved towers and the saucer -->
				<g class="bld" class:chosen={pick === 'city'}>
					<path d="M92 300 L92 150 Q118 122 142 118 L142 300 Z" fill="#dfe3e6" stroke="#7d8a95" stroke-width="2" />
					<path d="M212 300 L212 178 Q190 156 166 152 L166 300 Z" fill="#dfe3e6" stroke="#7d8a95" stroke-width="2" />
					<g stroke="#9aa7b2" stroke-width="1">{#each [170, 190, 210, 230, 250, 270] as y (y)}<line x1="96" y1={y} x2="140" y2={y} />{/each}{#each [195, 215, 235, 255, 275] as y (y)}<line x1="168" y1={y} x2="208" y2={y} />{/each}</g>
					<ellipse cx="154" cy="284" rx="34" ry="10" fill="#f4f5f6" stroke="#7d8a95" stroke-width="2" />
					<rect x="70" y="292" width="164" height="10" fill="#c9ced3" />
				</g>
				<!-- Queen's Park: pink sandstone legislature -->
				<g class="bld" class:chosen={pick === 'province'}>
					<rect x="362" y="232" width="176" height="70" fill="#c98c77" stroke="#8a5545" stroke-width="2" />
					<path d="M362 232 L380 214 L520 214 L538 232 Z" fill="#a8695a" />
					<rect x="434" y="168" width="32" height="64" fill="#c98c77" stroke="#8a5545" stroke-width="2" />
					<path d="M430 168 L450 140 L470 168 Z" fill="#8a5545" />
					<g fill="#6b3d31">{#each [378, 402, 426, 462, 486, 510] as x (x)}<path d="M{x} 300 L{x} 274 Q{x + 7} 264 {x + 14} 274 L{x + 14} 300 Z" />{/each}<path d="M440 300 L440 268 Q450 254 460 268 L460 300 Z" /></g>
				</g>
				<!-- Parliament Hill: Peace Tower -->
				<g class="bld" class:chosen={pick === 'federal'}>
					<rect x="672" y="244" width="156" height="58" fill="#d8cba9" stroke="#8c7f5f" stroke-width="2" />
					<path d="M672 244 L690 226 L810 226 L828 244 Z" fill="#5c9c87" />
					<rect x="734" y="142" width="32" height="102" fill="#d8cba9" stroke="#8c7f5f" stroke-width="2" />
					<path d="M730 142 L750 96 L770 142 Z" fill="#5c9c87" />
					<circle cx="750" cy="162" r="7" fill="#fff" stroke="#8c7f5f" stroke-width="1.5" />
					<g fill="#7a6c4d">{#each [686, 706, 784, 804] as x (x)}<rect {x} y="262" width="10" height="22" rx="2" />{/each}<rect x="740" y="270" width="20" height="32" rx="8" /></g>
				</g>
				<!-- street and tracks -->
				<rect y="302" width="900" height="78" fill="#7a7f85" />
				<rect y="302" width="900" height="6" fill="#b9bdc1" />
				<g stroke="#c9ccd0" stroke-width="2.5"><line x1="0" y1="352" x2="900" y2="352" /><line x1="0" y1="364" x2="900" y2="364" /></g>
				<line x1="0" y1="318" x2="900" y2="318" stroke="#5a5f64" stroke-width="1" />
			</svg>

			{#each LEVELS as l (l)}
				<button
					class="pick {l}"
					class:correct={pick && l === card.answer}
					class:wrong={pick === l && l !== card.answer}
					style="left:{PLACE[l].x}%"
					disabled={!!pick}
					onclick={() => choose(l)}
					aria-label="{PLACE[l].name}: {PLACE[l].level} government"
				>
					<span class="chip"><b>{PLACE[l].level}</b><small>{PLACE[l].name}</small></span>
				</button>
			{/each}

				</div>
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
	.num { font-size: 12px; font-weight: 600; letter-spacing: 1.2px; color: var(--mute); text-transform: uppercase; }
	.thing { font-family: var(--serif); font-size: clamp(22px, 3.6vw, 30px); font-weight: 700; line-height: 1.15; letter-spacing: -0.5px; }
	.hint { font-size: 13px; color: var(--mute); min-height: 1em; }
	/* The scene keeps its shape but never grows taller than about half the screen, so the
	   question, the buildings and the answer all fit without scrolling. */
	.scene { position: relative; aspect-ratio: 900 / 380; width: min(100%, calc(46vh * 900 / 380)); margin: 0 auto 64px; }
	.stage { position: relative; width: 100%; height: 100%; }
	.play { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(240px, 1fr); gap: 16px; align-items: stretch; }
	.side { display: flex; }
	.side .answer { margin: 0; width: 100%; }
	.waiting { align-self: center; font-size: 15px; color: var(--ink-2); background: #fff; border: 1px dashed var(--rule); border-radius: 18px; padding: 18px; width: 100%; }
	.arow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
	.arow .verdict { margin: 0; }
	.arow.foot { justify-content: space-between; }
	.arow.foot .proof { margin: 0; flex: 1; min-width: 160px; }
	.scene svg { display: block; width: 100%; height: auto; border-radius: 18px; overflow: hidden; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1); }
	.bld { transition: filter 0.4s, transform 0.4s; transform-origin: center bottom; transform-box: fill-box; }
	.bld.chosen { filter: drop-shadow(0 0 14px rgba(255, 214, 102, 1)) brightness(1.08); transform: translateY(-4px); }
	.pick { position: absolute; top: 14%; bottom: -60px; width: 30%; transform: translateX(-50%); background: none; border: 0; cursor: pointer; display: flex; align-items: flex-end; justify-content: center; padding: 0; }
	.pick:disabled { cursor: default; }
	.chip { display: flex; flex-direction: column; align-items: center; min-width: 120px; background: #fff; border: 1.5px solid var(--rule); border-radius: 12px; padding: 6px 14px; line-height: 1.15; transition: transform 0.2s, background 0.2s, border-color 0.2s; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06); }
	.pick.city .chip b { color: #2f5d9b; } .pick.province .chip b { color: #b56a1c; } .pick.federal .chip b { color: #3d7a4e; }
	.pick.correct .chip b { color: #fff; }
	.chip b { font-size: 15px; }
	.chip small { font-size: 11px; color: var(--ink-2); }
	.pick:not(:disabled):hover .chip, .pick:focus-visible .chip { transform: translateY(-4px) scale(1.05); }
	.pick.city:not(:disabled):hover .chip { border-color: #2f5d9b; }
	.pick.province:not(:disabled):hover .chip { border-color: #d9822b; }
	.pick.federal:not(:disabled):hover .chip { border-color: #4a8c5c; }
	.pick.correct .chip { color: #fff; border-color: transparent; }
	.pick.city.correct .chip { background: #2f5d9b; }
	.pick.province.correct .chip { background: #d9822b; }
	.pick.federal.correct .chip { background: #4a8c5c; }
	.pick.correct .chip small { color: #fff; }
	.pick.wrong .chip { text-decoration: line-through; opacity: 0.7; }
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
		.chip { min-width: 0; padding: 5px 9px; } .chip small { font-size: 10px; } .scene { margin-bottom: 58px; }
		.scene .answer { position: static; transform: none; width: auto; margin-top: 10px; }
		.chip { padding: 3px 7px; border-radius: 9px; }
		.chip b { font-size: 12px; }
		.chip small { font-size: 9px; }
			.cols { grid-template-columns: 1fr; }
	}
	@media (prefers-reduced-motion: reduce) { .chip, .answer, .bld { transition: none; animation: none; } }
</style>
