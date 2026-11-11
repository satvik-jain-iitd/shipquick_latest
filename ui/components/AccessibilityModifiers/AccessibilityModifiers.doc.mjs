/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "AccessibilityModifiers",
  "displayName": "Accessibility modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "AccessibilityModifiers",
  "category": "Utility",
  "keywords": [
    "accessibility",
    "voiceover",
    "label",
    "hint",
    "traits",
    "rotor"
  ],
  "usage": {
    "description": "Modifiers that tell VoiceOver and other assistive tools what a view is and does. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Give every control a spoken name. Most library controls already have one."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Accessibility modifiers",
      "variants": [
        {"name": "accessibilityActivationPoint", "note": "`.accessibilityActivationPoint(_:)`, iOS 14.0. Apple: \"The activation point for an element is the location assistive technologies use to initiate gestures.\""},
        {"name": "accessibilityAddTraits", "note": "`.accessibilityAddTraits(_:)`, iOS 14.0. Apple: \"Adds the given traits to the view.\""},
        {"name": "accessibilityChartDescriptor", "note": "`.accessibilityChartDescriptor(_:)`, iOS 15.0. Apple: \"Adds a descriptor to a View that represents a chart to make the chart’s contents accessible to all users.\""},
        {"name": "accessibilityChildren", "note": "`.accessibilityChildren(children:)`, iOS 15.0. Apple: \"Replaces the existing accessibility element’s children with one or more new synthetic accessibility elements.\""},
        {"name": "accessibilityCustomContent", "note": "`.accessibilityCustomContent(_:_:importance:)`, iOS 16.0. Apple: \"Add additional accessibility information to the view.\""},
        {"name": "accessibilityDirectTouch", "note": "`.accessibilityDirectTouch(_:options:)`, iOS 17.0. Apple: \"Explicitly set whether this accessibility element is a direct touch area. Direct touch areas passthrough touch events to the app rather than being handled through an assistive technology, such as VoiceOver. The modifier accepts an optional `AccessibilityDirectTouchOptions` option set to customize the functionality of the direct touch area.\""},
        {"name": "accessibilityElement", "note": "`.accessibilityElement(children:)`, iOS 13.0. Apple: \"Creates a new accessibility element, or modifies the `AccessibilityChildBehavior` of the existing accessibility element.\""},
        {"name": "accessibilityHeading", "note": "`.accessibilityHeading(_:)`, iOS 15.0. Apple: \"Sets the accessibility level of this heading.\""},
        {"name": "accessibilityHidden", "note": "`.accessibilityHidden(_:)`, iOS 14.0. Apple: \"Specifies whether to hide this view from system accessibility features.\""},
        {"name": "accessibilityHint", "note": "`.accessibilityHint(_:)`, iOS 16.0. Apple: \"Communicates to the user what happens after performing the view’s action.\""},
        {"name": "accessibilityIdentifier", "note": "`.accessibilityIdentifier(_:)`, iOS 14.0. Apple: \"Uses the string you specify to identify the view.\""},
        {"name": "accessibilityIgnoresInvertColors", "note": "`.accessibilityIgnoresInvertColors(_:)`, iOS 14.0. Apple: \"Sets whether this view should ignore the system Smart Invert setting.\""},
        {"name": "accessibilityInputLabels", "note": "`.accessibilityInputLabels(_:)`, iOS 14.0. Apple: \"Sets alternate input labels with which users identify a view.\""},
        {"name": "accessibilityLabel", "note": "`.accessibilityLabel(_:)`, iOS 16.0. Apple: \"Adds a label to the view that describes its contents.\""},
        {"name": "accessibilityLabeledPair", "note": "`.accessibilityLabeledPair(role:id:in:)`, iOS 14.0. Apple: \"Pairs an accessibility element representing a label with the element for the matching content.\""},
        {"name": "accessibilityLinkedGroup", "note": "`.accessibilityLinkedGroup(id:in:)`, iOS 14.0. Apple: \"Links multiple accessibility elements so that the user can quickly navigate from one element to another, even when the elements are not near each other in the accessibility hierarchy.\""},
        {"name": "accessibilityRemoveTraits", "note": "`.accessibilityRemoveTraits(_:)`, iOS 14.0. Apple: \"Removes the given traits from this view.\""},
        {"name": "accessibilityRepresentation", "note": "`.accessibilityRepresentation(representation:)`, iOS 15.0. Apple: \"Replaces one or more accessibility elements for this view with new accessibility elements.\""},
        {"name": "accessibilityRespondsToUserInteraction", "note": "`.accessibilityRespondsToUserInteraction(_:)`, iOS 15.0. Apple: \"Explicitly set whether this Accessibility element responds to user interaction and would thus be interacted with by technologies such as Switch Control, Voice Control or Full Keyboard Access.\""},
        {"name": "accessibilityScrollStatus", "note": "`.accessibilityScrollStatus(_:isEnabled:)`, iOS 26.0. Apple: \"Changes the announcement provided by accessibility technologies when a user scrolls a scroll view within this view.\""},
        {"name": "accessibilityShowsLargeContentViewer", "note": "`.accessibilityShowsLargeContentViewer()`, iOS 15.0. Apple: \"Adds a default large content view to be shown by the large content viewer.\""},
        {"name": "accessibilitySortPriority", "note": "`.accessibilitySortPriority(_:)`, iOS 14.0. Apple: \"Sets the sort priority order for this view’s accessibility element, relative to other elements at the same level.\""},
        {"name": "accessibilityTextContentType", "note": "`.accessibilityTextContentType(_:)`, iOS 15.0. Apple: \"Sets an accessibility text content type.\""},
        {"name": "accessibilityValue", "note": "`.accessibilityValue(_:)`, iOS 16.0. Apple: \"Adds a textual description of the value that the view contains.\""},
        {"name": "assistiveAccessNavigationIcon", "note": "`.assistiveAccessNavigationIcon(_:)`, iOS 26.0. Apple: \"Configures the view’s icon for purposes of navigation.\""},
        {"name": "accessibility", "note": "`.accessibility(label:)`, iOS 13.0. Apple: \"Adds a label to the view that describes its contents.\"", "status": "deprecated", "replacement": "accessibilityLabel"}
      ]
    }
  }
};
