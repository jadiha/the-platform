// Pre-build content checks (spec §8). Fails the build when:
//  1. a <Fact id="..."> refers to a fact that isn't in data/facts/*.yaml
//  2. a fact record is missing required fields, or its status isn't backed up
//  3. story copy contains a money/percent figure typed by hand instead of a <Fact>
import fs from 'node:fs';
import path from 'node:path';
import * as yaml from 'js-yaml';

const ROOT = path.resolve(import.meta.dirname, '..');
const FACTS_DIR = path.resolve(ROOT, '..', 'data', 'facts');
const errors = [];

const facts = {};
for (const f of fs.existsSync(FACTS_DIR) ? fs.readdirSync(FACTS_DIR).filter((n) => n.endsWith('.yaml')) : []) {
	for (const [id, fact] of Object.entries(yaml.load(fs.readFileSync(path.join(FACTS_DIR, f), 'utf8')) ?? {})) {
		if (facts[id]) errors.push(`duplicate fact id ${id} (${f})`);
		facts[id] = fact;
		for (const k of ['value', 'unit', 'label', 'primary', 'status', 'as_of']) {
			if (fact[k] === undefined || fact[k] === null || fact[k] === '') errors.push(`${f}: ${id} is missing "${k}"`);
		}
		if (!fact.primary?.url) errors.push(`${f}: ${id} primary source has no url`);
		if (fact.status === 'verified' && !(fact.crosscheck?.length > 0)) errors.push(`${f}: ${id} is "verified" but has no crosscheck`);
		if (fact.status === 'disagree' && !fact.note) errors.push(`${f}: ${id} is "disagree" but has no note explaining why`);
		if (!['verified', 'single', 'disagree', 'reported'].includes(fact.status)) errors.push(`${f}: ${id} has unknown status "${fact.status}"`);
	}
}

const files = [];
(function walk(dir) {
	for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
		const p = path.join(dir, e.name);
		if (e.isDirectory()) walk(p);
		else if (p.endsWith('.svelte')) files.push(p);
	}
})(path.join(ROOT, 'src'));

// Hand-typed figures in copy: "$4", "2.2%", "18 billion", "500 million".
const FIGURE = /\$\s?\d|\d+(?:\.\d+)?\s?%|\d+(?:\.\d+)?\s?(?:billion|million)\b/i;

for (const file of files) {
	const rel = path.relative(ROOT, file);
	const src = fs.readFileSync(file, 'utf8');
	for (const m of src.matchAll(/<Fact\s+id="([^"]+)"/g)) {
		if (!facts[m[1]]) errors.push(`${rel}: <Fact id="${m[1]}"> not found in data/facts`);
	}
	// Only routes hold story copy. Strip script/style blocks and {expressions}.
	if (!rel.startsWith(path.join('src', 'routes'))) continue;
	const markup = src
		.replace(/<script[\s\S]*?<\/script>/g, (s) => '\n'.repeat(s.split('\n').length - 1))
		.replace(/<style[\s\S]*?<\/style>/g, (s) => '\n'.repeat(s.split('\n').length - 1))
		.replace(/\{[^{}]*\}/g, '');
	markup.split('\n').forEach((line, i) => {
		const text = line.replace(/<[^>]*>/g, ' ');
		if (FIGURE.test(text)) errors.push(`${rel}:${i + 1}: hand-typed figure in copy, use <Fact>: "${text.trim().slice(0, 80)}"`);
	});
}

if (errors.length) {
	console.error(`\n✗ Content check failed (${errors.length}):\n  - ` + errors.join('\n  - ') + '\n');
	if (!process.argv.includes('--warn')) process.exit(1);
} else {
	console.log(`✓ Content check passed: ${Object.keys(facts).length} facts, ${files.length} components`);
}
