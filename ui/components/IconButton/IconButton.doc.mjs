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
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use FilledIconButton, FilledTonalIconButton or OutlinedIconButton for a stronger look."
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
      ]
    }
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
        "guidance": false,
        "description": "Use an icon nobody knows. Use a button with words instead."
      }
    ],
    "accessibility": [],
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
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "FilledIconButton",
          "note": "An icon button with a filled container. The strongest look."
        },
        {
          "name": "FilledTonalIconButton",
          "note": "An icon button with a tonal container. Between filled and outlined."
        },
        {
          "name": "OutlinedIconButton",
          "note": "An icon button with a border. Medium strength."
        },
        {
          "name": "IconToggleButton",
          "note": "A standard icon button that is checked or not. Pass checked and onCheckedChange. Use it for an on and off action, like Favourite."
        },
        {
          "name": "FilledIconToggleButton",
          "note": "A filled icon button that is checked or not. Pass checked and onCheckedChange."
        },
        {
          "name": "FilledTonalIconToggleButton",
          "note": "A tonal icon button that is checked or not. Pass checked and onCheckedChange."
        },
        {
          "name": "OutlinedIconToggleButton",
          "note": "An outlined icon button that is checked or not. Pass checked and onCheckedChange."
        }
      ],
      "supporting": [
        {
          "name": "IconButtonDefaults",
          "use": "The default colours, shapes and sizes for every icon button type."
        },
        {
          "name": "IconButtonColors",
          "use": "The colours of an icon button when it is on or off. Make one with IconButtonDefaults.iconButtonColors() or the colour function of its type."
        },
        {
          "name": "IconToggleButtonColors",
          "use": "The colours of an icon toggle button, checked and not checked. Make one with IconButtonDefaults.iconToggleButtonColors() or the colour function of its type."
        }
      ]
    }
  }
};
