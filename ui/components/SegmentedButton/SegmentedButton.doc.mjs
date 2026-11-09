/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/segmented-button (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SegmentedButton",
  "displayName": "Segmented button",
  "platforms": {
    "android": "androidx.compose.material3.SegmentedButton",
    "ios": "SwiftUI.SegmentedPickerStyle",
    "web": "@astryxdesign/core/SegmentedControl"
  },
  "platformUsage": {
    "android": {
      "description": "Single-select picks one. Multi-select picks some. Put the buttons in a SingleChoiceSegmentedButtonRow or a MultiChoiceSegmentedButtonRow.",
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
        }
      ]
    },
    "ios": {
      "description": "On iOS the twin is a Picker with .pickerStyle(.segmented). Apple: the style \"presents the options in a segmented control\". It picks one option. Each option gets a tag(_:) with its value.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Bind selection, and tag each option with its value, like Text(\"Day\").tag(Range.day)."
        },
        {
          "guidance": true,
          "description": "Use it for a few closely related choices (Apple HIG, Segmented controls)."
        },
        {
          "guidance": false,
          "description": "Mix actions and choices in one control."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "VoiceOver says each segment's words and which one is selected."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
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
    "description": "A segmented button lets the user pick from a few options set side by side.",
    "bestPractices": [],
    "accessibility": [
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
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "Says what the choice is for. VoiceOver reads it.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "selection",
      "type": "Binding<SelectionValue>",
      "description": "The picked option's tag.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "The options, each with a tag(_:).",
      "platform": "ios",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "SingleChoiceSegmentedButtonRow",
          "note": "The row for single-select. Each SegmentedButton in it takes selected and onClick."
        },
        {
          "name": "MultiChoiceSegmentedButtonRow",
          "note": "The row for multi-select. Each SegmentedButton in it takes checked and onCheckedChange."
        },
        {
          "name": "SegmentedButtonDefaults.ActiveIcon",
          "note": "The check mark a selected segment shows by default."
        },
        {
          "name": "SegmentedButtonDefaults.Icon",
          "note": "The icon slot. It shows the active icon when the segment is on, and the segment's own icon when it is off, with a short animation."
        }
      ],
      "supporting": [
        {
          "name": "SegmentedButtonDefaults",
          "use": "The default colours, border, icon, and itemShape(index, count) for each segment."
        },
        {
          "name": "SegmentedButtonColors",
          "use": "The container, content and border colours, active and inactive, on and off. Make one with SegmentedButtonDefaults.colors()."
        },
        {
          "name": "SingleChoiceSegmentedButtonRowScope",
          "use": "The scope inside SingleChoiceSegmentedButtonRow, where you call SegmentedButton."
        },
        {
          "name": "MultiChoiceSegmentedButtonRowScope",
          "use": "The scope inside MultiChoiceSegmentedButtonRow, where you call SegmentedButton."
        }
      ]
    }
  }
};
