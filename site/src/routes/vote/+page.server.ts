import { loadMayorProfiles, loadMayorPromises, loadOfficialCandidates, loadWhoseJob } from '#lib/server/data.ts';

const dev = import.meta.env.DEV;

export const load = () => ({
	...loadMayorPromises(dev),
	...loadMayorProfiles(dev),
	official: loadOfficialCandidates(),
	whoseJob: loadWhoseJob()
});
