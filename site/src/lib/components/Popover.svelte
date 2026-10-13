<script lang="ts">
	import type { Snippet } from 'svelte';

	let { trigger, children, label }: { trigger: Snippet; children: Snippet; label: string } = $props();
	let open = $state(false);
	let root: HTMLSpanElement;

	function onDocClick(e: MouseEvent) {
		if (open && !root.contains(e.target as Node)) open = false;
	}
</script>

<svelte:document onclick={onDocClick} onkeydown={(e) => e.key === 'Escape' && (open = false)} />

<span class="pop" bind:this={root}>
	<button type="button" class="trigger" aria-expanded={open} aria-label={label} onclick={() => (open = !open)}>
		{@render trigger()}
	</button>
	{#if open}
		<span class="panel sans" role="dialog" aria-label={label}>
			{@render children()}
		</span>
	{/if}
</span>

<style>
	.pop { position: relative; display: inline; }
	.trigger {
		all: unset; cursor: pointer; display: inline;
		font: inherit; color: inherit;
	}
	.trigger:focus-visible { outline: 2px solid var(--c-transit); outline-offset: 2px; }
	.panel {
		position: absolute; left: 0; top: calc(100% + 8px); z-index: 30;
		width: min(320px, 80vw); background: var(--ink); color: #fff;
		font-size: 13px; line-height: 1.5; padding: 12px 14px; text-align: left;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
		animation: in 0.15s ease-out;
	}
	@keyframes in { from { opacity: 0; transform: translateY(-4px); } }
	.panel :global(a) { color: #fff; }
</style>
