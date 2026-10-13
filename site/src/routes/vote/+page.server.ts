const dev = import.meta.env.DEV;
import { loadMayorPromises, loadOfficialCandidates, loadWards } from '#lib/server/data.ts';

export const load = () => ({
	...loadMayorPromises(dev),
	official: loadOfficialCandidates(),
	wards: loadWards()
});
