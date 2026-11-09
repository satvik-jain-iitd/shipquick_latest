/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/progress (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "ProgressIndicator",
  "displayName": "Progress indicator",
  "platforms": {
    "android": "androidx.compose.material3.LinearProgressIndicator",
    "ios": "SwiftUI.ProgressView",
    "web": "@astryxdesign/core/ProgressBar"
  },
  "platformUsage": {
    "android": {
      "description": "It comes as a line (LinearProgressIndicator) or a circle (CircularProgressIndicator).",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Pass progress when you know how much is done, as a number from 0.0 to 1.0."
        },
        {
          "guidance": true,
          "description": "Leave progress out when you do not know how long it takes."
        }
      ]
    },
    "ios": {
      "description": "On iOS, ProgressView shows a bar when it has a value, and a spinner when it does not. Apple: init(value:total:) \"Creates a progress view for showing determinate progress.\"",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Pass value and total when you know how much is done, like ProgressView(value: done, total: 10)."
        },
        {
          "guidance": true,
          "description": "Leave value out, or pass nil, when you do not know how long it takes."
        }
      ],
      "accessibility": []
    }
  },
  "group": "Progress",
  "category": "Feedback & Status",
  "keywords": [
    "progress",
    "loading",
    "spinner",
    "bar",
    "upload"
  ],
  "usage": {
    "description": "A progress indicator shows that work is going on, like loading data or an upload. Determinate shows how much is done. Indeterminate moves until the work ends.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Leave the user with no sign of work during a long wait."
      }
    ],
    "accessibility": [
      {
        "name": "Say what loads",
        "category": "Content",
        "criterion": "1.3.1 Info and Relationships",
        "requirement": "label near it",
        "description": "Put words near the indicator that say what is loading, so the progress has a meaning."
      },
      {
        "name": "Shape contrast",
        "category": "Color contrast",
        "criterion": "1.4.11 Non-text Contrast",
        "requirement": "3:1",
        "description": "The edge or the mark that shows state has at least 3:1 contrast with what is behind it."
      }
    ],
    "anatomy": [
      {
        "name": "Track",
        "required": true,
        "description": "The full length."
      },
      {
        "name": "Indicator",
        "required": true,
        "description": "The part that fills or moves."
      }
    ]
  },
  "props": [
    {
      "name": "progress",
      "type": "() => number",
      "description": "How much is done, from 0.0 to 1.0. Leave it out for indeterminate."
    },
    {
      "name": "value",
      "type": "Double?",
      "description": "How much is done, out of total. nil means indeterminate.",
      "platform": "ios",
      "default": "nil"
    },
    {
      "name": "total",
      "type": "Double",
      "description": "The value that means done.",
      "platform": "ios",
      "default": "1.0"
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "Words that say what loads. VoiceOver reads them.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "supporting": [
        {"name": "DefaultDateProgressLabel", "use": "iOS 16.0. Apple: \"The default type of the current value label when used by a date-relative progress view.\""},
        {"name": "ProgressViewStyleConfiguration.CurrentValueLabel", "use": "iOS 14.0. Apple: \"A type-erased label that describes the current value of a progress view.\""},
        {"name": "ProgressViewStyleConfiguration.Label", "use": "iOS 14.0. Apple: \"A type-erased label describing the task represented by the progress view.\""}
      ]
    }
  }
};
