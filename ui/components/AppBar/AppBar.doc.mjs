/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/app-bars (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "AppBar",
  "displayName": "App bar",
  "platforms": {
    "android": "androidx.compose.material3.TopAppBar",
    "ios": "SwiftUI.View.toolbar(content:)",
    "web": null
  },
  "group": "App bar",
  "category": "Navigation",
  "keywords": [
    "app bar",
    "toolbar",
    "header",
    "top bar",
    "bottom bar"
  ],
  "usage": {
    "description": "An app bar gives access to key tasks and navigation. A top app bar has the title, main actions and navigation. A bottom app bar has core navigation or actions. Pass app bars to Scaffold.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Pass the bar to Scaffold's topBar or bottomBar."
      },
      {
        "guidance": true,
        "description": "Use a scrollBehavior to shrink the bar as the content scrolls."
      },
      {
        "guidance": false,
        "description": "Put more than a few actions in the bar. Move the rest to a menu."
      }
    ],
    "accessibility": [
      {
        "name": "Icon name",
        "category": "Semantics",
        "criterion": "1.1.1 Non-text Content",
        "requirement": "contentDescription",
        "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
      },
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each action only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Navigation icon",
        "required": false,
        "description": "Back or menu."
      },
      {
        "name": "Title",
        "required": true,
        "description": "The screen name."
      },
      {
        "name": "Actions",
        "required": false,
        "description": "Icon buttons at the end."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "@Composable () -> Unit",
      "description": "The screen name.",
      "required": true
    },
    {
      "name": "navigationIcon",
      "type": "@Composable () -> Unit",
      "description": "Back or menu, at the start."
    },
    {
      "name": "actions",
      "type": "@Composable RowScope.() -> Unit",
      "description": "Icon buttons at the end."
    },
    {
      "name": "scrollBehavior",
      "type": "TopAppBarScrollBehavior",
      "description": "How the bar reacts when the content scrolls.",
      "default": "null"
    }
  ]
};
