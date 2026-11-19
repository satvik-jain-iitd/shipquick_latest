/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "BottomSheetScaffold",
  "displayName": "Bottom sheet scaffold",
  "platforms": {
    "android": "androidx.compose.material3.BottomSheetScaffold",
    "ios": null,
    "web": null
  },
  "group": "BottomSheet",
  "category": "Layout",
  "keywords": [
    "bottom sheet",
    "standard sheet",
    "scaffold"
  ],
  "usage": {
    "description": "BottomSheetScaffold is a screen layout with a standard bottom sheet. The sheet stays on screen beside the content, partly or fully open, like a map with a list.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Set sheetPeekHeight so the user sees the sheet is there."
      },
      {
        "guidance": false,
        "description": "Use it for a sheet that blocks the screen. Use ModalBottomSheet."
      }
    ],
    "accessibility": [
      {
        "name": "Reading order",
        "category": "Keyboard",
        "criterion": "1.3.2 Meaningful Sequence",
        "requirement": "order on screen",
        "description": "TalkBack reads the parts in the order they show on screen."
      }
    ]
  },
  "props": [
    {
      "name": "sheetContent",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "What is in the sheet.",
      "required": true
    },
    {
      "name": "scaffoldState",
      "type": "BottomSheetScaffoldState",
      "description": "The sheet and snackbar state. Make it with rememberBottomSheetScaffoldState()."
    },
    {
      "name": "sheetPeekHeight",
      "type": "Dp",
      "description": "How much of the sheet shows when it is partly open."
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
      "supporting": [
        {
          "name": "BottomSheetScaffoldState",
          "use": "Holds the sheet state and the snackbar host state of a BottomSheetScaffold."
        },
        {
          "name": "rememberBottomSheetScaffoldState",
          "use": "Creates and keeps a BottomSheetScaffoldState across recompositions."
        }
      ]
    }
  }
};
