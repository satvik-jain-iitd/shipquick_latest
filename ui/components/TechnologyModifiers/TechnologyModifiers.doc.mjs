/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "TechnologyModifiers",
  "displayName": "Technology modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "TechnologyModifiers",
  "category": "Utility",
  "keywords": [
    "health kit",
    "reality kit",
    "music picker",
    "sign in with apple",
    "device management",
    "sensor anchor"
  ],
  "usage": {
    "description": "Modifiers from other Apple frameworks that have no doc of their own: HealthKit, WorkoutKit, MusicKit, RealityKit, Core Motion, Core Location, Nearby Interaction, device management, Sign in with Apple and the system pickers. StoreKit, MapKit, TipKit, PassKit and Image Playground rows live in their own docs. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Technology-specific modifiers",
      "variants": [
        {"name": "automatedDeviceEnrollmentAddition", "note": "`.automatedDeviceEnrollmentAddition(isPresented:)`, iOS 16.0. Apple: \"Presents a modal view that enables users to add devices to their organization.\""},
        {"name": "continuityDevicePicker", "note": "`.continuityDevicePicker(isPresented:onDidConnect:)`, not on iOS. Apple: \"A `continuityDevicePicker` should be used to discover and connect nearby continuity device through a button interface or other form of activation. On tvOS, this presents a fullscreen continuity device picker experience when selected. The modal view covers as much the screen of `self` as possible when a given condition is true.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (tvOS picks a nearby Continuity device; Apple offers it on tvOS only)"},
        {"name": "groupActivityAssociation", "note": "`.groupActivityAssociation(_:)`, not on iOS. Apple: \"Specifies how a view should be associated with the current SharePlay group activity.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS SharePlay spatial placement only)"},
        {"name": "healthDataAccessRequest", "note": "`.healthDataAccessRequest(store:objectType:predicate:trigger:completion:)`, iOS 17.0. Apple: \"Asynchronously requests permission to read a data type that requires per-object authorization (such as vision prescriptions).\""},
        {"name": "journalingSuggestionsPicker", "note": "`.journalingSuggestionsPicker(isPresented:onCompletion:)`, iOS 17.2. Apple: \"Presents a visual picker interface that contains events and images that a person can select to retrieve more information.\""},
        {"name": "managedContentStyle", "note": "`.managedContentStyle(_:)`, iOS 17.2. Apple: \"Applies a managed content style to the view.\""},
        {"name": "musicPicker", "note": "`.musicPicker(isPresented:title:selection:)`, iOS 27.0. Apple: \"Presents a music picker to select items from the Apple Music catalog and the user’s music library.\""},
        {"name": "photosPickerMetadataOptions", "note": "`.photosPickerMetadataOptions(_:)`, iOS 27.0. Apple: \"Sets metadata options for the Photos picker.\""},
        {"name": "realityViewCameraControls", "note": "`.realityViewCameraControls(_:)`, iOS 18.0. Apple: \"Adds gestures that control the position and direction of a virtual camera.\""},
        {"name": "realityViewLayoutBehavior", "note": "`.realityViewLayoutBehavior(_:)`, iOS 26.0. Apple: \"A view modifier that controls the frame sizing and content alignment behavior for `RealityView`\""},
        {"name": "signInWithAppleButtonStyle", "note": "`.signInWithAppleButtonStyle(_:)`, iOS 14.0. Apple: \"Sets the style used for displaying the control (see `SignInWithAppleButton.Style`).\""},
        {"name": "tabletopGame", "note": "`.tabletopGame(_:parent:automaticUpdate:)`, not on iOS. Apple: \"Adds a tabletop game to a view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS tabletop game in 3D space)"},
        {"name": "transactionPicker", "note": "`.transactionPicker(isPresented:selection:)`, iOS 18.0. Apple: \"Presents a picker that selects a collection of transactions.\""},
        {"name": "transactionTask", "note": "`.transactionTask(_:action:)`, iOS 18.1. Apple: \"Provides a task to perform before this view appears\""},
        {"name": "workoutPreview", "note": "`.workoutPreview(_:isPresented:)`, iOS 17.0. Apple: \"Presents a preview of the workout contents as a modal sheet\""},
        {"name": "deviceMotionAnchor", "note": "`.deviceMotionAnchor(manager:isEnabled:)`, iOS 27.2. Apple: \"Specifies this view as the reference body for the motion manager’s device-motion calculations.\""},
        {"name": "locationHeadingAnchor", "note": "`.locationHeadingAnchor(manager:isEnabled:)`, iOS 27.2. Apple: \"Specifies this view as the reference body for the location manager’s heading calculations.\""},
        {"name": "nearbyInteractionOriginAnchor", "note": "`.nearbyInteractionOriginAnchor(session:isEnabled:)`, iOS 27.2. Apple: \"Specifies this view as the reference body for the nearby interaction session’s angle calculations.\""}
      ]
    }
  }
};
