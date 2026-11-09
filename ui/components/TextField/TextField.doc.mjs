/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/text/user-input (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "TextField",
  "displayName": "Text field",
  "platforms": {
    "android": "androidx.compose.material3.TextField",
    "ios": "SwiftUI.TextField",
    "web": "@astryxdesign/core/TextInput"
  },
  "group": "Text field",
  "category": "Data Input",
  "keywords": [
    "text field",
    "input",
    "form",
    "password",
    "email"
  ],
  "usage": {
    "description": "A text field lets the user type and change text. TextField is filled. OutlinedTextField has a border. SecureTextField hides a password. Google says the value-based fields are deprecated: use the state-based ones with TextFieldState.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the state-based field: rememberTextFieldState()."
      },
      {
        "guidance": true,
        "description": "Set keyboardOptions, like KeyboardType.Email for an email."
      },
      {
        "guidance": false,
        "description": "Use BasicTextField for a form. It has no label or error styling."
      }
    ],
    "accessibility": [
      {
        "name": "Label",
        "category": "Content",
        "criterion": "3.3.2 Labels or Instructions",
        "requirement": "visible label",
        "description": "Every input has words that say what to enter. A placeholder alone is not a label."
      },
      {
        "name": "Errors",
        "category": "Content",
        "criterion": "3.3.1 Error Identification",
        "requirement": "words, not colour only",
        "description": "Set isError and put the reason in supportingText, so the error is said in words."
      }
    ],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "Filled or outlined."
      },
      {
        "name": "Label",
        "required": true,
        "description": "Says what to type."
      },
      {
        "name": "Input",
        "required": true,
        "description": "The text."
      },
      {
        "name": "Supporting text",
        "required": false,
        "description": "Help or the error."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "TextFieldState",
      "description": "The text. Create it with rememberTextFieldState().",
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
      "type": "@Composable TextFieldLabelScope.() -> Unit",
      "description": "Says what to type."
    },
    {
      "name": "placeholder",
      "type": "@Composable () -> Unit",
      "description": "Hint text while empty."
    },
    {
      "name": "supportingText",
      "type": "@Composable () -> Unit",
      "description": "Help or the error reason below."
    },
    {
      "name": "isError",
      "type": "boolean",
      "description": "Shows the error style.",
      "default": "false"
    },
    {
      "name": "keyboardOptions",
      "type": "KeyboardOptions",
      "description": "The keyboard type and action, like KeyboardType.Email.",
      "default": "KeyboardOptions.Default"
    }
  ]
};
