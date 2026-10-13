import { loadMayorProfiles, loadMayorPromises, loadOfficialCandidates, loadWards, loadWhoseJob } from '#lib/server/data.ts';

const dev = import.meta.env.DEV;

export const load = () => ({
	...loadMayorPromises(dev),
	...loadMayorProfiles(dev),
	official: loadOfficialCandidates(),
	whoseJob: loadWhoseJob(),
	wards: (loadWards()?.wards ?? []).map((w) => ({ ward: w.ward, name: w.name, scarborough: w.scarborough }))
});
