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
  ]
};
