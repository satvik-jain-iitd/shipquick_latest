/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SecureTextField",
  "displayName": "Secure text field",
  "platforms": {
    "android": "androidx.compose.material3.SecureTextField",
    "ios": null,
    "web": null
  },
  "group": "TextField",
  "category": "Form Controls",
  "keywords": [
    "password",
    "secure",
    "text field",
    "input"
  ],
  "usage": {
    "description": "SecureTextField is a filled text field for a password. It hides what the user types.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Add a trailing icon button to show and hide the password."
      },
      {
        "guidance": false,
        "description": "Use a plain TextField for a password."
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
        "description": "The field has a label that stays in view."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "TextFieldState",
      "description": "Holds the text.",
      "required": true
    },
    {
      "name": "label",
      "type": "@Composable TextFieldLabelScope.() -> Unit",
      "description": "The label."
    },
    {
      "name": "textObfuscationMode",
      "type": "'RevealLastTyped' | 'Hidden' | 'Visible'",
      "description": "How the text is hidden.",
      "default": "'RevealLastTyped'"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "OutlinedSecureTextField",
          "note": "The outlined form of SecureTextField."
        }
      ]
    }
  }
};
