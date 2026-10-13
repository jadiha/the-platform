import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type Plugin } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

// Dev-only review endpoint: marks one promise in data/candidates/mayor-promises.yaml as checked.
// It only exists in `vite dev` (configureServer), so it can never ship in the static build.
function reviewEndpoint(): Plugin {
	const dir = path.resolve(import.meta.dirname, '..', 'data', 'candidates');
	return {
		name: 'ftb-review',
		configureServer(server) {
			server.middlewares.use('/__review', (req, res) => {
				let body = '';
				req.on('data', (c) => (body += c));
				req.on('end', () => {
					const { file, candidate, url, text } = JSON.parse(body || '{}');
					const target = path.join(dir, file === 'profiles' ? 'mayor-profiles.yaml' : 'mayor-promises.yaml');
					const src = fs.readFileSync(target, 'utf8');
					// Find the block for this item and flip its status line only.
					const blocks = src.split(/\n(?=  - candidate:)/);
					const i =
						file === 'profiles'
							? blocks.findIndex((b) => b.startsWith(`  - candidate: "${candidate}"`) || b.includes(`\n  - candidate: "${candidate}"`))
							: blocks.findIndex((b) => b.includes(`url: ${url}`) && b.includes(JSON.stringify(text).slice(1, 40)));
					if (i < 0 || !/status: draft/.test(blocks[i])) { res.statusCode = 404; return res.end('not found'); }
					const today = new Date().toISOString().slice(0, 10);
					blocks[i] = blocks[i].replace('status: draft', `status: checked\n    checked_on: ${today}`);
					fs.writeFileSync(target, blocks.join('\n'));
					res.end('ok');
				});
			});
		}
	};
}

export default defineConfig({
	plugins: [
		reviewEndpoint(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter({ strict: true })
		})
	],
	// The site reads pipeline output from ../data at build time.
	server: { fs: { allow: ['..'] } }
});
