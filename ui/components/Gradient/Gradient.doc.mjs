/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Gradient",
  "displayName": "Colors and gradients",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Gradient",
  "category": "Utility",
  "keywords": [
    "color",
    "gradient",
    "linear gradient",
    "radial gradient",
    "mesh gradient",
    "fill"
  ],
  "usage": {
    "description": "Color and the gradient types are views and fills. Use the SwiftUI type as Apple ships it. Do not redraw it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Take every color from the tokens in design/tokens.json. Do not type a new color."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Gradient",
      "variants": [
        {"name": "AngularGradient", "note": "iOS 13.0. Apple: \"An angular gradient.\""},
        {"name": "EllipticalGradient", "note": "iOS 15.0. Apple: \"A radial gradient that draws an ellipse.\""},
        {"name": "LinearGradient", "note": "iOS 13.0. Apple: \"A linear gradient.\""},
        {"name": "MeshGradient", "note": "iOS 18.0. Apple: \"A two-dimensional gradient defined by a 2D grid of positioned colors.\""},
        {"name": "RadialGradient", "note": "iOS 13.0. Apple: \"A radial gradient.\""}
      ]
    }
  }
};
