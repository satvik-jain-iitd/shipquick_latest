/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/snackbar (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Snackbar",
  "displayName": "Snackbar",
  "platforms": {
    "android": "androidx.compose.material3.SnackbarHost",
    "ios": null,
    "web": "@astryxdesign/core/Toast"
  },
  "group": "Snackbar",
  "category": "Feedback & Status",
  "keywords": [
    "snackbar",
    "toast",
    "message",
    "undo",
    "notice"
  ],
  "usage": {
    "description": "A snackbar is a short message at the bottom of the screen, like \"Message deleted\" with Undo. It does not stop the user. Put a SnackbarHost in Scaffold's snackbarHost slot and call SnackbarHostState.showSnackbar from a coroutine.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it to confirm an action, show that the app is offline, or say a change saved."
      },
      {
        "guidance": true,
        "description": "Offer one short action, like Undo."
      },
      {
        "guidance": false,
        "description": "Put the only way to do a task in a snackbar. It goes away."
      }
    ],
    "accessibility": [
      {
        "name": "Time to act",
        "category": "Content",
        "criterion": "2.2.1 Timing Adjustable",
        "requirement": "Indefinite with an action",
        "description": "With an action, showSnackbar stays until the user acts (Google's default duration is Indefinite then). Keep that default."
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
        "name": "Container",
        "required": true,
        "description": "The bar at the bottom."
      },
      {
        "name": "Message",
        "required": true,
        "description": "The words."
      },
      {
        "name": "Action",
        "required": false,
        "description": "One text button."
      },
      {
        "name": "Close",
        "required": false,
        "description": "The dismiss icon."
      }
    ]
  },
  "props": [
    {
      "name": "hostState",
      "type": "SnackbarHostState",
      "description": "The state that shows the snackbars. Create it with remember { SnackbarHostState() }.",
      "required": true
    },
    {
      "name": "message",
      "type": "string",
      "description": "The words to show.",
      "required": true
    },
    {
      "name": "actionLabel",
      "type": "string",
      "description": "The words on the one action button. Leave it out for no action."
    },
    {
      "name": "withDismissAction",
      "type": "boolean",
      "description": "Shows a close icon.",
      "default": "false"
    },
    {
      "name": "duration",
      "type": "'Short' | 'Long' | 'Indefinite'",
      "description": "How long it stays.",
      "default": "'Short', or 'Indefinite' with an action"
    }
  ]
};
