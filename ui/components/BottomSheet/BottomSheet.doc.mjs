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
  "platformUsage": {
    "android": {
      "description": "Its content is laid out in a column. SheetState opens and closes it from code.",
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
        }
      ]
    },
    "ios": {
      "description": "On iOS, show it with sheet(isPresented:onDismiss:content:). Apple: \"Presents a sheet when a binding to a Boolean value that you provide is true.\" presentationDetents(_:) sets its heights.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Drive it from one Bool, passed as a Binding to isPresented."
        },
        {
          "guidance": true,
          "description": "Add presentationDetents([.medium, .large]) for a half-height sheet, and presentationDragIndicator(.visible) to show the handle."
        },
        {
          "guidance": false,
          "description": "Show more than one sheet at a time (Apple HIG, Sheets)."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "VoiceOver moves into the sheet when it opens and back to what opened it when it closes. A swipe down or a Cancel button closes it."
        }
      ]
    }
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
    "description": "A modal bottom sheet slides up from the bottom over the screen, with more content or actions.",
    "bestPractices": [],
    "accessibility": [
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
    },
    {
      "name": "isPresented",
      "type": "Binding<Bool>",
      "description": "Shows the sheet while true. The system sets it to false when the user closes it.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "onDismiss",
      "type": "(() -> Void)?",
      "description": "Runs after the sheet closes.",
      "platform": "ios",
      "default": "nil"
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "What the sheet holds.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "presentationDetents",
      "type": "Set<PresentationDetent>",
      "description": "The heights the sheet can rest at, like .medium and .large.",
      "platform": "ios",
      "default": "[.large]"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "confirmationDialog", "note": "`.confirmationDialog(_:item:titleVisibility:actions:)`, iOS 15.0. Apple: \"Presents a confirmation dialog using data to produce the dialog’s content and a text view for the title.\""},
        {"name": "dismissalConfirmationDialog", "note": "`.dismissalConfirmationDialog(_:shouldPresent:actions:)`, iOS 27.0. Apple: \"Presents a confirmation dialog upon an attempt to dismiss the window for this view.\""},
        {"name": "fullScreenCover", "note": "`.fullScreenCover(isPresented:onDismiss:content:)`, iOS 14.0. Apple: \"Presents a modal view that covers as much of the screen as possible when binding to a Boolean value you provide is true.\""},
        {"name": "interactiveDismissDisabled", "note": "`.interactiveDismissDisabled(_:)`, iOS 15.0. Apple: \"Conditionally prevents interactive dismissal of presentations like popovers, sheets, and inspectors.\""},
        {"name": "presentationBackground", "note": "`.presentationBackground(_:)`, iOS 16.4. Apple: \"Sets the presentation background of the enclosing sheet using a shape style.\""},
        {"name": "presentationBackgroundInteraction", "note": "`.presentationBackgroundInteraction(_:)`, iOS 16.4. Apple: \"Controls whether people can interact with the view behind a presentation.\""},
        {"name": "presentationBreakthroughEffect", "note": "`.presentationBreakthroughEffect(_:)`, not on iOS. Apple: \"Changes the way the enclosing presentation breaks through content occluding it.\"", "status": "unavailable-ios", "replacement": "nothing on iOS ()"},
        {"name": "presentationCompactAdaptation", "note": "`.presentationCompactAdaptation(horizontal:vertical:)`, iOS 16.4. Apple: \"Specifies how to adapt a presentation to horizontally and vertically compact size classes.\""},
        {"name": "presentationContentInteraction", "note": "`.presentationContentInteraction(_:)`, iOS 16.4. Apple: \"Configures the behavior of swipe gestures on a presentation.\""},
        {"name": "presentationCornerRadius", "note": "`.presentationCornerRadius(_:)`, iOS 16.4. Apple: \"Requests that the presentation have a specific corner radius.\""},
        {"name": "presentationDetents", "note": "`.presentationDetents(_:)`, iOS 16.0. Apple: \"Sets the available detents for the enclosing sheet.\""},
        {"name": "presentationDragIndicator", "note": "`.presentationDragIndicator(_:)`, iOS 16.0. Apple: \"Sets the visibility of the drag indicator on top of a sheet.\""},
        {"name": "presentationPlacement", "note": "`.presentationPlacement(_:)`, iOS 27.0. Apple: \"Sets the placement of a presentation within the presenting view.\""},
        {"name": "presentationPreventsAppTermination", "note": "`.presentationPreventsAppTermination(_:)`, not on iOS. Apple: \"Whether a presentation prevents the app from being terminated/quit by the system or app termination menu item.\"", "status": "unavailable-ios", "replacement": "nothing on iOS ()"},
        {"name": "presentationSizing", "note": "`.presentationSizing(_:)`, iOS 18.0. Apple: \"Sets the sizing of the containing presentation.\""},
        {"name": "sheet", "note": "`.sheet(isPresented:onDismiss:content:)`, iOS 13.0. Apple: \"Presents a sheet when a binding to a Boolean value that you provide is true.\""}
      ]
    }
  }
};
