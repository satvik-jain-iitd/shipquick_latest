/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "InputModifiers",
  "displayName": "Input and event modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "InputModifiers",
  "category": "Utility",
  "keywords": [
    "on appear",
    "on change",
    "task",
    "open url",
    "user activity",
    "game controller"
  ],
  "usage": {
    "description": "Modifiers for view events and other input that no control doc owns: appear and disappear, value changes, open URLs, user activity, game controllers, cameras and visionOS or watchOS input. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it. Gestures, Focus, Keyboard, DragAndDrop and Hover have their own docs."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Input and event modifiers",
      "variants": [
        {"name": "cameraAnchor", "note": "`.cameraAnchor(isActive:)`, not on iOS. Apple: \"Specifies the view that should act as the virtual camera for Apple Vision Pro 2D Persona stream.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the virtual camera of a visionOS Persona stream)"},
        {"name": "digitalCrownAccessory", "note": "`.digitalCrownAccessory(_:)`, not on iOS. Apple: \"Specifies the visibility of Digital Crown accessory Views on Apple Watch.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the Apple Watch Digital Crown; iPhone has no crown)"},
        {"name": "digitalCrownRotation", "note": "`.digitalCrownRotation(_:from:through:sensitivity:isContinuous:isHapticFeedbackEnabled:onChange:onIdle:)`, not on iOS. Apple: \"Tracks Digital Crown rotations by updating the specified binding.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the Apple Watch Digital Crown; iPhone has no crown)"},
        {"name": "disabled", "note": "`.disabled(_:)`, iOS 13.0. Apple: \"Adds a condition that controls whether someone can interact with this view.\""},
        {"name": "exportableToServices", "note": "`.exportableToServices(_:)`, not on iOS. Apple: \"Exports items for consumption by shortcuts, quick actions, and services.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac Services and Continuity Camera import or export; iOS has no Services menu)"},
        {"name": "exportsItemProviders", "note": "`.exportsItemProviders(_:onExport:)`, not on iOS. Apple: \"Exports a read-only item provider for consumption by shortcuts, quick actions, and services.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac Services and Continuity Camera import or export; iOS has no Services menu)"},
        {"name": "handlesExternalEvents", "note": "`.handlesExternalEvents(preferring:allowing:)`, iOS 14.0. Apple: \"Specifies the external events that the view’s scene handles if the scene is already open.\""},
        {"name": "handlesGameControllerEvents", "note": "`.handlesGameControllerEvents(matching:)`, iOS 18.0. Apple: \"Specifies the game controllers events which should be delivered through the GameController framework when the view, or one of its descendants has focus.\""},
        {"name": "immersiveEnvironmentPicker", "note": "`.immersiveEnvironmentPicker(content:)`, not on iOS. Apple: \"Add menu items to open immersive spaces from a media player’s environment picker.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "importableFromServices", "note": "`.importableFromServices(for:action:)`, not on iOS. Apple: \"Enables importing items from services, such as Continuity Camera on macOS.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac Services and Continuity Camera import or export; iOS has no Services menu)"},
        {"name": "importsItemProviders", "note": "`.importsItemProviders(_:onImport:)`, not on iOS. Apple: \"Enables importing item providers from services, such as Continuity Camera on macOS.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac Services and Continuity Camera import or export; iOS has no Services menu)"},
        {"name": "interactionActivityTrackingTag", "note": "`.interactionActivityTrackingTag(_:)`, iOS 16.0. Apple: \"Sets a tag that you use for tracking interactivity.\""},
        {"name": "onAppear", "note": "`.onAppear(perform:)`, iOS 13.0. Apple: \"Adds an action to perform before this view appears.\""},
        {"name": "onAssignedDocumentDidSubmit", "note": "`.onAssignedDocumentDidSubmit(_:)`, iOS 26.4. Apple: \"Adds an action to perform after submitting an assigned document.\""},
        {"name": "onAssignedDocumentDidWithdraw", "note": "`.onAssignedDocumentDidWithdraw(_:)`, iOS 26.4. Apple: \"Adds an action to perform after an assigned document submission has been withdrawn.\""},
        {"name": "onAssignedDocumentWillSubmit", "note": "`.onAssignedDocumentWillSubmit(_:)`, iOS 26.4. Apple: \"Adds an action to perform before submitting an assigned document.\""},
        {"name": "onAssignedDocumentWillWithdraw", "note": "`.onAssignedDocumentWillWithdraw(_:)`, iOS 26.4. Apple: \"Adds an action to perform before withdrawing an assigned document submission.\""},
        {"name": "onCameraCaptureEvent", "note": "`.onCameraCaptureEvent(isEnabled:action:)`, iOS 18.0. Apple: \"Used to register an action triggered by system capture events.\""},
        {"name": "onChange", "note": "`.onChange(of:initial:_:)`, iOS 17.0. Apple: \"Adds a modifier for this view that fires an action when a specific value changes.\""},
        {"name": "onContinueUserActivity", "note": "`.onContinueUserActivity(_:perform:)`, iOS 14.0. Apple: \"Registers a handler to invoke in response to a user activity that your app receives.\""},
        {"name": "onDisappear", "note": "`.onDisappear(perform:)`, iOS 13.0. Apple: \"Adds an action to perform after this view disappears.\""},
        {"name": "onGeometryChange", "note": "`.onGeometryChange(for:of:action:)`, iOS 16.0. Apple: \"Adds an action to be performed when a value, created from a geometry proxy, changes.\""},
        {"name": "onGeometryChange3D", "note": "`.onGeometryChange3D(for:of:action:)`, not on iOS. Apple: \"Returns a new view that arranges to call `action(value)` whenever the value computed by `transform(proxy)` changes, where `proxy` provides access to the view’s 3D geometry properties.\"", "status": "unavailable-ios", "replacement": "onGeometryChange"},
        {"name": "onHingeChange", "note": "`.onHingeChange(isEnabled:_:)`, iOS 27.1. Apple: \"Adds an action to perform when the hinge context of the view hierarchy changes.\""},
        {"name": "onImmersionChange", "note": "`.onImmersionChange(initial:_:)`, not on iOS. Apple: \"Performs an action when the immersion state of your app changes.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "onInteractiveResizeChange", "note": "`.onInteractiveResizeChange(_:)`, iOS 26.0. Apple: \"Adds an action to perform when the enclosing window is being interactively resized.\""},
        {"name": "onOpenURL", "note": "`.onOpenURL(perform:)`, iOS 14.0. Apple: \"Registers a handler to invoke in response to a URL that your app receives.\""},
        {"name": "onReceive", "note": "`.onReceive(_:perform:)`, iOS 13.0. Apple: \"Adds an action to perform when this view detects data emitted by the given publisher.\""},
        {"name": "onVolumeViewpointChange", "note": "`.onVolumeViewpointChange(updateStrategy:initial:_:)`, not on iOS. Apple: \"Adds an action to perform when the viewpoint of the volume changes.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "onWorldRecenter", "note": "`.onWorldRecenter(action:)`, not on iOS. Apple: \"Adds an action to perform when recentering the view with the digital crown.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "supportedVolumeViewpoints", "note": "`.supportedVolumeViewpoints(_:)`, not on iOS. Apple: \"Specifies which viewpoints are supported for the window bar and ornaments in a volume.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "task", "note": "`.task(id:name:priority:file:line:_:)`, iOS 15.0. Apple: \"Adds a task to perform before this view appears or when a specified value changes.\""},
        {"name": "userActivity", "note": "`.userActivity(_:element:_:)`, iOS 14.0. Apple: \"Advertises a user activity type.\""}
      ]
    }
  }
};
