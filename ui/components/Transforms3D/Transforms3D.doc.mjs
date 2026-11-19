/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Transforms3D",
  "displayName": "3D transforms",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Transforms3D",
  "category": "Utility",
  "keywords": [
      "3D",
      "rotation3D",
      "perspective",
      "projection",
      "transform",
      "visionOS"
  ],
  "usage": {
    "description": "Modifiers that rotate, project, scale and lay out a view in three dimensions. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "3D transforms",
      "variants": [
        {"name": "aspectRatio3D", "note": "`.aspectRatio3D(_:contentMode:)`, not on iOS. Apple: \"Constrains this view’s dimensions to the specified 3D aspect ratio.\"", "status": "unavailable-ios", "replacement": "aspectRatio"},
        {"name": "scaledToFill3D", "note": "`.scaledToFill3D()`, not on iOS. Apple: \"Scales this view to fill its parent.\"", "status": "unavailable-ios", "replacement": "scaledToFill"},
        {"name": "scaledToFit3D", "note": "`.scaledToFit3D()`, not on iOS. Apple: \"Scales this view to fit its parent.\"", "status": "unavailable-ios", "replacement": "scaledToFit"},
        {"name": "perspectiveRotationEffect", "note": "`.perspectiveRotationEffect(_:axis:anchor:anchorZ:perspective:)`, not on iOS. Apple: \"Renders a view’s content as if it’s rotated in three dimensions around the specified axis.\"", "status": "unavailable-ios", "replacement": "rotation3DEffect"},
        {"name": "projectionEffect", "note": "`.projectionEffect(_:)`, iOS 13.0. Apple: \"Applies a projection transformation to this view’s rendered output.\""},
        {"name": "rotation3DEffect", "note": "`.rotation3DEffect(_:axis:anchor:anchorZ:perspective:)`, iOS 13.0. Apple: \"Renders a view’s content as if it’s rotated in three dimensions around the specified axis.\""},
        {"name": "rotation3DLayout", "note": "`.rotation3DLayout(_:)`, not on iOS. Apple: \"Rotates a view with impacts to its frame in a containing layout\"", "status": "unavailable-ios", "replacement": "rotation3DEffect"},
        {"name": "transform3DEffect", "note": "`.transform3DEffect(_:)`, not on iOS. Apple: \"Applies a 3D transformation to this view’s rendered output.\"", "status": "unavailable-ios", "replacement": "transformEffect"},
        {"name": "visualEffect3D", "note": "`.visualEffect3D(_:)`, not on iOS. Apple: \"Applies effects to this view, while providing access to layout information through a 3D geometry proxy.\"", "status": "unavailable-ios", "replacement": "visualEffect"}
      ]
    }
  }
};
