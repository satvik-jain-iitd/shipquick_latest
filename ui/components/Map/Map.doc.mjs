/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Map",
  "displayName": "Map",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Map",
  "category": "Utility",
  "keywords": [
    "map kit",
    "map",
    "map camera",
    "look around",
    "map item"
  ],
  "usage": {
    "description": "Modifiers for MapKit's Map view: style, controls, camera, feature selection, map item details and Look Around. Each entry is a SwiftUI view modifier from MapKit. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Map",
      "variants": [
        {"name": "lookAroundViewer", "note": "`.lookAroundViewer(isPresented:scene:allowsNavigation:showsRoadLabels:pointsOfInterest:onDismiss:)`, iOS 17.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/lookaroundviewer(ispresented:scene:allowsnavigation:showsroadlabels:pointsofinterest:ondismiss:)"},
        {"name": "mapCameraKeyframeAnimator", "note": "`.mapCameraKeyframeAnimator(trigger:keyframes:)`, iOS 17.0. Apple: \"Uses the given keyframes to animate the camera of a `Map` when the given trigger value changes.\""},
        {"name": "mapControls", "note": "`.mapControls(_:)`, iOS 17.0. Apple: \"Configures all `Map` views in the associated environment to have standard size and position controls\""},
        {"name": "mapControlVisibility", "note": "`.mapControlVisibility(_:)`, iOS 17.0. Apple: \"Configures all Map controls in the environment to have the specified visibility\""},
        {"name": "mapFeatureSelectionAccessory", "note": "`.mapFeatureSelectionAccessory(_:)`, iOS 18.0. Apple: \"Specifies the selection accessory to display for a `MapFeature`\""},
        {"name": "mapFeatureSelectionContent", "note": "`.mapFeatureSelectionContent(content:)`, iOS 17.0. Apple: \"Specifies a custom presentation for the currently selected feature.\""},
        {"name": "mapFeatureSelectionDisabled", "note": "`.mapFeatureSelectionDisabled(_:)`, iOS 17.0. Apple: \"Specifies which map features should have selection disabled.\""},
        {"name": "mapItemDetailPopover", "note": "`.mapItemDetailPopover(isPresented:item:displaysMap:attachmentAnchor:)`, iOS 18.0. Apple: \"Presents a map item detail popover.\""},
        {"name": "mapItemDetailSheet", "note": "`.mapItemDetailSheet(isPresented:item:displaysMap:)`, iOS 18.0. Apple: \"Presents a map item detail sheet.\""},
        {"name": "mapScope", "note": "`.mapScope(_:)`, iOS 17.0. Apple: \"Creates a mapScope that SwiftUI uses to connect map controls to an associated map.\""},
        {"name": "mapStyle", "note": "`.mapStyle(_:)`, iOS 17.0. Apple: \"Specifies the map style to be used.\""},
        {"name": "onMapCameraChange", "note": "`.onMapCameraChange(frequency:_:)`, iOS 17.0. Apple: \"Performs an action when Map camera framing changes\""}
      ]
    }
  }
};
