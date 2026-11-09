/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/time-pickers (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "TimePicker",
  "displayName": "Time picker",
  "platforms": {
    "android": "androidx.compose.material3.TimePicker",
    "ios": null,
    "web": null
  },
  "group": "Picker",
  "category": "Data Input",
  "keywords": [
    "time",
    "clock",
    "picker",
    "hour"
  ],
  "usage": {
    "description": "A time picker lets the user pick a time. TimePicker is a dial. TimeInput uses the keyboard. Both take a TimePickerState, and both show in a dialog.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Create the state with rememberTimePickerState and read hour and minute."
      },
      {
        "guidance": true,
        "description": "Show it in a dialog with confirm and dismiss buttons."
      },
      {
        "guidance": false,
        "description": "Build a clock face by hand."
      }
    ],
    "accessibility": [
      {
        "name": "Label",
        "category": "Content",
        "criterion": "3.3.2 Labels or Instructions",
        "requirement": "visible label",
        "description": "Every input has words that say what to enter. A placeholder alone is not a label."
      },
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each number only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Time",
        "required": true,
        "description": "Hour and minute."
      },
      {
        "name": "Dial or fields",
        "required": true,
        "description": "The dial, or the input fields."
      },
      {
        "name": "AM or PM",
        "required": false,
        "description": "On a 12-hour clock."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "TimePickerState",
      "description": "The picked time. Create it with rememberTimePickerState().",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "TimeInput",
          "note": "Picks a time by typing the hour and minute in fields, not on a dial. Use it when space is short or for typing users."
        },
        {
          "name": "TimePickerDialog",
          "note": "A dialog that holds a TimePicker or TimeInput, with a title, confirm and dismiss buttons and an optional mode toggle button."
        },
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
          "name": "TimePickerState",
          "use": "Holds the hour (0 to 23), the minute, is24hour and which part is being picked."
        },
        {
          "name": "rememberTimePickerState",
          "use": "Creates and keeps a TimePickerState, with the first hour and minute and is24Hour."
        },
        {
          "name": "TimePickerDefaults",
          "use": "Default colours and the layout type for time pickers. Make colours with TimePickerDefaults.colors()."
        },
        {
          "name": "TimePickerColors",
          "use": "The dial, selector, period button and time box colours of a time picker."
        },
        {
          "name": "TimePickerDialogDefaults",
          "use": "The default title, mode toggle, container colour, shape and minimum height for TimePickerDialog."
        },
        {
          "name": "TimePickerDisplayMode",
          "use": "How a time picker dialog shows: Picker (a dial) or Input (text fields)."
        },
        {
          "name": "TimePickerLayoutType",
          "use": "How the dial and the time sit: Vertical (time above the dial) or Horizontal (side by side, for landscape)."
        },
        {
          "name": "TimePickerSelectionMode",
          "use": "Which part the user is picking: Hour or Minute."
        }
      ]
    }
  }
};
