/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "DatePickerDialog",
  "displayName": "Date picker dialog",
  "platforms": {
    "android": "androidx.compose.material3.DatePickerDialog",
    "ios": null,
    "web": null
  },
  "group": "DatePicker",
  "category": "Overlay",
  "keywords": [
    "date",
    "picker",
    "dialog",
    "calendar"
  ],
  "usage": {
    "description": "DatePickerDialog holds a DatePicker in a dialog, with confirm and dismiss buttons. Use it when the user picks a date from a form.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Read the date from the DatePickerState when the user confirms."
      },
      {
        "guidance": false,
        "description": "Save the date before the user confirms."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "the feel.touchTarget token",
        "description": "Each control in it is at least the feel.touchTarget token in design/tokens.json."
      }
    ]
  },
  "props": [
    {
      "name": "onDismissRequest",
      "type": "() -> Unit",
      "description": "Runs when the user taps outside or presses Back.",
      "required": true
    },
    {
      "name": "confirmButton",
      "type": "@Composable () -> Unit",
      "description": "The OK button.",
      "required": true
    },
    {
      "name": "dismissButton",
      "type": "@Composable () -> Unit",
      "description": "The Cancel button."
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "The DatePicker.",
      "required": true
    }
  ]
};
