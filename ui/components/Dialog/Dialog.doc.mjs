/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/dialog (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Dialog",
  "displayName": "Dialog",
  "platforms": {
    "android": "androidx.compose.material3.AlertDialog",
    "ios": "SwiftUI.View.alert(_:isPresented:actions:)",
    "web": "@astryxdesign/core/AlertDialog"
  },
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Give a dismiss button and handle onDismissRequest."
        },
        {
          "guidance": false,
          "description": "Use a dialog for news that does not need an answer. Use a snackbar."
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
      "description": "On iOS the twin is an alert: alert(_:isPresented:actions:message:). Apple: \"Presents an alert with a message when a given condition is true.\"",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Give each button a role: .cancel for the safe choice, .destructive for a delete."
        },
        {
          "guidance": true,
          "description": "Keep the title a short question, and put the detail in message."
        },
        {
          "guidance": false,
          "description": "Use an alert only to give news. Apple: use alerts sparingly, and not for actions that can be undone."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "VoiceOver moves into the alert when it opens and reads the title first. Focus goes back when it closes."
        }
      ]
    }
  },
  "group": "Dialog",
  "category": "Overlay",
  "keywords": [
    "dialog",
    "alert",
    "confirm",
    "modal",
    "popup"
  ],
  "usage": {
    "description": "A dialog shows a message or asks for input on a layer above the app. It stops the user on purpose. Use it to confirm an action, like deleting a file, or to ask a short question.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Say the choice in the title and the buttons, like \"Delete file?\" with Delete and Cancel."
      }
    ],
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
        "name": "Icon",
        "required": false,
        "description": "At the top."
      },
      {
        "name": "Title",
        "required": false,
        "description": "The question."
      },
      {
        "name": "Text",
        "required": false,
        "description": "More detail."
      },
      {
        "name": "Buttons",
        "required": true,
        "description": "Confirm, and often dismiss."
      }
    ]
  },
  "props": [
    {
      "name": "onDismissRequest",
      "type": "() => void",
      "description": "Runs when the user closes the dialog: a tap outside or Back.",
      "required": true
    },
    {
      "name": "confirmButton",
      "type": "@Composable () -> Unit",
      "description": "The button that says yes, usually a TextButton.",
      "required": true
    },
    {
      "name": "dismissButton",
      "type": "@Composable () -> Unit",
      "description": "The button that says no."
    },
    {
      "name": "icon",
      "type": "@Composable () -> Unit",
      "description": "A picture at the top."
    },
    {
      "name": "title",
      "type": "@Composable () -> Unit",
      "description": "The words along the top."
    },
    {
      "name": "text",
      "type": "@Composable () -> Unit",
      "description": "The main words."
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "The question along the top.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "isPresented",
      "type": "Binding<Bool>",
      "description": "Shows the alert while true.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "actions",
      "type": "() -> some View",
      "description": "The buttons, each with a role.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "message",
      "type": "() -> some View",
      "description": "The detail under the title.",
      "platform": "ios"
    }
  ]
};
