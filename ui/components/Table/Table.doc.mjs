/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Table",
  "displayName": "Table",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Table",
  "category": "Table & List",
  "keywords": [
    "table",
    "columns",
    "rows",
    "data grid",
    "sort"
  ],
  "usage": {
    "description": "Table shows rows of data in columns. On iPhone it shows only the first column. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use List when the data has one column on iPhone."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "tableStyle", "note": "`.tableStyle(_:)`, iOS 16.0. Apple: \"Sets the style for tables within this view.\""}
      ]
    }
  }
};
