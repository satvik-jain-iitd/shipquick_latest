/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/icon-button (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "IconButton",
  "displayName": "Icon button",
  "platforms": {
    "android": "androidx.compose.material3.IconButton",
    "ios": null,
    "web": "@astryxdesign/core/IconButton"
  },
  "group": "Button",
  "category": "Action",
  "keywords": [
    "icon",
    "button",
    "toggle",
    "favorite"
  ],
  "usage": {
    "description": "An icon button is an action shown as one icon. Use it for common actions, like open a menu or search. A toggle icon button turns something on or off, like favorite.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use an icon whose meaning is clear on its own."
      },
      {
        "guidance": true,
        "description": "Use FilledIconButton, FilledTonalIconButton or OutlinedIconButton for a stronger look."
      },
      {
        "guidance": false,
        "description": "Use an icon nobody knows. Use a button with words instead."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on the icon button only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      },
      {
        "name": "Icon name",
        "category": "Semantics",
        "criterion": "1.1.1 Non-text Content",
        "requirement": "contentDescription",
        "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
      }
    ],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "The pressable area, at least 48dp."
      },
      {
        "name": "Icon",
        "required": true,
        "description": "The picture of the action."
      }
    ]
  },
  "props": [
    {
      "name": "onClick",
      "type": "() => void",
      "description": "Runs when the user taps the icon button.",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The inside, usually one Icon.",
      "required": true
    }
  ]
};
