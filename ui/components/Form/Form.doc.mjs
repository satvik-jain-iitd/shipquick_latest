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
        {"name": "Form", "note": "iOS 13.0. Apple: \"A container for grouping controls used for data entry, such as in settings or inspectors.\""},
        {"name": "LabeledContent", "note": "iOS 16.0. Apple: \"A container for attaching a label to a value-bearing view.\""},
        {"name": "formStyle", "note": "`.formStyle(_:)`, iOS 16.0. Apple: \"Sets the style for forms in a view hierarchy.\""},
        {"name": "labeledContentStyle", "note": "`.labeledContentStyle(_:)`, iOS 16.0. Apple: \"Sets a style for labeled content.\""}
      ],
      "supporting": [
        {"name": "FormStyleConfiguration.Content", "use": "iOS 16.0. Apple: \"A type-erased content of a form.\""},
        {"name": "LabeledContentStyleConfiguration.Content", "use": "iOS 16.0. Apple: \"A type-erased content of a labeled content instance.\""},
        {"name": "LabeledContentStyleConfiguration.Label", "use": "iOS 16.0. Apple: \"A type-erased label of a labeled content instance.\""}
      ]
    }
  }
};
