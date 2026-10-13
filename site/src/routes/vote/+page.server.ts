import { loadMayorProfiles, loadMayorPromises, loadOfficialCandidates, loadWards, loadWhoseJob } from '#lib/server/data.ts';

const dev = import.meta.env.DEV;

// The ward map only needs each candidate's name and website.
const slim = (c: { name: string; website: string | null }) => ({ name: c.name, website: c.website });

export const load = () => {
	const official = loadOfficialCandidates();
	return {
		...loadMayorPromises(dev),
		...loadMayorProfiles(dev),
		official: official && { source: official.source, school_chart: official.school_chart, mayor: official.mayor },
		races: (official?.wards ?? []).map((w) => ({
			ward: w.ward,
			councillor: w.councillor.map(slim),
			trustees: w.trustees.map((t) => ({ ...t, candidates: t.candidates.map(slim) }))
		})),
		whoseJob: loadWhoseJob(),
		wards: (loadWards()?.wards ?? []).map((w) => ({ ward: w.ward, name: w.name, scarborough: w.scarborough }))
	};
};
