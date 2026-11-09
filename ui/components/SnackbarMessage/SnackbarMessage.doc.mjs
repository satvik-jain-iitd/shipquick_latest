/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SnackbarMessage",
  "displayName": "Snackbar (the message)",
  "platforms": {
    "android": "androidx.compose.material3.Snackbar",
    "ios": null,
    "web": null
  },
  "group": "Snackbar",
  "category": "Feedback & Status",
  "keywords": [
    "snackbar",
    "message",
    "toast"
  ],
  "usage": {
    "description": "Snackbar is the message itself: a short line with an optional action and close button. SnackbarHost shows it for you. Call it directly only to change how the host draws each one.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Show it through SnackbarHostState.showSnackbar()."
      },
      {
        "guidance": false,
        "description": "Put more than one action in it."
      }
    ],
    "accessibility": [
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its container."
      }
    ]
  },
  "props": [
    {
      "name": "snackbarData",
      "type": "SnackbarData",
      "description": "The message the host gives you to draw.",
      "required": true
    },
    {
      "name": "actionOnNewLine",
      "type": "boolean",
      "description": "Puts the action under the message, for long text.",
      "default": "false"
    }
  ],
  "platformApi": {
    "android": {
      "supporting": [
        {
          "name": "SnackbarData",
          "use": "The snackbar on show: its visuals, and performAction() and dismiss()."
        },
        {
          "name": "SnackbarVisuals",
          "use": "What a snackbar says: message, actionLabel, withDismissAction and duration."
        },
        {
          "name": "SnackbarDuration",
          "use": "How long a snackbar stays: Short, Long or Indefinite (until the user acts or it is dismissed)."
        },
        {
          "name": "SnackbarResult",
          "use": "What the user did: ActionPerformed or Dismissed."
        },
        {
          "name": "SnackbarDefaults",
          "use": "Default colours and shape for snackbars."
        }
      ]
    }
  }
};
