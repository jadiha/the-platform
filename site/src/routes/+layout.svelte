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
		href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Libre+Franklin:wght@400;500;600;700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="election sans" role="note">
	Toronto votes <strong>Monday, Oct 26, 2026</strong>.
</div>

<header class="masthead">
	<a class="name" href="/vote/">The 6ix Votes</a>
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
		display: flex; justify-content: space-between; align-items: baseline; gap: 16px; flex-wrap: wrap;
		border-bottom: 1px solid var(--ink); padding: 14px 20px; position: sticky; top: 0; z-index: 20;
		background: color-mix(in srgb, var(--paper) 94%, transparent); backdrop-filter: blur(6px);
	}
	.name { font-weight: 700; font-size: 21px; letter-spacing: -0.3px; text-decoration: none; }
	nav { display: flex; gap: 18px; font-size: 13px; flex-wrap: wrap; }
	nav a { text-decoration: none; color: var(--mute); }
	nav a[aria-current='page'], nav a:hover { color: var(--ink); text-decoration: underline; }
	nav a:first-child { color: #2f5d9b; font-weight: 600; }
	footer { border-top: 1px solid var(--ink); margin-top: 80px; padding: 24px 0 40px; font-size: 13px; color: var(--ink-2); }
	.fine { color: var(--mute); }
	@media (max-width: 640px) {
		.masthead { position: static; }
		nav { gap: 12px; }
	}
</style>
