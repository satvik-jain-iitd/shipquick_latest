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
        {"name": "allowedDynamicRange", "note": "`.allowedDynamicRange(_:)`, iOS 17.0. Apple: \"Returns a new view configured with the specified allowed dynamic range.\""},
        {"name": "background", "note": "`.background(alignment:content:)`, iOS 15.0. Apple: \"Layers the views that you specify behind this view.\""},
        {"name": "backgroundExtensionEffect", "note": "`.backgroundExtensionEffect()`, iOS 26.0. Apple: \"Adds the background extension effect to the view. The view will be duplicated into mirrored copies which will be placed around the view on any edge with available safe area. Additionally, a blur effect will be applied on top to blur out the copies.\""},
        {"name": "backgroundStyle", "note": "`.backgroundStyle(_:)`, iOS 16.0. Apple: \"Sets the specified style to render backgrounds within the view.\""},
        {"name": "border", "note": "`.border(_:width:)`, iOS 13.0. Apple: \"Adds a border to this view with the specified style and width.\""},
        {"name": "controlSize", "note": "`.controlSize(_:)`, iOS 15.0. Apple: \"Sets the size for controls within this view.\""},
        {"name": "dynamicIsland", "note": "`.dynamicIsland(verticalPlacement:)`, iOS 16.1. Apple: \"Specifies the vertical placement for a view of an expanded Live Activity that appears in the Dynamic Island.\""},
        {"name": "foregroundStyle", "note": "`.foregroundStyle(_:)`, iOS 15.0. Apple: \"Sets a view’s foreground elements to use a given style.\""},
        {"name": "hidden", "note": "`.hidden()`, iOS 13.0. Apple: \"Hides this view unconditionally.\""},
        {"name": "labelsHidden", "note": "`.labelsHidden()`, iOS 13.0. Apple: \"Hides the labels of any controls contained within this view.\""},
        {"name": "labelsVisibility", "note": "`.labelsVisibility(_:)`, iOS 18.0. Apple: \"Controls the visibility of labels of any controls contained within this view.\""},
        {"name": "overlay", "note": "`.overlay(alignment:content:)`, iOS 15.0. Apple: \"Layers the views that you specify in front of this view.\""},
        {"name": "persistentSystemOverlays", "note": "`.persistentSystemOverlays(_:)`, iOS 16.0. Apple: \"Sets the preferred visibility of the non-transient system views overlaying the app.\""},
        {"name": "preferredColorScheme", "note": "`.preferredColorScheme(_:)`, iOS 13.0. Apple: \"Sets the preferred color scheme for this presentation.\""},
        {"name": "sensoryFeedback", "note": "`.sensoryFeedback(_:trigger:)`, iOS 17.0. Apple: \"Plays the specified `feedback` when the provided `trigger` value changes.\""},
        {"name": "tint", "note": "`.tint(_:)`, iOS 15.0. Apple: \"Sets the tint color within this view.\""},
        {"name": "accentColor", "note": "`.accentColor(_:)`, iOS 13.0. Apple: \"Sets the accent color for this view and the views it contains.\"", "status": "deprecated", "replacement": "the"},
        {"name": "colorScheme", "note": "`.colorScheme(_:)`, iOS 13.0. Apple: \"Sets this view’s color scheme.\"", "status": "deprecated", "replacement": "preferredColorScheme"},
        {"name": "complicationForeground", "note": "`.complicationForeground()`, not on iOS. Apple: \"Promotes this view to the foreground in a complication.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a watchOS complication; iOS has no complications)"},
        {"name": "foregroundColor", "note": "`.foregroundColor(_:)`, iOS 13.0. Apple: \"Sets the color of the foreground elements displayed by this view.\"", "status": "deprecated", "replacement": "foregroundStyle"},
        {"name": "statusBar", "note": "`.statusBar(hidden:)`, iOS 13.0. Apple: \"Sets the visibility of the status bar.\"", "status": "deprecated", "replacement": "statusBarHidden"},
        {"name": "statusBarHidden", "note": "`.statusBarHidden(_:)`, iOS 13.0. Apple: \"Sets the visibility of the status bar.\"", "status": "deprecated", "replacement": "toolbarVisibility"},
        {"name": "Color", "note": "iOS 13.0. Apple: \"A representation of a color that adapts to a given context.\""}
      ]
    }
  }
};
