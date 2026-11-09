/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ShapePlumbing",
  "displayName": "Shape plumbing",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ShapePlumbing",
  "category": "Utility",
  "keywords": [
    "any shape",
    "stroke",
    "fill",
    "offset shape",
    "rotated shape",
    "plumbing"
  ],
  "usage": {
    "description": "These types wrap a shape after you fill, stroke, move, turn or scale it. SwiftUI makes them for you. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "ShapePlumbing",
      "variants": [
        {"name": "AnyShape", "note": "iOS 16.0. Apple: \"A type-erased shape value.\""},
        {"name": "FillShapeView", "note": "iOS 17.0. Apple: \"A shape provider that fills its shape.\""},
        {"name": "OffsetShape", "note": "iOS 13.0. Apple: \"A shape with a translation offset transform applied to it.\""},
        {"name": "RotatedShape", "note": "iOS 13.0. Apple: \"A shape with a rotation transform applied to it.\""},
        {"name": "ScaledShape", "note": "iOS 13.0. Apple: \"A shape with a scale transform applied to it.\""},
        {"name": "StrokeBorderShapeView", "note": "iOS 17.0. Apple: \"A shape provider that strokes the border of its shape.\""},
        {"name": "StrokeShapeView", "note": "iOS 17.0. Apple: \"A shape provider that strokes its shape.\""},
        {"name": "TransformedShape", "note": "iOS 13.0. Apple: \"A shape with an affine transform applied to it.\""}
      ]
    }
  }
};
