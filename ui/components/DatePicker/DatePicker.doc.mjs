/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/datepickers (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "DatePicker",
  "displayName": "Date picker",
  "platforms": {
    "android": "androidx.compose.material3.DatePicker",
    "ios": null,
    "web": null
  },
  "group": "Picker",
  "category": "Data Input",
  "keywords": [
    "date",
    "calendar",
    "picker",
    "range"
  ],
  "usage": {
    "description": "A date picker lets the user pick a date, a range, or both, from a calendar or by typing. Docked sits in the layout. Modal shows in DatePickerDialog. DateRangePicker picks a start and an end.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Create the state with rememberDatePickerState and read selectedDateMillis."
      },
      {
        "guidance": true,
        "description": "Use DatePickerDialog for a modal picker."
      },
      {
        "guidance": false,
        "description": "Build a calendar grid by hand."
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
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on each day only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      }
    ],
    "anatomy": [
      {
        "name": "Headline",
        "required": true,
        "description": "The picked date."
      },
      {
        "name": "Mode toggle",
        "required": false,
        "description": "Calendar or text input."
      },
      {
        "name": "Calendar",
        "required": true,
        "description": "The month grid."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "DatePickerState",
      "description": "The picked date and the shown month. Create it with rememberDatePickerState().",
      "required": true
    },
    {
      "name": "title",
      "type": "@Composable () -> Unit",
      "description": "The words at the top."
    },
    {
      "name": "headline",
      "type": "@Composable () -> Unit",
      "description": "Shows the picked date."
    },
    {
      "name": "showModeToggle",
      "type": "boolean",
      "description": "Shows the switch between calendar and text input.",
      "default": "true"
    }
  ]
};
