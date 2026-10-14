// The election ride is the front door; the Scarborough walk now lives at /walk/.
import { redirect } from '@sveltejs/kit';

export const load = () => redirect(307, '/vote/');
