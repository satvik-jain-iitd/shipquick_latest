/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "LayoutModifiers",
  "displayName": "Layout modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "LayoutModifiers",
  "category": "Layout",
  "keywords": [
    "frame",
    "padding",
    "safe area",
    "offset",
    "position",
    "layout priority"
  ],
  "usage": {
    "description": "Modifiers that set a view's size and place. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Take spacing from the tokens in design/tokens.json."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Layout modifiers",
      "variants": [
        {"name": "alignmentGuide", "note": "`.alignmentGuide(_:computeValue:)`, iOS 13.0. Apple: \"Sets the view’s horizontal alignment.\""},
        {"name": "containerCornerOffset", "note": "`.containerCornerOffset(_:sizeToFit:)`, iOS 26.0. Apple: \"Adjusts the view’s layout to avoid the container view’s corner insets for the specified edges.\""},
        {"name": "containerRelativeFrame", "note": "`.containerRelativeFrame(_:alignment:)`, iOS 17.0. Apple: \"Positions this view within an invisible frame with a size relative to the nearest container.\""},
        {"name": "containerValue", "note": "`.containerValue(_:_:)`, iOS 18.0. Apple: \"Sets a particular container value of a view.\""},
        {"name": "contentMargins", "note": "`.contentMargins(_:for:)`, iOS 17.0. Apple: \"Configures the content margin for a provided placement.\""},
        {"name": "coordinateSpace", "note": "`.coordinateSpace(_:)`, iOS 17.0. Apple: \"Assigns a name to the view’s coordinate space, so other code can operate on dimensions like points and sizes relative to the named space.\""},
        {"name": "fixedSize", "note": "`.fixedSize()`, iOS 13.0. Apple: \"Fixes this view at its ideal size.\""},
        {"name": "frame", "note": "`.frame(width:height:alignment:)`, iOS 13.0. Apple: \"Positions this view within an invisible frame with the specified size.\""},
        {"name": "ignoresSafeArea", "note": "`.ignoresSafeArea(_:edges:)`, iOS 14.0. Apple: \"Expands the safe area of a view.\""},
        {"name": "layoutDirectionBehavior", "note": "`.layoutDirectionBehavior(_:)`, iOS 17.0. Apple: \"Sets the behavior of this view for different layout directions.\""},
        {"name": "layoutPriority", "note": "`.layoutPriority(_:)`, iOS 13.0. Apple: \"Sets the priority by which a parent layout should apportion space to this child.\""},
        {"name": "layoutValue", "note": "`.layoutValue(key:value:)`, iOS 16.0. Apple: \"Associates a value with a custom layout property.\""},
        {"name": "offset", "note": "`.offset(_:)`, iOS 13.0. Apple: \"Offset this view by the horizontal and vertical amount specified in the offset parameter.\""},
        {"name": "padding", "note": "`.padding(_:)`, iOS 13.0. Apple: \"Adds a different padding amount to each edge of this view.\""},
        {"name": "padding3D", "note": "`.padding3D(_:)`, not on iOS. Apple: \"Pads this view using the edge insets you specify.\"", "status": "unavailable-ios", "replacement": "padding"},
        {"name": "position", "note": "`.position(_:)`, iOS 13.0. Apple: \"Positions the center of this view at the specified point in its parent’s coordinate space.\""},
        {"name": "safeAreaBar", "note": "`.safeAreaBar(edge:alignment:spacing:content:)`, iOS 26.0. Apple: \"Shows the specified content as a custom bar beside the modified view.\""},
        {"name": "safeAreaInset", "note": "`.safeAreaInset(edge:alignment:spacing:content:)`, iOS 15.0. Apple: \"Shows the specified content beside the modified view.\""},
        {"name": "safeAreaPadding", "note": "`.safeAreaPadding(_:)`, iOS 17.0. Apple: \"Adds the provided insets into the safe area of this view.\""},
        {"name": "scenePadding", "note": "`.scenePadding(_:)`, iOS 15.0. Apple: \"Adds padding to the specified edges of this view using an amount that’s appropriate for the current scene.\""},
        {"name": "zIndex", "note": "`.zIndex(_:)`, iOS 13.0. Apple: \"Controls the display order of overlapping views.\""},
        {"name": "edgesIgnoringSafeArea", "note": "`.edgesIgnoringSafeArea(_:)`, iOS 13.0. Apple: \"Changes the view’s proposed area to extend outside the screen’s safe areas.\"", "status": "deprecated", "replacement": "ignoresSafeArea"}
      ]
    }
  }
};
