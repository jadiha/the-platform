<script lang="ts">
	// A few maple leaves drifting down behind the last stop. Decorative only: hidden from screen
	// readers, never catches clicks, and holds still under reduced motion.
	const COLORS = ['#d9531e', '#e8892b', '#c0392b', '#f0b429', '#b5651d'];
	const leaves = Array.from({ length: 7 }, (_, i) => ({
		left: (i * 83) % 100,
		delay: -((i * 2.7) % 14),
		dur: 11 + ((i * 5) % 8),
		size: 12 + ((i * 5) % 9),
		color: COLORS[i % COLORS.length],
		sway: i % 2 ? 40 : -40
	}));
</script>

<div class="leaves" aria-hidden="true">
	{#each leaves as l, i (i)}
		<svg viewBox="0 0 40 40" style="left:{l.left}%;width:{l.size}px;animation-delay:{l.delay}s;animation-duration:{l.dur}s;--sway:{l.sway}px">
			<path fill={l.color} d="M20 2 L23 11 L30 8 L28 16 L37 15 L31 22 L35 26 L25 26 L26 33 L21 29 L21 39 L19 39 L19 29 L14 33 L15 26 L5 26 L9 22 L3 15 L12 16 L10 8 L17 11 Z" />
		</svg>
	{/each}
</div>

<style>
	.leaves { position: absolute; top: 0; bottom: 0; left: 50%; width: 100vw; transform: translateX(-50%); pointer-events: none; overflow: hidden; z-index: -1; }
	svg { position: absolute; top: -40px; opacity: 0.6; animation: fall linear infinite; }
	@keyframes fall {
		0% { top: -40px; transform: translateX(0) rotate(0deg); }
		50% { transform: translateX(var(--sway)) rotate(180deg); }
		100% { top: 100%; transform: translateX(0) rotate(360deg); }
	}
	@media (prefers-reduced-motion: reduce) {
		svg { animation: none; top: auto; bottom: 8vh; opacity: 0.5; }
	}
</style>
