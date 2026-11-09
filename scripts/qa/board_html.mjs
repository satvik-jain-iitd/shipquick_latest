// Shared by render_boards.mjs and board_controls.mjs: read one design-canvas board (<name>.dc.html) and make it
// open from disk. Relative and root links ("x.css", "/_blob/a.png") point into the canvas folder, and the
// {{theme}} slot gets $QA_THEME (default "light"). Web links, data: and # links are left alone.
import fs from 'node:fs';
import path from 'node:path';

export const VIEWPORT = (() => {   // the board's frame, $QA_VIEWPORT as WxH; default a 390 x 844 phone
  const [width, height] = (process.env.QA_VIEWPORT || '390x844').split('x').map(Number);
  return { width, height };
})();

export function prepare(dir, name) {
  const abs = path.resolve(dir);
  return fs.readFileSync(path.join(abs, name + '.dc.html'), 'utf8')
    .replaceAll('{{theme}}', process.env.QA_THEME || 'light')
    .replace(/\b(href|src)="(?![a-z][a-z0-9+.-]*:|#|\/\/)([^"]+)"/gi, (_, attr, p) => `${attr}="file://${path.join(abs, p)}"`);   // path.join keeps "/x" inside abs
}

export function boards(dir, names) {
  return names.length ? names : fs.readdirSync(dir).filter(f => f.endsWith('.dc.html')).map(f => f.slice(0, -8));
}
