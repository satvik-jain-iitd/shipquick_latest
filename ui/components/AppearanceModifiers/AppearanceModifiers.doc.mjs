/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "AppearanceModifiers",
  "displayName": "Appearance modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "AppearanceModifiers",
  "category": "Utility",
  "keywords": [
    "background",
    "foreground style",
    "tint",
    "hidden",
    "redacted",
    "color scheme"
  ],
  "usage": {
    "description": "Modifiers that change how a view looks: its colors, its background, or if it shows. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Take colors from the tokens in design/tokens.json."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Appearance modifiers",
      "variants": [
        {"name": "accessoryWidgetGroupStyle", "note": "`.accessoryWidgetGroupStyle(_:)`, not on iOS. Apple: \"The view modifier that can be applied to `AccessoryWidgetGroup` to specify the shape the three content views will be masked with. The value of `style` is set to `.automatic`, which is `.circular` by default.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a watchOS accessory widget group; build iOS widgets with WidgetKit)"},
        {"name": "allowedDynamicRange", "note": "`.allowedDynamicRange(_:)`, iOS 17.0. Apple: \"Returns a new view configured with the specified allowed dynamic range.\""},
        {"name": "background", "note": "`.background(alignment:content:)`, iOS 15.0. Apple: \"Layers the views that you specify behind this view.\""},
        {"name": "backgroundExtensionEffect", "note": "`.backgroundExtensionEffect()`, iOS 26.0. Apple: \"Adds the background extension effect to the view. The view will be duplicated into mirrored copies which will be placed around the view on any edge with available safe area. Additionally, a blur effect will be applied on top to blur out the copies.\""},
        {"name": "backgroundStyle", "note": "`.backgroundStyle(_:)`, iOS 16.0. Apple: \"Sets the specified style to render backgrounds within the view.\""},
        {"name": "border", "note": "`.border(_:width:)`, iOS 13.0. Apple: \"Adds a border to this view with the specified style and width.\""},
        {"name": "breakthroughEffect", "note": "`.breakthroughEffect(_:)`, not on iOS. Apple: \"Ensures that the view is always visible to the user, even when other content is occluding it, like 3D models.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS content seen through 3D models; iOS has no 3D occlusion)"},
        {"name": "containerBackground", "note": "`.containerBackground(_:for:)`, iOS 17.0. Apple: \"Sets the container background of the enclosing container using a view.\""},
        {"name": "contentCaptureProtected", "note": "`.contentCaptureProtected(_:)`, not on iOS. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contentcaptureprotected(_:)", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS 26 only, Apple's page names no iOS twin)"},
        {"name": "controlSize", "note": "`.controlSize(_:)`, iOS 15.0. Apple: \"Sets the size for controls within this view.\""},
        {"name": "controlWidgetActionHint", "note": "`.controlWidgetActionHint(_:)`, iOS 18.0. Apple: \"The action hint of the control described by the modified label.\""},
        {"name": "controlWidgetStatus", "note": "`.controlWidgetStatus(_:)`, iOS 18.0. Apple: \"The status of the control described by the modified label.\""},
        {"name": "dynamicIsland", "note": "`.dynamicIsland(verticalPlacement:)`, iOS 16.1. Apple: \"Specifies the vertical placement for a view of an expanded Live Activity that appears in the Dynamic Island.\""},
        {"name": "foregroundStyle", "note": "`.foregroundStyle(_:)`, iOS 15.0. Apple: \"Sets a view’s foreground elements to use a given style.\""},
        {"name": "hidden", "note": "`.hidden()`, iOS 13.0. Apple: \"Hides this view unconditionally.\""},
        {"name": "invalidatableContent", "note": "`.invalidatableContent(_:)`, iOS 17.0. Apple: \"Mark the receiver as their content might be invalidated.\""},
        {"name": "labelsHidden", "note": "`.labelsHidden()`, iOS 13.0. Apple: \"Hides the labels of any controls contained within this view.\""},
        {"name": "labelsVisibility", "note": "`.labelsVisibility(_:)`, iOS 18.0. Apple: \"Controls the visibility of labels of any controls contained within this view.\""},
        {"name": "overlay", "note": "`.overlay(alignment:content:)`, iOS 15.0. Apple: \"Layers the views that you specify in front of this view.\""},
        {"name": "persistentSystemOverlays", "note": "`.persistentSystemOverlays(_:)`, iOS 16.0. Apple: \"Sets the preferred visibility of the non-transient system views overlaying the app.\""},
        {"name": "preferredColorScheme", "note": "`.preferredColorScheme(_:)`, iOS 13.0. Apple: \"Sets the preferred color scheme for this presentation.\""},
        {"name": "preferredSurroundingsEffect", "note": "`.preferredSurroundingsEffect(_:)`, not on iOS. Apple: \"Applies an effect to passthrough video.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it tints visionOS passthrough video; iOS has no passthrough)"},
        {"name": "preferredWindowClippingMargins", "note": "`.preferredWindowClippingMargins(_:_:)`, not on iOS. Apple: \"Requests additional margins for drawing beyond the bounds of the window.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (drawing past a visionOS window's bounds)"},
        {"name": "privacySensitive", "note": "`.privacySensitive(_:)`, iOS 15.0. Apple: \"Marks the view as containing sensitive, private user data.\""},
        {"name": "redacted", "note": "`.redacted(reason:)`, iOS 14.0. Apple: \"Adds a reason to apply a redaction to this view hierarchy.\""},
        {"name": "sensoryFeedback", "note": "`.sensoryFeedback(_:trigger:)`, iOS 17.0. Apple: \"Plays the specified `feedback` when the provided `trigger` value changes.\""},
        {"name": "spatialOverlay", "note": "`.spatialOverlay(alignment:content:)`, not on iOS. Apple: \"Adds secondary views within the 3D bounds of this view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "spatialOverlayPreferenceValue", "note": "`.spatialOverlayPreferenceValue(_:alignment:_:)`, not on iOS. Apple: \"Uses the specified preference value from the view to produce another view occupying the same 3D space of the first view.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "tint", "note": "`.tint(_:)`, iOS 15.0. Apple: \"Sets the tint color within this view.\""},
        {"name": "unredacted", "note": "`.unredacted()`, iOS 14.0. Apple: \"Removes any reason to apply a redaction to this view hierarchy.\""},
        {"name": "upperLimbVisibility", "note": "`.upperLimbVisibility(_:)`, not on iOS. Apple: \"Sets the preferred visibility of the user’s upper limbs, while an `ImmersiveSpace` scene is presented.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (the person's arms in a visionOS immersive space)"},
        {"name": "volumeBaseplateVisibility", "note": "`.volumeBaseplateVisibility(_:)`, not on iOS. Apple: \"Sets the visibility of the baseplate of a volume, which appears when a user looks towards the ‘floor’ of a volume and during resize. Both `automatic` and `visible` will show the baseplate. `hidden` will never show it.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"},
        {"name": "widgetAccentable", "note": "`.widgetAccentable(_:)`, iOS 16.0. Apple: \"Adds the view and all of its subviews to the accented group.\""},
        {"name": "widgetCurvesContent", "note": "`.widgetCurvesContent(_:)`, iOS 17.0. Apple: \"Displays the widget’s content along a curve if the context allows it.\""},
        {"name": "widgetLabel", "note": "`.widgetLabel(_:)`, iOS 16.0. Apple: \"Returns a localized text label that displays additional content outside the accessory family widget’s main SwiftUI view.\""},
        {"name": "windowDismissBehavior", "note": "`.windowDismissBehavior(_:)`, not on iOS. Apple: \"Configures the dismiss functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowFullScreenBehavior", "note": "`.windowFullScreenBehavior(_:)`, not on iOS. Apple: \"Configures the full screen functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowMinimizeBehavior", "note": "`.windowMinimizeBehavior(_:)`, not on iOS. Apple: \"Configures the minimize functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowResizeAnchor", "note": "`.windowResizeAnchor(_:)`, not on iOS. Apple: \"Sets the window anchor point used when the size of the view changes such that the window must resize.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowResizeBehavior", "note": "`.windowResizeBehavior(_:)`, not on iOS. Apple: \"Configures the resize functionality for the window enclosing `self`.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (it shapes a Mac app window; an iOS app has no such window control)"},
        {"name": "windowToolbarFullScreenVisibility", "note": "`.windowToolbarFullScreenVisibility(_:)`, iOS 18.0. Apple: \"Configures the visibility of the window toolbar when the window enters full screen mode.\""},
        {"name": "accentColor", "note": "`.accentColor(_:)`, iOS 13.0. Apple: \"Sets the accent color for this view and the views it contains.\"", "status": "deprecated", "replacement": "the"},
        {"name": "colorScheme", "note": "`.colorScheme(_:)`, iOS 13.0. Apple: \"Sets this view’s color scheme.\"", "status": "deprecated", "replacement": "preferredColorScheme"},
        {"name": "complicationForeground", "note": "`.complicationForeground()`, not on iOS. Apple: \"Promotes this view to the foreground in a complication.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a watchOS complication; iOS has no complications)"},
        {"name": "foregroundColor", "note": "`.foregroundColor(_:)`, iOS 13.0. Apple: \"Sets the color of the foreground elements displayed by this view.\"", "status": "deprecated", "replacement": "foregroundStyle"},
        {"name": "statusBar", "note": "`.statusBar(hidden:)`, iOS 13.0. Apple: \"Sets the visibility of the status bar.\"", "status": "deprecated", "replacement": "statusBarHidden"}
      ]
    }
  }
};
