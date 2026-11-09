/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/datepickers (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "DatePicker",
  "displayName": "Date picker",
  "platforms": {
    "android": "androidx.compose.material3.DatePicker",
    "ios": "SwiftUI.DatePicker",
    "web": null
  },
  "platformUsage": {
    "android": {
      "description": "It also picks a range, from a calendar or by typing. Docked sits in the layout. Modal shows in DatePickerDialog. DateRangePicker picks a start and an end.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Create the state with rememberDatePickerState and read selectedDateMillis."
        },
        {
          "guidance": true,
          "description": "Use DatePickerDialog for a modal picker."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on each day only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS, DatePicker picks a date, a time, or both. Apple: \"A control for selecting an absolute date.\" datePickerStyle(_:) sets the look: .compact, .graphical (a calendar) or .wheel.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Bind selection to a Date held in @State."
        },
        {
          "guidance": true,
          "description": "Limit the dates with in:, like Date()... for future dates only."
        },
        {
          "guidance": true,
          "description": "Pick what shows with displayedComponents: .date, .hourAndMinute, or both."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
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
    "description": "A date picker lets the user pick a date.",
    "bestPractices": [
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
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "Says what the date is for. VoiceOver reads it.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "selection",
      "type": "Binding<Date>",
      "description": "The picked date.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "in",
      "type": "ClosedRange<Date>",
      "description": "The dates the user may pick. Partial ranges work too.",
      "platform": "ios"
    },
    {
      "name": "displayedComponents",
      "type": "DatePickerComponents",
      "description": "Which parts show: .date, .hourAndMinute.",
      "platform": "ios",
      "default": "[.hourAndMinute, .date]"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "DatePickerDefaults.DatePickerTitle",
          "note": "The default title at the top of a DatePicker. It changes with the display mode."
        },
        {
          "name": "DatePickerDefaults.DatePickerHeadline",
          "note": "The default headline that shows the chosen date, or a hint when none is chosen."
        }
      ],
      "supporting": [
        {
          "name": "DatePickerState",
          "use": "Holds the chosen date (selectedDateMillis, in UTC), the month on show, the year range, the display mode and the selectable dates."
        },
        {
          "name": "rememberDatePickerState",
          "use": "Creates and keeps a DatePickerState, with the first date, year range, display mode and selectable dates you give."
        },
        {
          "name": "DatePickerDefaults",
          "use": "Default colours, shape, year range, date formatter, title, headline and sizes for date pickers."
        },
        {
          "name": "DatePickerColors",
          "use": "The container, title, headline, day, year and selection colours of a date picker. Make one with DatePickerDefaults.colors()."
        },
        {
          "name": "DatePickerFormatter",
          "use": "Turns dates into text for the picker's headline and month line (formatDate, formatMonthYear). Make one with DatePickerDefaults.dateFormatter()."
        },
        {
          "name": "DisplayMode",
          "use": "How a date picker shows: Picker (a calendar) or Input (a text field). The user can switch with the mode button."
        },
        {
          "name": "SelectableDates",
          "use": "Says which dates and years the user can pick: isSelectableDate and isSelectableYear. Use it to block past dates or weekends."
        }
      ]
    }
  }
};
