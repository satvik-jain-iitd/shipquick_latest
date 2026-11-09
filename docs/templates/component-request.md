# Component request

Copy this into a new issue in the ShipQuick kit repo (the libraries live in `ui/android/` and `ui/ios/`). Add the label `component-request`.
The coder fills every line below. Then the coder stops work on that part of the screen.
Full rule: `docs/COMPONENT_LIBRARY.md`.

Screen: <the screen and its board on the canvas>
What is missing: <what the screen needs that no component does>
Tried: <each component you tried, and why it cannot do it>
Picture: <link to a sketch, screenshot or canvas board>
Platform twin: <the issue for the same component on the other platform>

## How the owner's yes is recorded

The coder writes this body, so the owner's yes never goes here.
After the owner says yes, a reviewer account posts an issue comment on this issue:
`Owner yes: <date> "<his words>"`.
The same reviewer account adds the label `component-approved`.
Only that comment and that label count. Story S8 (#186) checks both.
No approved comment and label, no build.
