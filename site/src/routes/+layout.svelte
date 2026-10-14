<script lang="ts">
	import '../app.css';
	import favicon from '#lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { setSiteData } from '#lib/context.ts';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();
	// svelte-ignore state_referenced_locally
	setSiteData({ facts: data.facts, people: data.people });

	// [link, full label, short label for phones so all four fit on one row]
	const nav = [
		['/vote/', '2026 Election', 'Election'],
		['/explore/budget/', 'Explore the budget', 'Budget'],
		['/glossary/', 'Glossary', 'Glossary'],
		['/sources/', 'Sources', 'Sources']
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

<!-- Election day, said plainly: the date, the hours, and where to go. -->
<div class="election sans" role="note">
	<span>Election day: <strong>Monday, October 26</strong></span>
	<span class="hours">Polls open <strong>10 a.m. to 8 p.m.</strong></span>
	<a href="https://www.toronto.ca/city-government/elections/" target="_blank" rel="noopener">Where to vote ↗</a>
</div>

<header class="masthead">
	<a class="name" href="/vote/">The Platform<span class="tagline">: your vote counts</span></a>
	<nav class="sans" aria-label="Main">
		{#each nav as [href, label, short]}
			<a {href} aria-current={page.url.pathname === href ? 'page' : undefined}><span class="full">{label}</span><span class="short">{short}</span></a>
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
	.election { display: flex; justify-content: center; flex-wrap: wrap; gap: 2px 18px; background: var(--ink); color: #fff; font-size: 13.5px; padding: 8px 20px; text-align: center; }
	.election strong { color: var(--lime); }
	.election a { color: #fff; text-decoration: underline; text-underline-offset: 3px; }
	.short { display: none; }
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
		.election { font-size: 12.5px; padding: 6px 14px; gap: 0 12px; }
		.full { display: none; } .short { display: inline; }
		nav { justify-content: space-between; overflow-x: visible; }
		.masthead { position: static; padding: 10px 14px; gap: 6px; }
		/* One swipeable row of links on phones instead of two wrapped lines. */
		nav { flex-wrap: nowrap; overflow-x: auto; width: calc(100% + 28px); margin: 0 -14px; padding: 2px 14px 4px; scrollbar-width: none; }
		nav::-webkit-scrollbar { display: none; }
		nav a { flex: none; font-size: 13px; }
		.name { font-size: 19px; }
		nav { gap: 4px; } nav a { padding: 3px 9px; }
	}
</style>
