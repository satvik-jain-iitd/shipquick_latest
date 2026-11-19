/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "DateRangePicker",
  "displayName": "Date range picker",
  "platforms": {
    "android": "androidx.compose.material3.DateRangePicker",
    "ios": null,
    "web": null
  },
  "group": "DatePicker",
  "category": "Data Input",
  "keywords": [
    "date",
    "range",
    "picker",
    "calendar",
    "trip"
  ],
  "usage": {
    "description": "DateRangePicker lets the user pick a start date and an end date, like the days of a trip.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Block dates the user cannot pick with SelectableDates."
      },
      {
        "guidance": false,
        "description": "Use two DatePickers for a range."
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
      "name": "state",
      "type": "DateRangePickerState",
      "description": "Holds the chosen dates. Make it with rememberDateRangePickerState().",
      "required": true
    },
    {
      "name": "showModeToggle",
      "type": "boolean",
      "description": "Shows the button that switches between the calendar and text input.",
      "default": "true"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "DateRangePickerDefaults.DateRangePickerTitle",
          "note": "The default title at the top of a DateRangePicker. It changes with the display mode."
        },
        {
          "name": "DateRangePickerDefaults.DateRangePickerHeadline",
          "note": "The default headline that shows the chosen start and end dates."
        }
      ],
      "supporting": [
        {
          "name": "DateRangePickerState",
          "use": "Holds the chosen start and end dates (in UTC), the month on show, the year range and the display mode."
        },
        {
          "name": "rememberDateRangePickerState",
          "use": "Creates and keeps a DateRangePickerState across recompositions."
        },
        {
          "name": "DateRangePickerDefaults",
          "use": "The default title and headline for date range pickers."
        }
      ]
    }
  }
};
