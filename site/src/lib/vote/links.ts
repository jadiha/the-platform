// Links that take the reader straight to the proof.

/** Text-fragment link: opens the page scrolled to `text`, highlighted (Chrome, Edge, Safari 16.1+).
 * Browsers without support just open the page. Long quotes use start,end so small edits in the
 * middle don't break the highlight. */
export function highlightLink(url: string, text: string): string {
	const enc = (s: string) => encodeURIComponent(s).replace(/-/g, '%2D').replace(/,/g, '%2C');
	const words = text.replace(/\s+/g, ' ').trim().split(' ');
	const frag = words.length > 12 ? `${enc(words.slice(0, 5).join(' '))},${enc(words.slice(-4).join(' '))}` : enc(words.join(' '));
	const [base, hash] = url.split('#');
	return `${base}#${hash ? hash + ':~:' : ':~:'}text=${frag}`;
}

/** PDFs open at the cited page when the locator says "p. 264". */
export function pdfPageLink(url: string, locator?: string): string {
	const m = locator?.match(/\bp\.\s*(\d+)/);
	return m && /\.pdf($|\?)/i.test(url) ? `${url}#page=${m[1]}` : url;
}

/** "Bradford, Brad" -> "Brad Bradford" */
export const displayName = (ballot: string) => {
	const [last, first] = ballot.split(', ');
	return first ? `${first} ${last}` : ballot;
};
