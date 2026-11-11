/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "GraphicsModifiers",
  "displayName": "Graphics and rendering modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "GraphicsModifiers",
  "category": "Utility",
  "keywords": [
    "opacity",
    "blur",
    "shadow",
    "clip",
    "mask",
    "scale",
    "rotate"
  ],
  "usage": {
    "description": "Modifiers that change how a view is drawn: clip, blur, shadow, turn or scale. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Graphics and rendering modifiers",
      "variants": [
        {"name": "aspectRatio", "note": "`.aspectRatio(_:contentMode:)`, iOS 13.0. Apple: \"Constrains this view’s dimensions to the specified aspect ratio.\""},
        {"name": "blendMode", "note": "`.blendMode(_:)`, iOS 13.0. Apple: \"Sets the blend mode for compositing this view with overlapping views.\""},
        {"name": "blur", "note": "`.blur(radius:opaque:)`, iOS 13.0. Apple: \"Applies a Gaussian blur to this view.\""},
        {"name": "clipped", "note": "`.clipped(antialiased:)`, iOS 13.0. Apple: \"Clips this view to its bounding rectangular frame.\""},
        {"name": "clipShape", "note": "`.clipShape(_:style:)`, iOS 13.0. Apple: \"Sets a clipping shape for this view.\""},
        {"name": "compositingGroup", "note": "`.compositingGroup()`, iOS 13.0. Apple: \"Wraps this view in a compositing group.\""},
        {"name": "containerShape", "note": "`.containerShape(_:)`, iOS 26.0. Apple: \"Sets the container shape to use for any container relative shape or concentric rectangle within this view.\""},
        {"name": "drawingGroup", "note": "`.drawingGroup(opaque:colorMode:)`, iOS 13.0. Apple: \"Composites this view’s contents into an offscreen image before final display.\""},
        {"name": "mask", "note": "`.mask(alignment:_:)`, iOS 15.0. Apple: \"Masks this view using the alpha channel of the given view.\""},
        {"name": "materialActiveAppearance", "note": "`.materialActiveAppearance(_:)`, iOS 18.0. Apple: \"Sets an explicit active appearance for materials in this view.\""},
        {"name": "opacity", "note": "`.opacity(_:)`, iOS 13.0. Apple: \"Sets the transparency of this view.\""},
        {"name": "rotationEffect", "note": "`.rotationEffect(_:anchor:)`, iOS 13.0. Apple: \"Rotates a view’s rendered output in two dimensions around the specified point.\""},
        {"name": "scaledToFill", "note": "`.scaledToFill()`, iOS 13.0. Apple: \"Scales this view to fill its parent.\""},
        {"name": "scaledToFit", "note": "`.scaledToFit()`, iOS 13.0. Apple: \"Scales this view to fit its parent.\""},
        {"name": "scaleEffect", "note": "`.scaleEffect(x:y:anchor:)`, iOS 13.0. Apple: \"Scales this view’s rendered output by the given horizontal and vertical amounts, relative to an anchor point.\""},
        {"name": "shadow", "note": "`.shadow(color:radius:x:y:)`, iOS 13.0. Apple: \"Adds a shadow to this view.\""},
        {"name": "transformEffect", "note": "`.transformEffect(_:)`, iOS 13.0. Apple: \"Applies an affine transformation to this view’s rendered output.\""},
        {"name": "cornerRadius", "note": "`.cornerRadius(_:antialiased:)`, iOS 13.0. Apple: \"Clips this view to its bounding frame, with the specified corner radius.\"", "status": "deprecated", "replacement": "clipShape"}
      ]
    }
  }
};
