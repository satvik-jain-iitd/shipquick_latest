/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/fab (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "FloatingActionButton",
  "displayName": "Floating action button",
  "platforms": {
    "android": "androidx.compose.material3.FloatingActionButton",
    "ios": null,
    "web": null
  },
  "group": "Button",
  "category": "Action",
  "keywords": [
    "fab",
    "floating",
    "action",
    "create",
    "add"
  ],
  "usage": {
    "description": "A floating action button (FAB) is a high-emphasis button for the one main action on a screen, like a new note. It sits at the bottom right. Small, large and extended (icon plus words) FABs exist too.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use one FAB for the most common action on the screen."
      },
      {
        "guidance": true,
        "description": "Pass it to Scaffold's floatingActionButton slot, so it sits in the right place."
      },
      {
        "guidance": false,
        "description": "Use a FAB for a small or rare action. Use a button or an icon button."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on the FAB only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
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
        "description": "The raised shape."
      },
      {
        "name": "Icon",
        "required": true,
        "description": "Shows the action."
      },
      {
        "name": "Label",
        "required": false,
        "description": "Words, on the extended FAB only."
      }
    ]
  },
  "props": [
    {
      "name": "onClick",
      "type": "() => void",
      "description": "Runs when the user presses the FAB.",
      "required": true
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
          "name": "SmallFloatingActionButton",
          "note": "A smaller FAB. Use it for a second action, or next to other parts."
        },
        {
          "name": "LargeFloatingActionButton",
          "note": "A bigger FAB. Use it when the screen has room and the action is the main one."
        },
        {
          "name": "ExtendedFloatingActionButton",
          "note": "A wider FAB with a text label and an optional icon. Use it when words make the action clearer. Its expanded flag shrinks it to the icon, for example while a list scrolls."
        }
      ],
      "supporting": [
        {
          "name": "FloatingActionButtonDefaults",
          "use": "The default colour, shapes and elevation for every FAB size."
        },
        {
          "name": "FloatingActionButtonElevation",
          "use": "The shadow of a FAB in each state. Make one with FloatingActionButtonDefaults.elevation() or loweredElevation()."
        },
        {
          "name": "FabPosition",
          "use": "Where Scaffold puts the FAB: Start, Center, End or EndOverlay. Pass it as floatingActionButtonPosition."
        }
      ]
    }
  }
};
