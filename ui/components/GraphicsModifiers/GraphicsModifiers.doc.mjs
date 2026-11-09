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
        {"name": "aspectRatio3D", "note": "`.aspectRatio3D(_:contentMode:)`, not on iOS. Apple: \"Constrains this view’s dimensions to the specified 3D aspect ratio.\"", "status": "unavailable-ios", "replacement": "aspectRatio"},
        {"name": "blendMode", "note": "`.blendMode(_:)`, iOS 13.0. Apple: \"Sets the blend mode for compositing this view with overlapping views.\""},
        {"name": "blur", "note": "`.blur(radius:opaque:)`, iOS 13.0. Apple: \"Applies a Gaussian blur to this view.\""},
        {"name": "brightness", "note": "`.brightness(_:)`, iOS 13.0. Apple: \"Brightens this view by the specified amount.\""},
        {"name": "clipped", "note": "`.clipped(antialiased:)`, iOS 13.0. Apple: \"Clips this view to its bounding rectangular frame.\""},
        {"name": "clipShape", "note": "`.clipShape(_:style:)`, iOS 13.0. Apple: \"Sets a clipping shape for this view.\""},
        {"name": "colorEffect", "note": "`.colorEffect(_:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a filter effect on the color of each pixel.\""},
        {"name": "colorInvert", "note": "`.colorInvert()`, iOS 13.0. Apple: \"Inverts the colors in this view.\""},
        {"name": "colorMultiply", "note": "`.colorMultiply(_:)`, iOS 13.0. Apple: \"Adds a color multiplication effect to this view.\""},
        {"name": "compositingGroup", "note": "`.compositingGroup()`, iOS 13.0. Apple: \"Wraps this view in a compositing group.\""},
        {"name": "containerShape", "note": "`.containerShape(_:)`, iOS 26.0. Apple: \"Sets the container shape to use for any container relative shape or concentric rectangle within this view.\""},
        {"name": "contrast", "note": "`.contrast(_:)`, iOS 13.0. Apple: \"Sets the contrast and separation between similar colors in this view.\""},
        {"name": "distortionEffect", "note": "`.distortionEffect(_:maxSampleOffset:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a geometric distortion effect on the location of each pixel.\""},
        {"name": "drawingGroup", "note": "`.drawingGroup(opaque:colorMode:)`, iOS 13.0. Apple: \"Composites this view’s contents into an offscreen image before final display.\""},
        {"name": "grayscale", "note": "`.grayscale(_:)`, iOS 13.0. Apple: \"Adds a grayscale effect to this view.\""},
        {"name": "hueRotation", "note": "`.hueRotation(_:)`, iOS 13.0. Apple: \"Applies a hue rotation effect to this view.\""},
        {"name": "layerEffect", "note": "`.layerEffect(_:maxSampleOffset:isEnabled:)`, iOS 17.0. Apple: \"Returns a new view that applies `shader` to `self` as a filter on the raster layer created from `self`.\""},
        {"name": "luminanceToAlpha", "note": "`.luminanceToAlpha()`, iOS 13.0. Apple: \"Adds a luminance to alpha effect to this view.\""},
        {"name": "mask", "note": "`.mask(alignment:_:)`, iOS 15.0. Apple: \"Masks this view using the alpha channel of the given view.\""},
        {"name": "materialActiveAppearance", "note": "`.materialActiveAppearance(_:)`, iOS 18.0. Apple: \"Sets an explicit active appearance for materials in this view.\""},
        {"name": "opacity", "note": "`.opacity(_:)`, iOS 13.0. Apple: \"Sets the transparency of this view.\""},
        {"name": "perspectiveRotationEffect", "note": "`.perspectiveRotationEffect(_:axis:anchor:anchorZ:perspective:)`, not on iOS. Apple: \"Renders a view’s content as if it’s rotated in three dimensions around the specified axis.\"", "status": "unavailable-ios", "replacement": "rotation3DEffect"},
        {"name": "projectionEffect", "note": "`.projectionEffect(_:)`, iOS 13.0. Apple: \"Applies a projection transformation to this view’s rendered output.\""},
        {"name": "rotation3DEffect", "note": "`.rotation3DEffect(_:axis:anchor:anchorZ:perspective:)`, iOS 13.0. Apple: \"Renders a view’s content as if it’s rotated in three dimensions around the specified axis.\""},
        {"name": "rotation3DLayout", "note": "`.rotation3DLayout(_:)`, not on iOS. Apple: \"Rotates a view with impacts to its frame in a containing layout\"", "status": "unavailable-ios", "replacement": "rotation3DEffect"},
        {"name": "rotationEffect", "note": "`.rotationEffect(_:anchor:)`, iOS 13.0. Apple: \"Rotates a view’s rendered output in two dimensions around the specified point.\""},
        {"name": "saturation", "note": "`.saturation(_:)`, iOS 13.0. Apple: \"Adjusts the color saturation of this view.\""},
        {"name": "scaledToFill", "note": "`.scaledToFill()`, iOS 13.0. Apple: \"Scales this view to fill its parent.\""},
        {"name": "scaledToFill3D", "note": "`.scaledToFill3D()`, not on iOS. Apple: \"Scales this view to fill its parent.\"", "status": "unavailable-ios", "replacement": "scaledToFill"},
        {"name": "scaledToFit", "note": "`.scaledToFit()`, iOS 13.0. Apple: \"Scales this view to fit its parent.\""},
        {"name": "scaledToFit3D", "note": "`.scaledToFit3D()`, not on iOS. Apple: \"Scales this view to fit its parent.\"", "status": "unavailable-ios", "replacement": "scaledToFit"},
        {"name": "scaleEffect", "note": "`.scaleEffect(x:y:anchor:)`, iOS 13.0. Apple: \"Scales this view’s rendered output by the given horizontal and vertical amounts, relative to an anchor point.\""},
        {"name": "shadow", "note": "`.shadow(color:radius:x:y:)`, iOS 13.0. Apple: \"Adds a shadow to this view.\""},
        {"name": "transform3DEffect", "note": "`.transform3DEffect(_:)`, not on iOS. Apple: \"Applies a 3D transformation to this view’s rendered output.\"", "status": "unavailable-ios", "replacement": "transformEffect"},
        {"name": "transformEffect", "note": "`.transformEffect(_:)`, iOS 13.0. Apple: \"Applies an affine transformation to this view’s rendered output.\""},
        {"name": "visualEffect", "note": "`.visualEffect(_:)`, iOS 17.0. Apple: \"Applies effects to this view, while providing access to layout information through a geometry proxy.\""},
        {"name": "visualEffect3D", "note": "`.visualEffect3D(_:)`, not on iOS. Apple: \"Applies effects to this view, while providing access to layout information through a 3D geometry proxy.\"", "status": "unavailable-ios", "replacement": "visualEffect"},
        {"name": "cornerRadius", "note": "`.cornerRadius(_:antialiased:)`, iOS 13.0. Apple: \"Clips this view to its bounding frame, with the specified corner radius.\"", "status": "deprecated", "replacement": "clipShape"}
      ]
    }
  }
};
