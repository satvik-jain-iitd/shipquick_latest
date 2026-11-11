/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "PresentationModifiers",
  "displayName": "Presentation modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "PresentationModifiers",
  "category": "Overlay",
  "keywords": [
    "present",
    "quick look",
    "translation",
    "certificate sheet",
    "modal"
  ],
  "usage": {
    "description": "Modifiers that present system screens no other doc covers, like a Quick Look preview or a translation popover. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Presentation modifiers",
      "variants": [
        {"name": "certificateSheet", "note": "`.certificateSheet(trust:title:message:help:)`, iOS 18.4. Apple: \"Displays a certificate sheet using the provided certificate trust.\""},
        {"name": "familyActivityPicker", "note": "`.familyActivityPicker(isPresented:selection:)`, iOS 15.0. Apple: \"Presents an activity picker view as a sheet.\""},
        {"name": "foveatedStreamingPauseSheet", "note": "`.foveatedStreamingPauseSheet(session:)`, not on iOS. Apple: \"Tells the system to present a sheet with controls for resuming or ending the foveated streaming session when it pauses.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS foveated streaming only)"},
        {"name": "gameSaveSyncingAlert", "note": "`.gameSaveSyncingAlert(directory:finishedLoading:)`, iOS 26.0. Apple: \"Presents a modal view while the game synced directory loads.\""},
        {"name": "musicSubscriptionOffer", "note": "`.musicSubscriptionOffer(isPresented:options:onLoadCompletion:)`, iOS 15.0. Apple: \"Initiates the process of presenting a sheet with subscription offers for Apple Music when the `isPresented` binding is `true`.\""},
        {"name": "quickLookPreview", "note": "`.quickLookPreview(_:)`, iOS 14.0. Apple: \"Presents a Quick Look preview of the contents of a single URL.\""},
        {"name": "recordingEditor", "note": "`.recordingEditor(_:)`, iOS 27.0. Apple: \"Presents the recording editor for the given recording URL.\""},
        {"name": "translationPresentation", "note": "`.translationPresentation(isPresented:text:attachmentAnchor:arrowEdge:replacementAction:)`, iOS 17.4. Apple: \"Presents a translation popover when a given condition is true.\""},
        {"name": "translationTask", "note": "`.translationTask(_:action:)`, iOS 18.0. Apple: \"Adds a task to perform before this view appears or when the translation configuration changes.\""}
      ]
    }
  }
};
