/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Picker",
  "displayName": "Picker",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Picker",
  "category": "Form Controls",
  "keywords": [
    "picker",
    "select",
    "choose one",
    "options",
    "wheel",
    "menu picker"
  ],
  "usage": {
    "description": "Picker lets people choose one value from a set. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Set the look with the pickerStyle modifier, not by drawing your own control."
      },
      {
        "guidance": true,
        "description": "Give every picker a label, even when the style hides it."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "Picker", "note": "iOS 13.0. Apple: \"A control for selecting from a set of mutually exclusive values.\""}
      ]
    }
  }
};
