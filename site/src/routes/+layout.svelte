<script lang="ts">
	import '../app.css';
	import favicon from '#lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { setSiteData } from '#lib/context.ts';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();
	// svelte-ignore state_referenced_locally
	setSiteData({ facts: data.facts, people: data.people });

	const nav = [
		['/vote/', '2026 Election'],
		['/explore/budget/', 'Explore the budget'],
		['/glossary/', 'Glossary'],
		['/sources/', 'Sources']
	];
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@600;700;800&family=Jost:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400..800;1,6..72,400&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="election sans" role="note">
	Toronto votes <strong>Monday, Oct 26, 2026</strong>.
</div>

<header class="masthead">
	<a class="name" href="/vote/">The Platform<span class="tagline">: your vote counts</span></a>
	<nav class="sans" aria-label="Main">
		{#each nav as [href, label]}
			<a {href} aria-current={page.url.pathname === href ? 'page' : undefined}>{label}</a>
		{/each}
	</nav>
</header>

<main>
	{@render children()}
</main>

{#if page.url.pathname !== '/vote/'}
<footer class="sans">
	<div class="wide">
		<p>
			Every number on this site links to the official document it came from. Spotted an error?
			<a href="/sources/#corrections">Tell us and see past corrections</a>.
		</p>
		<p class="fine">An independent, non-partisan community project. Not affiliated with any government, party or candidate.</p>
	</div>
</footer>
{/if}

<style>
	.election { background: var(--ink); color: #fff; font-size: 13px; padding: 8px 20px; text-align: center; }
	.masthead {
		display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
		border-bottom: var(--line); padding: 14px 20px; position: sticky; top: 0; z-index: 20;
		background: color-mix(in srgb, var(--paper) 94%, transparent); backdrop-filter: blur(6px);
	}
	.tagline { font-weight: 400; font-style: italic; color: var(--red); }
	.name { font-family: var(--display); font-weight: 700; font-size: 21px; letter-spacing: 0; text-decoration: none; }
	nav { display: flex; gap: 6px; font-size: 13.5px; flex-wrap: wrap; }
	nav { align-items: center; }
	nav a { text-decoration: none; color: var(--ink-2); font-weight: 600; border: 1.5px solid transparent; border-radius: 999px; padding: 4px 12px; }
	nav a:hover { color: var(--ink); border-color: var(--ink); }
	nav a[aria-current='page'] { color: var(--ink); background: var(--lime); border-color: var(--ink); box-shadow: 2px 2px 0 var(--ink); }
	footer { border-top: 1px solid var(--ink); margin-top: 80px; padding: 24px 0 40px; font-size: 13px; color: var(--ink-2); }
	.fine { color: var(--mute); }
	@media (max-width: 640px) {
		.election { font-size: 12px; padding: 5px 14px; }
		.masthead { position: static; padding: 10px 14px; gap: 6px; }
		/* One swipeable row of links on phones instead of two wrapped lines. */
		nav { flex-wrap: nowrap; overflow-x: auto; width: calc(100% + 28px); margin: 0 -14px; padding: 2px 14px 4px; scrollbar-width: none; }
		nav::-webkit-scrollbar { display: none; }
		nav a { flex: none; font-size: 13px; }
		.name { font-size: 19px; }
		nav { gap: 4px; } nav a { padding: 3px 9px; }
	}
</style>
