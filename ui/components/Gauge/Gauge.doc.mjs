/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Gauge",
  "displayName": "Gauge",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.Gauge",
    "web": null
  },
  "group": "Gauge",
  "category": "Feedback & Status",
  "keywords": [
    "gauge",
    "meter",
    "level",
    "value in range",
    "capacity"
  ],
  "usage": {
    "description": "Gauge shows one number inside a range, like a battery level. Apple: \"A view that shows a value within a range.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Write short labels for the value and both ends of the range."
      },
      {
        "guidance": false,
        "description": "Use a gauge for the progress of a task. Use a ProgressView."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "VoiceOver reads the visible labels, so name the value and both ends."
      }
    ],
    "anatomy": [
      {
        "name": "Track",
        "required": true,
        "description": "The range."
      },
      {
        "name": "Indicator",
        "required": true,
        "description": "Where the value sits."
      },
      {
        "name": "Labels",
        "required": false,
        "description": "Value and range ends."
      }
    ]
  },
  "props": [
    {
      "name": "value",
      "type": "number",
      "description": "The value to show. init(value:in:label:).",
      "required": true
    },
    {
      "name": "bounds",
      "type": "ClosedRange<BinaryFloatingPoint>",
      "description": "The range (the `in:` label).",
      "default": "0...1"
    },
    {
      "name": "label",
      "type": "() -> some View",
      "description": "Says what the gauge measures.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "gaugeStyle", "note": "`.gaugeStyle(_:)`, iOS 16.0. Apple: \"Sets the style for gauges within this view.\""}
      ]
    }
  }
};
