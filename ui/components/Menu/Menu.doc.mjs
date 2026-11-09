/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/menu (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Menu",
  "displayName": "Menu",
  "platforms": {
    "android": "androidx.compose.material3.DropdownMenu",
    "ios": "SwiftUI.Menu",
    "web": "@astryxdesign/core/DropdownMenu"
  },
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Open it from an IconButton and set expanded from your state."
        },
        {
          "guidance": true,
          "description": "Close it in onDismissRequest."
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
      ]
    },
    "ios": {
      "description": "On iOS, Menu is a button that opens a list of actions. Apple: \"A control for presenting a menu of actions.\"",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Start each item with a clear verb, like \"Rename\" (Apple HIG, Menus)."
        },
        {
          "guidance": true,
          "description": "List the most used items first. Give a delete item role: .destructive."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "The menu's label is its spoken name. Give an icon a name with Label(\"More\", systemImage: \"ellipsis.circle\")."
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
        "guidance": false,
        "description": "Put the main action of the screen only in a menu."
      }
    ],
    "accessibility": [],
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
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "The words on the button that opens the menu.",
      "platform": "ios"
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "The Buttons in the menu.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "label",
      "type": "() -> some View",
      "description": "A custom label, like a Label with an icon.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "MenuButton", "note": "not on iOS. Apple: \"A button that displays a menu containing a list of choices when pressed.\"", "status": "unavailable-ios", "replacement": "Menu"},
        {"name": "menuStyle", "note": "`.menuStyle(_:)`, iOS 14.0. Apple: \"Sets the style for menus within this view.\""}
      ],
      "supporting": [
        {"name": "MenuStyleConfiguration.Content", "use": "iOS 14.0. Apple: \"A type-erased content of a menu.\""},
        {"name": "MenuStyleConfiguration.Label", "use": "iOS 14.0. Apple: \"A type-erased label of a menu.\""}
      ]
    }
  }
};
