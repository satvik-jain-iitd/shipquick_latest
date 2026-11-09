/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/menu (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Menu",
  "displayName": "Menu",
  "platforms": {
    "android": "androidx.compose.material3.DropdownMenu",
    "ios": null,
    "web": "@astryxdesign/core/DropdownMenu"
  },
  "group": "Menu",
  "category": "Overlay",
  "keywords": [
    "menu",
    "dropdown",
    "overflow",
    "more",
    "options"
  ],
  "usage": {
    "description": "A drop-down menu opens from an icon, a text field or another part and shows a list of options on a short-lived surface. It can have dividers and icons.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Open it from an IconButton and set expanded from your state."
      },
      {
        "guidance": true,
        "description": "Close it in onDismissRequest."
      },
      {
        "guidance": false,
        "description": "Put the main action of the screen only in a menu."
      }
    ],
    "accessibility": [
      {
        "name": "Focus",
        "category": "Keyboard",
        "criterion": "2.4.3 Focus Order",
        "requirement": "focus moves in and back",
        "description": "Focus moves into the surface when it opens and back to what opened it when it closes. Back closes it."
      },
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each item only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Anchor",
        "required": true,
        "description": "What opens the menu."
      },
      {
        "name": "Surface",
        "required": true,
        "description": "The menu box."
      },
      {
        "name": "Item",
        "required": true,
        "description": "One option."
      }
    ]
  },
  "props": [
    {
      "name": "expanded",
      "type": "boolean",
      "description": "True when the menu shows.",
      "required": true
    },
    {
      "name": "onDismissRequest",
      "type": "() => void",
      "description": "Runs when the user closes the menu.",
      "required": true
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "The DropdownMenuItems.",
      "required": true
    }
  ]
};
