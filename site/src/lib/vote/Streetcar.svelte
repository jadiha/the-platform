<script lang="ts">
	// A TTC Flexity streetcar, drawn simply: red body, black window band, grey skirt. Faces right.
	// No pantograph: the ride bar has no overhead wire for it to reach.
	let { width = 100 }: { width?: number } = $props();
</script>

<svg viewBox="0 26 200 44" {width} aria-hidden="true" class="car">
	<!-- Body: three sections with a rounded nose on the right. -->
	<path d="M4 64 L4 32 Q4 27 10 27 L178 27 Q194 27 197 44 L197 64 Z" fill="#da251d" stroke="#8f1712" stroke-width="1.2" />
	<path d="M10 33 L176 33 Q188 33 191 46 L10 46 Z" fill="#1b1f24" />
	<g stroke="#da251d" stroke-width="3">{#each [52, 100, 148] as x (x)}<line x1={x} y1="33" x2={x} y2="46" />{/each}</g>
	<rect x="4" y="56" width="193" height="8" fill="#e9e6e0" stroke="#8f1712" stroke-width="1.2" />
	<g stroke="#8f1712" stroke-width="1">{#each [66, 134] as x (x)}<line x1={x} y1="27" x2={x} y2="64" />{/each}</g>
	<circle cx="192" cy="52" r="2.2" fill="#ffe08a" />
	<g fill="#2a2e33">{#each [24, 92, 162] as x (x)}<rect {x} y="64" width="20" height="6" rx="2" />{/each}</g>
</svg>

<style>
	.car { display: block; height: auto; overflow: visible; }
</style>
