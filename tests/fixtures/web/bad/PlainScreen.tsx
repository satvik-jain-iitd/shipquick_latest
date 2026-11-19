// Fixture (PR #371 review on story #189): a web screen that uses no component library at all. Nothing here is a
// raw element, colour, px or inline style; the only miss is the missing @astryxdesign/core import. The scorer must
// fail it with no_library_import alone. Read as text only; this file is never compiled.
export const PlainScreen = () => <div className="screen">plain</div>;
