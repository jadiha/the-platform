<script lang="ts">
	import PersonCard from './PersonCard.svelte';
	import { siteData } from '#lib/context.ts';

	let { ids, title = 'Who decides this' }: { ids: string[]; title?: string } = $props();
	const { people } = siteData();
	const list = $derived(ids.map((id) => people.find((p) => p.id === id)).filter((p) => !!p));
</script>

{#if list.length}
	<section class="people">
		<h3 class="kicker">{title}</h3>
		<div class="grid">
			{#each list as person (person.id)}
				<PersonCard {person} compact />
			{/each}
		</div>
	</section>
{/if}

<style>
	.people { margin-top: 22px; }
	h3 { color: var(--mute); margin: 0 0 4px; }
	.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 4px 20px; }
</style>
