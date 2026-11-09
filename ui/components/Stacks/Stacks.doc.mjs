/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Stacks",
  "displayName": "Stacks and layout containers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Stacks",
  "category": "Layout",
  "keywords": [
    "hstack",
    "vstack",
    "zstack",
    "spacer",
    "layout",
    "geometry reader",
    "group"
  ],
  "usage": {
    "description": "Stacks place views in a row, a column, or on top of each other. Spacer pushes views apart. These are layout containers. Rule 38 allows them. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "arrangementViewStyle", "note": "`.arrangementViewStyle(_:)`, iOS 27.1. Apple: \"Sets the style for arrangement views within this view.\""},
        {"name": "overlayArrangementEdge", "note": "`.overlayArrangementEdge(_:)`, iOS 27.1. Apple: \"The horizontal edge a view in an overlay arrangement aligns to when the arrangement transitions to a landscape orientation.\""},
        {"name": "splitArrangementFixedLayoutSize", "note": "`.splitArrangementFixedLayoutSize(horizontal:vertical:)`, iOS 27.1. Apple: \"Sets the preferred size constraint for a view in a split arrangement style to the ideal size of the view within its container.\""},
        {"name": "splitArrangementLayoutRatio", "note": "`.splitArrangementLayoutRatio(_:)`, iOS 27.1. Apple: \"Sets the preferred size ratio for a view in a split style arrangement view.\""},
        {"name": "splitArrangementLayoutSize", "note": "`.splitArrangementLayoutSize(minWidth:idealWidth:maxWidth:minHeight:idealHeight:maxHeight:)`, iOS 27.1. Apple: \"Sets the size constraints for a view in a split style arrangement view.\""}
      ]
    }
  }
};
