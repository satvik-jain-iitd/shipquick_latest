/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/scaffold (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Scaffold",
  "displayName": "Scaffold",
  "platforms": {
    "android": "androidx.compose.material3.Scaffold",
    "ios": null,
    "web": null
  },
  "group": "Layout",
  "category": "Layout",
  "keywords": [
    "scaffold",
    "screen",
    "layout",
    "shell",
    "structure"
  ],
  "usage": {
    "description": "Scaffold is the frame of a screen. It holds the top app bar, the bottom bar, the floating action button and the snackbar host in their right places.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Start every screen with Scaffold."
      },
      {
        "guidance": true,
        "description": "Apply the PaddingValues it gives to the content's root."
      },
      {
        "guidance": false,
        "description": "Place app bars or the FAB by hand."
      }
    ],
    "accessibility": [
      {
        "name": "Order",
        "category": "Keyboard",
        "criterion": "2.4.3 Focus Order",
        "requirement": "top bar, content, bottom bar",
        "description": "Scaffold keeps the reading order: top bar, then content, then the bottom bar."
      }
    ],
    "anatomy": [
      {
        "name": "Top bar",
        "required": false,
        "description": "The top app bar."
      },
      {
        "name": "Content",
        "required": true,
        "description": "The screen body."
      },
      {
        "name": "Bottom bar",
        "required": false,
        "description": "A bottom app bar or a navigation bar."
      },
      {
        "name": "FAB",
        "required": false,
        "description": "The floating action button."
      }
    ]
  },
  "props": [
    {
      "name": "topBar",
      "type": "@Composable () -> Unit",
      "description": "The top app bar."
    },
    {
      "name": "bottomBar",
      "type": "@Composable () -> Unit",
      "description": "The bottom app bar or navigation bar."
    },
    {
      "name": "snackbarHost",
      "type": "@Composable () -> Unit",
      "description": "Where snackbars show, usually SnackbarHost."
    },
    {
      "name": "floatingActionButton",
      "type": "@Composable () -> Unit",
      "description": "The FAB."
    },
    {
      "name": "floatingActionButtonPosition",
      "type": "'Start' | 'Center' | 'End' | 'EndOverlay'",
      "description": "Where the FAB sits.",
      "default": "'End'"
    },
    {
      "name": "content",
      "type": "@Composable (PaddingValues) -> Unit",
      "description": "The screen body. Apply the padding it gets.",
      "required": true
    }
  ]
};
