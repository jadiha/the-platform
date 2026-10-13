import fs from 'node:fs';
import path from 'node:path';
import { loadSources } from '#lib/server/data.ts';

const DATA_DIR = path.resolve(process.cwd(), '..', 'data');

function readCsv(file: string): { original_line: string; category: string; notes: string }[] {
	const p = path.join(DATA_DIR, 'mappings', file);
	if (!fs.existsSync(p)) return [];
	const [, ...lines] = fs.readFileSync(p, 'utf8').trim().split('\n');
	return lines.map((line) => {
		// Minimal CSV: fields may be quoted, quotes inside are not used in these files.
		const cells = [...line.matchAll(/"([^"]*)"|([^,]+)|(?<=,)(?=,|$)/g)].map((m) => m[1] ?? m[2] ?? '');
		return { original_line: cells[0], category: cells[1], notes: cells[2] ?? '' };
	});
}

function trendNotes(): string[] {
	const out: string[] = [];
	for (const f of ['trends-ontario.json', 'trends-toronto.json']) {
		const p = path.join(DATA_DIR, 'clean', f);
		if (!fs.existsSync(p)) continue;
		const d = JSON.parse(fs.readFileSync(p, 'utf8'));
		for (const n of [...(d.notes ?? []), ...(d['toronto-notes'] ?? [])]) out.push(String(n));
	}
	return out;
}

export const load = () => ({
	sources: loadSources(),
	mappings: { toronto: readCsv('toronto.csv'), ontario: readCsv('ontario.csv') },
	trendNotes: trendNotes()
});
