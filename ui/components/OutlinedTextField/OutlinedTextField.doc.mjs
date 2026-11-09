/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "OutlinedTextField",
  "displayName": "Outlined text field",
  "platforms": {
    "android": "androidx.compose.material3.OutlinedTextField",
    "ios": null,
    "web": null
  },
  "group": "TextField",
  "category": "Form Controls",
  "keywords": [
    "text field",
    "input",
    "outlined",
    "form"
  ],
  "usage": {
    "description": "OutlinedTextField is a text field with a border and no fill. Use it when filled fields look too heavy, for example in a long form.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use one field style on a screen."
      },
      {
        "guidance": true,
        "description": "Give every field a label."
      },
      {
        "guidance": false,
        "description": "Use the placeholder as the only label. It goes away when the user types."
      }
    ],
    "accessibility": [
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its container."
      },
      {
        "name": "Label",
        "category": "Semantics",
        "criterion": "3.3.2 Labels or Instructions",
        "requirement": "a visible label",
        "description": "Each field has a label that stays in view."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "TextFieldState",
      "description": "Holds the text. Other overloads take value and onValueChange.",
      "required": true
    },
    {
      "name": "label",
      "type": "@Composable TextFieldLabelScope.() -> Unit",
      "description": "The label."
    },
    {
      "name": "supportingText",
      "type": "@Composable () -> Unit",
      "description": "Help or error text under the field."
    },
    {
      "name": "isError",
      "type": "boolean",
      "description": "Shows the field in its error colours.",
      "default": "false"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "OutlinedTextFieldDefaults.Container",
          "note": "The default container (border) of an outlined field, for use inside its DecorationBox."
        },
        {
          "name": "OutlinedTextFieldDefaults.DecorationBox",
          "note": "The label, icons and border of an outlined field around a BasicTextField. Use it only when OutlinedTextField cannot do the job."
        },
        {
          "name": "OutlinedTextFieldDefaults.ContainerBox",
          "note": "The old name of the outlined container.",
          "status": "deprecated",
          "replacement": "OutlinedTextFieldDefaults.Container (Google: ReplaceWith names Container in the same object; the message says \"Renamed to TextFieldDefaults.Container\")"
        }
      ],
      "supporting": [
        {
          "name": "OutlinedTextFieldDefaults",
          "use": "Default colours, shape, sizes, padding and the decorator for outlined fields. Make colours with OutlinedTextFieldDefaults.colors()."
        }
      ]
    }
  }
};
