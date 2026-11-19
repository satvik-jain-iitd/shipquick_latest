/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Spatial",
  "displayName": "Spatial appearance",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Spatial",
  "category": "Utility",
  "keywords": [
      "visionOS",
      "spatial",
      "immersive",
      "surroundings",
      "hands",
      "baseplate"
  ],
  "usage": {
    "description": "Modifiers for visionOS: spatial overlays, the surroundings effect, hand visibility and the volume baseplate. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Spatial appearance",
      "variants": [
        {"name": "spatialOverlay", "note": "`.spatialOverlay(alignment:content:)`, not on iOS. Apple: \"Adds secondary views within the 3D bounds of this view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "spatialOverlayPreferenceValue", "note": "`.spatialOverlayPreferenceValue(_:alignment:_:)`, not on iOS. Apple: \"Uses the specified preference value from the view to produce another view occupying the same 3D space of the first view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "preferredSurroundingsEffect", "note": "`.preferredSurroundingsEffect(_:)`, not on iOS. Apple: \"Applies an effect to passthrough video.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it tints visionOS passthrough video; iOS has no passthrough)"},
        {"name": "breakthroughEffect", "note": "`.breakthroughEffect(_:)`, not on iOS. Apple: \"Ensures that the view is always visible to the user, even when other content is occluding it, like 3D models.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS content seen through 3D models; iOS has no 3D occlusion)"},
        {"name": "upperLimbVisibility", "note": "`.upperLimbVisibility(_:)`, not on iOS. Apple: \"Sets the preferred visibility of the user’s upper limbs, while an `ImmersiveSpace` scene is presented.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the person's arms in a visionOS immersive space)"},
        {"name": "volumeBaseplateVisibility", "note": "`.volumeBaseplateVisibility(_:)`, not on iOS. Apple: \"Sets the visibility of the baseplate of a volume, which appears when a user looks towards the ‘floor’ of a volume and during resize. Both `automatic` and `visible` will show the baseplate. `hidden` will never show it.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"}
      ]
    }
  }
};
