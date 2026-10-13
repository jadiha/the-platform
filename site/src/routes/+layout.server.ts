import { loadFacts, loadPeople } from '#lib/server/data.ts';

export const load = () => ({ facts: loadFacts(), people: loadPeople() });
