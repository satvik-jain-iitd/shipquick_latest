/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ControlGroup",
  "displayName": "Control group",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ControlGroup",
  "category": "Action",
  "keywords": [
    "control group",
    "button group",
    "grouped controls",
    "toolbar group"
  ],
  "usage": {
    "description": "ControlGroup shows a few related controls together, like zoom in and zoom out. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "ControlGroup",
      "variants": [
        {"name": "ControlGroup", "note": "iOS 15.0. Apple: \"A container view that displays semantically-related controls in a visually-appropriate manner for the context\""},
        {"name": "controlGroupStyle", "note": "`.controlGroupStyle(_:)`, iOS 15.0. Apple: \"Sets the style for control groups within this view.\""}
      ],
      "supporting": [
        {"name": "ControlGroupStyleConfiguration.Content", "use": "iOS 15.0. Apple: \"A type-erased content of a `ControlGroup`.\""},
        {"name": "ControlGroupStyleConfiguration.Label", "use": "iOS 16.0. Apple: \"A type-erased label of a `ControlGroup`.\""}
      ]
    }
  }
};
