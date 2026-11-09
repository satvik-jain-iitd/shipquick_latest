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
        {"name": "ArrangementView", "note": "iOS 27.1. Apple: \"A view that dynamically lays out a primary and secondary view based on size class, orientation, and reserved regions.\""},
        {"name": "GeometryReader", "note": "iOS 13.0. Apple: \"A container view that defines its content as a function of its own size and coordinate space.\""},
        {"name": "GeometryReader3D", "note": "not on iOS. Apple: \"A container view that defines its content as a function of its own size and coordinate space.\"", "status": "unavailable-ios", "replacement": "GeometryReader"},
        {"name": "Group", "note": "iOS 13.0. Apple: \"A type that collects multiple instances of a content type — like views, scenes, or commands — into a single unit.\""},
        {"name": "HSplitView", "note": "not on iOS. Apple: \"A layout container that arranges its children in a horizontal line and allows the user to resize them using dividers placed between them.\"", "status": "unavailable-ios", "replacement": "NavigationSplitView"},
        {"name": "HStack", "note": "iOS 13.0. Apple: \"A view that arranges its subviews in a horizontal line.\""},
        {"name": "LazyHStack", "note": "iOS 14.0. Apple: \"A view that arranges its children in a line that grows horizontally, creating items only as needed.\""},
        {"name": "LazyVStack", "note": "iOS 14.0. Apple: \"A view that arranges its children in a line that grows vertically, creating items only as needed.\""},
        {"name": "Spacer", "note": "iOS 13.0. Apple: \"A flexible space that expands along the major axis of its containing stack layout, or on both axes if not contained in a stack.\""},
        {"name": "ViewThatFits", "note": "iOS 16.0. Apple: \"A view that adapts to the available space by providing the first child view that fits.\""},
        {"name": "VSplitView", "note": "not on iOS. Apple: \"A layout container that arranges its children in a vertical line and allows the user to resize them using dividers placed between them.\"", "status": "unavailable-ios", "replacement": "VStack"},
        {"name": "VStack", "note": "iOS 13.0. Apple: \"A view that arranges its subviews in a vertical line.\""},
        {"name": "ZStack", "note": "iOS 13.0. Apple: \"A view that overlays its subviews, aligning them in both axes.\""},
        {"name": "ZStackContent3D", "note": "not on iOS. Apple: \"A type that adds spacing to a `ZStack`.\"", "status": "unavailable-ios", "replacement": "ZStack"}
      ],
      "supporting": [
        {"name": "ArrangementViewStyleConfiguration.Primary", "use": "iOS 27.1. Apple: \"A type-erased view of the primary content of an arrangement view.\""},
        {"name": "ArrangementViewStyleConfiguration.Secondary", "use": "iOS 27.1. Apple: \"A type-erased view of the secondary content of an arrangement view.\""}
      ]
    }
  }
};
