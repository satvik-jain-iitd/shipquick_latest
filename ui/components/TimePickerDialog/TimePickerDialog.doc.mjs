/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "TimePickerDialog",
  "displayName": "Time picker dialog",
  "platforms": {
    "android": "androidx.compose.material3.TimePickerDialog",
    "ios": null,
    "web": null
  },
  "group": "TimePicker",
  "category": "Overlay",
  "keywords": [
    "time",
    "picker",
    "dialog",
    "clock"
  ],
  "usage": {
    "description": "TimePickerDialog holds a TimePicker or TimeInput in a dialog, with a title, confirm and dismiss buttons and an optional mode toggle.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Add the mode toggle so the user can type the time."
      },
      {
        "guidance": false,
        "description": "Save the time before the user confirms."
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
      "name": "title",
      "type": "@Composable () -> Unit",
      "description": "The title. TimePickerDialogDefaults.Title is the default.",
      "required": true
    },
    {
      "name": "modeToggleButton",
      "type": "@Composable () -> Unit",
      "description": "The button that switches between the dial and text input."
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "The TimePicker or TimeInput.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "TimePickerDialogDefaults.Title",
          "note": "The default title of a TimePickerDialog. It changes with the display mode."
        },
        {
          "name": "TimePickerDialogDefaults.DisplayModeToggle",
          "note": "The default button that switches a TimePickerDialog between the dial and the input fields."
        }
      ],
      "supporting": [
        {
          "name": "TimePickerDialogDefaults",
          "use": "The default title, mode toggle, container colour, shape and minimum height for TimePickerDialog."
        }
      ]
    }
  }
};
