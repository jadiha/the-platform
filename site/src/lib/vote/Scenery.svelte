<script lang="ts">
	// Toronto scenery behind the journey: a soft band at the bottom of the screen that cross-fades
	// from place to place as you ride. Decorative only (hidden from screen readers), muted so text
	// on top stays readable, and still under reduced motion.
	let { scene }: { scene: number } = $props(); // -1 = no scenery
	const WALL = ['#e4572e', '#29a19c', '#f3c623', '#6a4c93', '#ff8c42', '#1982c4', '#8ac926', '#ff595e'];
</script>

<div class="scenery" aria-hidden="true">
	<!-- 0 Harbourfront: the lake, ferry, sailboats, skyline and CN Tower -->
	<svg class:on={scene === 0} viewBox="0 0 1600 400" preserveAspectRatio="xMidYMax slice">
		<g fill="#b9c8d6">
			<rect x="120" y="150" width="70" height="170" /><rect x="200" y="110" width="60" height="210" /><rect x="270" y="170" width="80" height="150" />
			<rect x="980" y="130" width="70" height="190" /><rect x="1060" y="90" width="60" height="230" /><rect x="1130" y="160" width="90" height="160" />
			<rect x="1240" y="120" width="60" height="200" /><rect x="1320" y="180" width="80" height="140" />
		</g>
		<g fill="#a5b6c6"><path d="M690 320 L708 70 L716 70 L734 320 Z" /><ellipse cx="712" cy="86" rx="26" ry="13" /><rect x="709" y="0" width="6" height="74" /></g>
		<rect y="300" width="1600" height="100" fill="#8fb8d8" />
		<g stroke="#cfe2f1" stroke-width="3" fill="none" opacity=".8">
			{#each [330, 355, 380] as y (y)}<path d="M0 {y} q40 -8 80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0 t80 0" />{/each}
		</g>
		<rect y="296" width="1600" height="8" fill="#c8a97e" />
		<g class="drift">
			<path d="M300 330 L420 330 L405 350 L315 350 Z" fill="#fff" stroke="#6b7a88" stroke-width="2" /><rect x="330" y="314" width="60" height="16" fill="#fff" stroke="#6b7a88" stroke-width="2" />
			<path d="M1180 345 L1240 345 L1232 356 L1188 356 Z" fill="#fff" /><path d="M1210 345 L1210 290 L1240 343 Z" fill="#fff" stroke="#9fb2c3" />
			<path d="M520 360 L560 360 L555 368 L525 368 Z" fill="#fff" /><path d="M540 360 L540 322 L560 358 Z" fill="#fff" stroke="#9fb2c3" />
		</g>
	</svg>

	<!-- 1 St. Lawrence Market and the Flatiron (Gooderham) building -->
	<svg class:on={scene === 1} viewBox="0 0 1600 400" preserveAspectRatio="xMidYMax slice">
		<rect y="0" width="1600" height="400" fill="none" />
		<g fill="#c9b8a8"><rect x="80" y="170" width="140" height="160" /><rect x="1380" y="150" width="160" height="180" /></g>
		<g>
			<rect x="420" y="180" width="560" height="150" fill="#c98c77" stroke="#8a5545" stroke-width="3" />
			<path d="M640 180 L700 130 L760 180 Z" fill="#a8695a" stroke="#8a5545" stroke-width="3" />
			<rect x="420" y="170" width="560" height="14" fill="#a8695a" />
			<g fill="#5b3a30">{#each [450, 510, 570, 790, 850, 910] as x (x)}<path d="M{x} 300 L{x} 230 Q{x + 20} 205 {x + 40} 230 L{x + 40} 300 Z" />{/each}</g>
			<path d="M660 330 L660 230 Q700 190 740 230 L740 330 Z" fill="#5b3a30" />
			<rect x="430" y="300" width="540" height="30" fill="#7c4b3d" />
		</g>
		<g>
			<path d="M1080 330 L1080 120 L1150 90 L1260 330 Z" fill="#c26d4f" stroke="#7d3f2b" stroke-width="3" />
			<g fill="#f2e6d8">{#each [140, 175, 210, 245, 280] as y (y)}{#each [1095, 1120, 1145] as x (x)}<rect {x} {y} width="12" height="18" rx="5" />{/each}{/each}</g>
			<path d="M1080 120 L1150 90 L1150 80 L1080 108 Z" fill="#6b8f7a" />
		</g>
		<rect y="330" width="1600" height="70" fill="#9aa0a6" />
		<rect y="330" width="1600" height="6" fill="#c3c7cb" />
	</svg>

	<!-- 2 Graffiti Alley: painted walls, garage doors, fire escapes -->
	<svg class:on={scene === 2} viewBox="0 0 1600 400" preserveAspectRatio="xMidYMax slice">
		<rect x="0" y="90" width="1600" height="250" fill="#d7d2c8" />
		{#each Array.from({ length: 16 }, (_, i) => i) as i (i)}
			{@const x = i * 100}
			<path d="M{x} {340 - (i % 3) * 30} Q{x + 30} {150 + (i % 4) * 25} {x + 60} {300 - (i % 2) * 60} T{x + 120} {200 + (i % 3) * 30} L{x + 120} 340 Z" fill={WALL[i % WALL.length]} opacity=".85" />
			<circle cx={x + 50} cy={150 + (i % 5) * 18} r={14 + (i % 3) * 8} fill={WALL[(i + 3) % WALL.length]} opacity=".9" />
			<path d="M{x + 10} {120 + (i % 2) * 20} l20 -14 l20 14 l20 -14 l20 14" stroke={WALL[(i + 5) % WALL.length]} stroke-width="7" fill="none" stroke-linecap="round" />
		{/each}
		<g fill="#5c5f63" opacity=".9">{#each [260, 760, 1260] as x (x)}<rect {x} y="250" width="120" height="90" rx="3" />{/each}</g>
		<g stroke="#6f7377" stroke-width="2" opacity=".9">{#each [260, 760, 1260] as x (x)}{#each [262, 276, 290, 304, 318, 332] as y (y)}<line x1={x} y1={y} x2={x + 120} y2={y} />{/each}{/each}</g>
		<g stroke="#3d4043" stroke-width="3" fill="none">{#each [520, 1040] as x (x)}<rect {x} y="110" width="90" height="70" /><line x1={x} y1="145" x2={x + 90} y2="145" /><line x1={x + 20} y1="180" x2={x + 70} y2="110" />{/each}</g>
		<rect y="340" width="1600" height="60" fill="#8d8a84" />
	</svg>

	<!-- 3 Chinatown on Spadina: storefronts, signs, lanterns -->
	<svg class:on={scene === 3} viewBox="0 0 1600 400" preserveAspectRatio="xMidYMax slice">
		{#each Array.from({ length: 10 }, (_, i) => i) as i (i)}
			{@const x = i * 160}
			<rect {x} y={120 + (i % 3) * 20} width="156" height={220 - (i % 3) * 20} fill={['#d8c3a5', '#c9b79c', '#e0d2bc'][i % 3]} stroke="#9c8a70" stroke-width="2" />
			<rect x={x + 10} y={150 + (i % 3) * 20} width="136" height="34" rx="4" fill={['#c0392b', '#1f6f5c', '#d4a017', '#2c3e72'][i % 4]} />
			<g fill="#fff" opacity=".85">{#each [0, 1, 2, 3] as k (k)}<rect x={x + 22 + k * 30} y={160 + (i % 3) * 20} width="18" height="14" rx="2" />{/each}</g>
			<rect x={x + 18} y={230} width="120" height="70" fill="#6d7f8c" opacity=".7" />
			<path d="M{x + 8} 225 L{x + 148} 225 L{x + 140} 240 L{x + 16} 240 Z" fill={['#c0392b', '#1f6f5c', '#d4a017'][i % 3]} />
		{/each}
		<path d="M0 95 Q400 135 800 95 T1600 95" stroke="#3d3d3d" stroke-width="2" fill="none" />
		<g fill="#d63a2f">{#each Array.from({ length: 16 }, (_, i) => i) as i (i)}<ellipse cx={50 + i * 100} cy={110 + Math.sin(i) * 6} rx="12" ry="15" /><rect x={46 + i * 100} y={124 + Math.sin(i) * 6} width="8" height="6" fill="#f2c14e" />{/each}</g>
		<rect y="340" width="1600" height="60" fill="#9aa0a6" />
		<g stroke="#c9ccd0" stroke-width="3"><line x1="0" y1="372" x2="1600" y2="372" /><line x1="0" y1="386" x2="1600" y2="386" /></g>
	</svg>

	<!-- 4 Rogers Centre dome beside the CN Tower -->
	<svg class:on={scene === 4} viewBox="0 0 1600 400" preserveAspectRatio="xMidYMax slice">
		<g fill="#b9c8d6"><rect x="1150" y="140" width="80" height="190" /><rect x="1240" y="100" width="60" height="230" /><rect x="1310" y="170" width="90" height="160" /></g>
		<g fill="#a5b6c6"><path d="M960 330 L978 60 L986 60 L1004 330 Z" /><ellipse cx="982" cy="78" rx="28" ry="14" /><rect x="979" y="-10" width="6" height="74" /></g>
		<path d="M380 330 Q380 150 640 140 Q900 150 900 330 Z" fill="#dfe4e8" stroke="#8d99a4" stroke-width="3" />
		<g stroke="#a3afba" stroke-width="2" fill="none">{#each [0.25, 0.42, 0.58, 0.75] as f (f)}<path d="M{380 + f * 520} 330 Q{380 + f * 520} 200 640 142" /><path d="M{900 - f * 520} 330 Q{900 - f * 520} 200 640 142" />{/each}</g>
		<rect x="360" y="300" width="560" height="30" fill="#5d6d7c" />
		<g fill="#fff" opacity=".9">{#each Array.from({ length: 22 }, (_, i) => i) as i (i)}<rect x={372 + i * 24} y="308" width="14" height="10" rx="2" />{/each}</g>
		<rect y="330" width="1600" height="70" fill="#9aa0a6" />
	</svg>

</div>

<style>
	.scenery { position: fixed; left: 0; right: 0; bottom: 0; height: 26vh; z-index: -1; pointer-events: none; }
	.scenery::before { content: ''; position: absolute; inset: 0 0 auto 0; height: 70%; background: linear-gradient(var(--paper), transparent); z-index: 2; }
	svg { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; transition: opacity 1.1s ease; }
	svg.on { opacity: 0.32; }
	.drift { animation: drift 30s linear infinite alternate; }
	@keyframes drift { to { transform: translateX(60px); } }
	@media (max-width: 640px) { .scenery { height: 24vh; } svg.on { opacity: 0.25; } }
	@media (prefers-reduced-motion: reduce) { svg { transition: none; } .drift { animation: none; } }
</style>
