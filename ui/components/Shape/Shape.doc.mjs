/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Shape",
  "displayName": "Shapes",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Shape",
  "category": "Utility",
  "keywords": [
    "shape",
    "rectangle",
    "circle",
    "capsule",
    "rounded rectangle",
    "path",
    "canvas"
  ],
  "usage": {
    "description": "Shapes fill or stroke a simple form, like a circle behind an icon. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Do not build a control from shapes, Path or Canvas. Rule 38 refuses hand-drawn UI. Use the library control."
      },
      {
        "guidance": true,
        "description": "Use a shape for a background, a mask or a clip."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "ButtonBorderShape", "note": "iOS 15.0. Apple: \"A shape used to draw a button’s border.\""},
        {"name": "Canvas", "note": "iOS 15.0. Apple: \"A view type that supports immediate mode drawing.\""},
        {"name": "Capsule", "note": "iOS 13.0. Apple: \"A capsule shape aligned inside the frame of the view containing it.\""},
        {"name": "Circle", "note": "iOS 13.0. Apple: \"A circle centered on the frame of the view containing it.\""},
        {"name": "ConcentricRectangle", "note": "iOS 26.0. Apple: \"A shape whose corners you configure, individually or uniformly, to be squared, rounded, or concentric relative to a container shape’s corners.\""},
        {"name": "ContainerRelativeShape", "note": "iOS 14.0. Apple: \"A shape whose dimensions the system calculates from an inset version of the current container shape.\""},
        {"name": "Ellipse", "note": "iOS 13.0. Apple: \"An ellipse aligned inside the frame of the view containing it.\""},
        {"name": "Path", "note": "iOS 13.0. Apple: \"The outline of a 2D shape.\""},
        {"name": "Rectangle", "note": "iOS 13.0. Apple: \"A rectangular shape aligned inside the frame of the view containing it.\""},
        {"name": "RoundedRectangle", "note": "iOS 13.0. Apple: \"A rectangular shape with rounded corners, aligned inside the frame of the view containing it.\""},
        {"name": "UnevenRoundedRectangle", "note": "iOS 16.0. Apple: \"A rectangular shape with rounded corners with different values, aligned inside the frame of the view containing it.\""}
      ]
    }
  }
};
