import { getContext, setContext } from 'svelte';
import type { Facts, Person } from '#lib/types.ts';

const KEY = Symbol('site-data');
interface SiteData { facts: Facts; people: Person[] }

export const setSiteData = (d: SiteData) => setContext(KEY, d);
export const siteData = () => getContext<SiteData>(KEY);
