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
  ],
  "platformApi": {
    "android": {
      "family": "DragHandle",
      "variants": [
        {
          "name": "VerticalDragHandle",
          "note": "A tall handle between two panes. The user drags it to change the pane widths, on large screens."
        },
        {
          "name": "ProvideTextStyle",
          "note": "Sets the text style for all Text inside it. Parts like buttons and app bars use it for their labels."
        }
      ],
      "supporting": [
        {
          "name": "ScaffoldDefaults",
          "use": "The default contentWindowInsets of Scaffold."
        },
        {
          "name": "VerticalDragHandleDefaults",
          "use": "Default colours, shapes and sizes for VerticalDragHandle."
        },
        {
          "name": "DragHandleColors",
          "use": "The colours of a drag handle when it rests, is pressed and is dragged."
        },
        {
          "name": "DragHandleShapes",
          "use": "The shape of a drag handle when it rests, is pressed and is dragged."
        },
        {
          "name": "DragHandleSizes",
          "use": "The size of a drag handle when it rests, is pressed and is dragged."
        },
        {
          "name": "MaterialTheme",
          "use": "Reads the current theme inside any composable: MaterialTheme.colorScheme, MaterialTheme.typography and MaterialTheme.shapes."
        },
        {
          "name": "ColorScheme",
          "use": "The named colour roles of the theme, like primary and onPrimary. Make one with lightColorScheme() or darkColorScheme(), or dynamicLightColorScheme() and dynamicDarkColorScheme() on Android 12 and later."
        },
        {
          "name": "contentColorFor",
          "use": "Gives the matching content colour for a background colour of the scheme, like onPrimary for primary."
        },
        {
          "name": "Typography",
          "use": "The type scale of the theme: display, headline, title, body and label, each in large, medium and small."
        },
        {
          "name": "Shapes",
          "use": "The shape scale of the theme: extraSmall, small, medium, large and extraLarge."
        },
        {
          "name": "ShapeDefaults",
          "use": "The default value of each shape in the scale."
        },
        {
          "name": "RippleDefaults",
          "use": "The default ripple alpha values."
        },
        {
          "name": "RippleConfiguration",
          "use": "Changes the ripple colour or alpha for one part of the screen, set through LocalRippleConfiguration. Use it only when the default ripple cannot be seen."
        },
        {
          "name": "ExperimentalMaterial3Api",
          "use": "Marks M3 API that may still change. Opt in with @OptIn(ExperimentalMaterial3Api::class) where you call it; experimental rows are marked in docs/research/android-m3-api.md."
        }
      ]
    }
  }
};
