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
        {"name": "Table", "note": "iOS 16.0. Apple: \"A container that presents rows of data arranged in one or more columns, optionally providing the ability to select one or more members.\""},
        {"name": "tableStyle", "note": "`.tableStyle(_:)`, iOS 16.0. Apple: \"Sets the style for tables within this view.\""},
        {"name": "tableColumnHeaders", "note": "`.tableColumnHeaders(_:)`, iOS 17.0. Apple: \"Controls the visibility of a `Table`’s column header views.\""}
      ]
    }
  }
};
