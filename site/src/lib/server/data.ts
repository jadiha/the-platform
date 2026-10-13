// Build-time access to the pipeline's output in ../data (see docs/data-contract.md).
// Missing files return null so the site can still build while the pipeline is incomplete;
// scripts/check-content.mjs is what enforces completeness before deploy.
import fs from 'node:fs';
import path from 'node:path';
import * as yaml from 'js-yaml';
import type { BudgetNode, DataSource, Facts, Person, Trends, Wards } from '#lib/types.ts';

const DATA_DIR = path.resolve(process.cwd(), '..', 'data');

function readText(rel: string): string | null {
	const file = path.join(DATA_DIR, rel);
	return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
}

function readJSON<T>(rel: string): T | null {
	const text = readText(rel);
	return text ? (JSON.parse(text) as T) : null;
}

export function loadFacts(): Facts {
	const dir = path.join(DATA_DIR, 'facts');
	if (!fs.existsSync(dir)) return {};
	const facts: Facts = {};
	for (const name of fs.readdirSync(dir).filter((f) => f.endsWith('.yaml')).sort()) {
		const parsed = yaml.load(fs.readFileSync(path.join(dir, name), 'utf8')) as Facts | null;
		for (const [id, fact] of Object.entries(parsed ?? {})) {
			if (id in facts) throw new Error(`Duplicate fact id "${id}" in data/facts/${name}`);
			facts[id] = normalizeDates(fact);
		}
	}
	return facts;
}

export function loadPeople(): Person[] {
	const text = readText('people.yaml');
	return text ? ((yaml.load(text) as Person[]) ?? []).map(normalizeDates) : [];
}

export const loadBudget = (level: string, year: string) =>
	readJSON<BudgetNode>(`clean/budget-${level}-${year}.json`);

export function loadTrends(): Trends {
	return {
		...(readJSON<Trends>('clean/trends-ontario.json') ?? {}),
		...(readJSON<Trends>('clean/trends-toronto.json') ?? {})
	} as Trends;
}

export const loadWards = () => readJSON<Wards>('clean/wards.json');
export const loadSources = () => readJSON<DataSource[]>('sources.json') ?? [];
export const loadResearch = (name: string) => readText(`../research/${name}.md`);

// js-yaml turns unquoted dates into Date objects; the site wants ISO strings everywhere.
function normalizeDates<T>(value: T): T {
	if (value instanceof Date) return value.toISOString().slice(0, 10) as T;
	if (Array.isArray(value)) return value.map(normalizeDates) as T;
	if (value && typeof value === 'object') {
		return Object.fromEntries(
			Object.entries(value).map(([k, v]) => [k, normalizeDates(v)])
		) as T;
	}
	return value;
}
