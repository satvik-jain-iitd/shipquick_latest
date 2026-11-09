// Story #183 (S3, ADR-012): the kit's integration for Meta's Astryx CLI, used as shipped.
// It registers NO web component (the web uses @astryxdesign/core's own docs). Android and iOS components are
// reference topics in ./docs, generated from ui/components/ by scripts/ui_topics.py; S2's check_ui_docs.py
// checks the source. The agent text below is appended to the CLI's managed AGENTS.md block by `astryx init`.
export default {
  docs: './docs',
  agentDocs: {
    append: [
      'ShipQuick rule 38 (Library first): build every screen only from library components and start it from a template.',
      'Before you use a native component, read it: `bash knowledge/shipquick_latest/scripts/ui.sh docs android-<name> --dense` (or ios-<name>).',
      'Android: Jetpack Compose Material 3 as Google ships it. No raw Box, Canvas, custom Shape or Color(0x...) in app code.',
      'iOS: SwiftUI as Apple ships it. No raw Shape, Color(red:...) or magic padding numbers; use the tokens.',
      'SELF-CHECK: re-read the file you wrote; swap any raw element for the library component or token.',
      'Nothing fits: file a component-request (docs/templates/component-request.md) and stop. Never build a stand-in.',
    ],
  },
  issuesUrl: 'https://github.com/satvik-jain-iitd/shipquick_latest/issues',
};
