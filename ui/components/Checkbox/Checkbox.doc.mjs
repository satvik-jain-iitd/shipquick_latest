/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/checkbox (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Checkbox",
  "displayName": "Checkbox",
  "platforms": {
    "android": "androidx.compose.material3.Checkbox",
    "ios": null,
    "web": "@astryxdesign/core/CheckboxInput"
  },
  "platformUsage": {
    "android": {
      "description": "It is unselected, selected or indeterminate (TriStateCheckbox).",
      "accessibility": [
        {
          "name": "State is read out",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "role and state",
          "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on the checkbox only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    }
  },
  "group": "Checkbox",
  "category": "Form Controls",
  "keywords": [
    "checkbox",
    "check",
    "tick",
    "agree",
    "multi select"
  ],
  "usage": {
    "description": "A checkbox lets the user pick one or more items from a list, turn an item on or off, or agree to terms.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use checkboxes when the user can pick more than one option."
      },
      {
        "guidance": true,
        "description": "Put the label next to the box."
      },
      {
        "guidance": false,
        "description": "Use a checkbox for one pick from many. Use radio buttons."
      }
    ],
    "accessibility": [
      {
        "name": "Shape contrast",
        "category": "Color contrast",
        "criterion": "1.4.11 Non-text Contrast",
        "requirement": "3:1",
        "description": "The edge or the mark that shows state has at least 3:1 contrast with what is behind it."
      }
    ],
    "anatomy": [
      {
        "name": "Box",
        "required": true,
        "description": "The container."
      },
      {
        "name": "Check",
        "required": true,
        "description": "Shows the state."
      },
      {
        "name": "Label",
        "required": true,
        "description": "The words for the option."
      }
    ]
  },
  "props": [
    {
      "name": "checked",
      "type": "boolean",
      "description": "True when the box is ticked.",
      "required": true
    },
    {
      "name": "onCheckedChange",
      "type": "((checked: boolean) => void) | null",
      "description": "Runs with the new value when the user taps. Pass null when the whole row handles the tap.",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "TriStateCheckbox",
          "note": "A checkbox with three states: On, Off and Indeterminate (a ToggleableState). Use it for a parent box that checks or clears a group."
        }
      ],
      "supporting": [
        {
          "name": "CheckboxDefaults",
          "use": "Default colours and stroke width for checkboxes. Make colours with CheckboxDefaults.colors()."
        },
        {
          "name": "CheckboxColors",
          "use": "The box, border and check mark colours of a checkbox in each state."
        }
      ]
    }
  }
};
