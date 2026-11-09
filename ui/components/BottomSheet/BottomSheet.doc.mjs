/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/bottom-sheets (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "BottomSheet",
  "displayName": "Bottom sheet",
  "platforms": {
    "android": "androidx.compose.material3.ModalBottomSheet",
    "ios": "SwiftUI.View.sheet(isPresented:onDismiss:content:)",
    "web": "@astryxdesign/core/BottomSheet"
  },
  "group": "Sheet",
  "category": "Overlay",
  "keywords": [
    "bottom sheet",
    "sheet",
    "modal",
    "drawer"
  ],
  "usage": {
    "description": "A modal bottom sheet slides up from the bottom over the screen, with more content or actions. Its content is laid out in a column. SheetState opens and closes it from code.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Create the state with rememberModalBottomSheetState and pass it as sheetState."
      },
      {
        "guidance": true,
        "description": "Take the sheet out of the composition after it hides."
      },
      {
        "guidance": false,
        "description": "Build your own sliding panel. Use ModalBottomSheet."
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
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its fill. The colours come from the tokens, never typed in."
      }
    ],
    "anatomy": [
      {
        "name": "Scrim",
        "required": true,
        "description": "Dims the screen behind."
      },
      {
        "name": "Sheet",
        "required": true,
        "description": "The surface."
      },
      {
        "name": "Drag handle",
        "required": false,
        "description": "The small bar to drag it."
      }
    ]
  },
  "props": [
    {
      "name": "onDismissRequest",
      "type": "() => void",
      "description": "Runs when the user closes the sheet: a tap outside, a swipe down or Back.",
      "required": true
    },
    {
      "name": "sheetState",
      "type": "SheetState",
      "description": "Opens and closes the sheet. Create it with rememberModalBottomSheetState().",
      "default": "rememberModalBottomSheetState()"
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "What the sheet holds, in a column.",
      "required": true
    }
  ]
};
