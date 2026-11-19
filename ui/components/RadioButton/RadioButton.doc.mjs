/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/radio-button (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "RadioButton",
  "displayName": "Radio button",
  "platforms": {
    "android": "androidx.compose.material3.RadioButton",
    "ios": null,
    "web": null
  },
  "group": "Radio",
  "category": "Form Controls",
  "keywords": [
    "radio",
    "option",
    "single select",
    "choice"
  ],
  "usage": {
    "description": "A radio button lets the user pick one option from a set. Put each RadioButton and its label in a Row.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use radio buttons when only one item can be picked."
      },
      {
        "guidance": true,
        "description": "Make the whole row selectable and pass onClick = null to the RadioButton."
      },
      {
        "guidance": false,
        "description": "Use radio buttons when the user can pick more than one. Use checkboxes."
      }
    ],
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
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on the row only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Circle",
        "required": true,
        "description": "The mark."
      },
      {
        "name": "Dot",
        "required": true,
        "description": "Shows the pick."
      },
      {
        "name": "Label",
        "required": true,
        "description": "The words."
      }
    ]
  },
  "props": [
    {
      "name": "selected",
      "type": "boolean",
      "description": "True when this option is picked.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "(() => void) | null",
      "description": "Runs when the user taps. When null, the user cannot tap the button itself; the row handles it.",
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
      "supporting": [
        {
          "name": "RadioButtonDefaults",
          "use": "Default colours for radio buttons. Make them with RadioButtonDefaults.colors()."
        },
        {
          "name": "RadioButtonColors",
          "use": "The colours of a radio button, selected and not, on and off."
        }
      ]
    }
  }
};
