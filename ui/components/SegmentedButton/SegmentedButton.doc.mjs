/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/segmented-button (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SegmentedButton",
  "displayName": "Segmented button",
  "platforms": {
    "android": "androidx.compose.material3.SegmentedButton",
    "ios": null,
    "web": "@astryxdesign/core/SegmentedControl"
  },
  "group": "Button",
  "category": "Form Controls",
  "keywords": [
    "segmented",
    "toggle group",
    "options",
    "choice"
  ],
  "usage": {
    "description": "A segmented button lets the user pick from a few options set side by side. Single-select picks one. Multi-select picks some. Put the buttons in a SingleChoiceSegmentedButtonRow or a MultiChoiceSegmentedButtonRow.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Keep multi-select to two to five options."
      },
      {
        "guidance": true,
        "description": "Set each button's shape with SegmentedButtonDefaults.itemShape(index, count)."
      },
      {
        "guidance": false,
        "description": "Use it for more than five options or complex choices. Use chips."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each segment only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      },
      {
        "name": "State is read out",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "role and state",
        "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its fill. The colours come from the tokens, never typed in."
      }
    ],
    "anatomy": [
      {
        "name": "Row",
        "required": true,
        "description": "The single or multi choice row that holds the buttons."
      },
      {
        "name": "Segment",
        "required": true,
        "description": "One option."
      },
      {
        "name": "Check icon",
        "required": false,
        "description": "Shows a picked option."
      }
    ]
  },
  "props": [
    {
      "name": "selected",
      "type": "boolean",
      "description": "Single choice: true when this option is picked.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "() => void",
      "description": "Single choice: runs when the user picks this option.",
      "required": true
    },
    {
      "name": "shape",
      "type": "Shape",
      "description": "Where the segment sits in the row. Use SegmentedButtonDefaults.itemShape(index, count).",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "label",
      "type": "@Composable () -> Unit",
      "description": "The words for the option.",
      "required": true
    }
  ]
};
