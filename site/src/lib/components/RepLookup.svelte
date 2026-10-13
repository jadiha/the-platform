<script lang="ts">
	// Postal code → ward and ridings via Open North's Represent API (boundaries only).
	// Names come from our own people.yaml, built from official lists, because Represent's
	// representative names can lag behind by-elections.
	import PersonCard from './PersonCard.svelte';
	import { siteData } from '#lib/context.ts';
	import type { Person } from '#lib/types.ts';

	const SETS = {
		'toronto-wards-2018': { level: 'city', label: 'City councillor', official: 'https://www.toronto.ca/city-government/council/members-of-council/' },
		'ontario-electoral-districts-representation-act-2015': { level: 'province', label: 'MPP (Ontario)', official: 'https://www.ola.org/en/members/current' },
		'federal-electoral-districts-2023-representation-order': { level: 'federal', label: 'MP (Canada)', official: 'https://www.ourcommons.ca/members/en' }
	} as const;
	type SetKey = keyof typeof SETS;

	const { people } = siteData();
	let code = $state('');
	let status = $state<'idle' | 'loading' | 'error' | 'done'>('idle');
	let error = $state('');
	let results = $state<{ set: SetKey; area: string; person?: Person }[]>([]);

	const norm = (s: string) => s.toLowerCase().replace(/[—–-]/g, ' ').replace(/\s+/g, ' ').trim();

	function findPerson(level: string, area: string): Person | undefined {
		const a = norm(area);
		return people.find((p) => p.level === level && p.ward_or_riding && norm(p.ward_or_riding).includes(a));
	}

	async function lookup(e: SubmitEvent) {
		e.preventDefault();
		const pc = code.toUpperCase().replace(/\s/g, '');
		if (!/^[A-Z]\d[A-Z]\d[A-Z]\d$/.test(pc)) {
			status = 'error';
			error = 'That doesn’t look like a postal code. Try something like M1P 4N7.';
			return;
		}
		status = 'loading';
		try {
			const res = await fetch(`https://represent.opennorth.ca/postcodes/${pc}/`);
			if (!res.ok) throw new Error(res.status === 404 ? 'We couldn’t find that postal code.' : 'The lookup service is busy. Try again in a minute.');
			const d = await res.json();
			const seen = new Set<string>();
			const out: typeof results = [];
			for (const b of [...(d.boundaries_concordance ?? []), ...(d.boundaries_centroid ?? [])]) {
				const set = (b.related?.boundary_set_url ?? '').split('/').filter(Boolean).pop() as SetKey;
				if (!(set in SETS) || seen.has(set + b.name)) continue;
				seen.add(set + b.name);
				out.push({ set, area: b.name, person: findPerson(SETS[set].level, b.name) });
			}
			out.sort((a, b) => Object.keys(SETS).indexOf(a.set) - Object.keys(SETS).indexOf(b.set));
			results = out;
			status = 'done';
		} catch (err) {
			status = 'error';
			error = err instanceof Error ? err.message : 'Something went wrong.';
		}
	}

	const multiple = $derived(
		(Object.keys(SETS) as SetKey[]).some((s) => results.filter((r) => r.set === s).length > 1)
	);
</script>

<form class="lookup sans" onsubmit={lookup}>
	<label for="pc" class="visually-hidden">Postal code</label>
	<input id="pc" bind:value={code} placeholder="Postal code, e.g. M1P 4N7" autocomplete="postal-code" maxlength="7" />
	<button type="submit" disabled={status === 'loading'}>{status === 'loading' ? 'Looking…' : 'Find my reps'}</button>
</form>
<p class="privacy sans">Your postal code is sent to Open North’s free Represent service to find your area. We don’t store it.</p>

{#if status === 'error'}
	<p class="err sans" role="alert">{error}</p>
{:else if status === 'done'}
	{#if multiple}
		<p class="warn sans">Your postal code crosses a boundary, so we’re showing every possible match. Your exact address decides which one is yours.</p>
	{/if}
	<div class="results">
		{#each results as r (r.set + r.area)}
			<div>
				<p class="kicker">{SETS[r.set].label} · {r.area}</p>
				{#if r.person}
					<PersonCard person={r.person} compact />
				{:else}
					<p class="none sans">
						We haven’t added this {SETS[r.set].level === 'city' ? 'ward' : 'riding'} yet, or the seat may be vacant.
						<a href={SETS[r.set].official} target="_blank" rel="noopener">See the official list →</a>
					</p>
				{/if}
			</div>
		{/each}
	</div>
{/if}

<style>
	.lookup { display: flex; gap: 8px; margin: 14px 0 4px; flex-wrap: wrap; }
	input { flex: 1 1 200px; font: inherit; font-size: 16px; padding: 10px 12px; border: 1px solid var(--ink); background: #fff; }
	button { font: inherit; font-weight: 600; font-size: 15px; padding: 10px 18px; background: var(--ink); color: #fff; border: 0; cursor: pointer; }
	button:disabled { opacity: 0.6; }
	.privacy { font-size: 11.5px; color: var(--mute); margin: 0 0 14px; }
	.err { color: #b02a37; font-size: 14px; }
	.warn { background: #fdf1e4; padding: 8px 12px; font-size: 13px; }
	.results { display: grid; gap: 18px; margin-top: 8px; }
	.kicker { color: var(--mute); margin: 0; }
	.none { font-size: 13.5px; color: var(--ink-2); }
</style>
