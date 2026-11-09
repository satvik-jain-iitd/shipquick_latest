/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Form",
  "displayName": "Form",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Form",
  "category": "Form Controls",
  "keywords": [
    "form",
    "settings",
    "labeled content",
    "grouped rows",
    "input screen"
  ],
  "usage": {
    "description": "Form groups controls for data entry, like a settings screen. LabeledContent shows a label next to a value. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "formStyle", "note": "`.formStyle(_:)`, iOS 16.0. Apple: \"Sets the style for forms in a view hierarchy.\""},
        {"name": "labeledContentStyle", "note": "`.labeledContentStyle(_:)`, iOS 16.0. Apple: \"Sets a style for labeled content.\""}
      ]
    }
  }
};
