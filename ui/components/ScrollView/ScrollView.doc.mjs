/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ScrollView",
  "displayName": "ScrollView",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.ScrollView",
    "web": null
  },
  "group": "ScrollView",
  "category": "Layout",
  "keywords": [
    "scroll",
    "scrollable",
    "overflow",
    "long content"
  ],
  "usage": {
    "description": "ScrollView lets people move content that is bigger than the screen. Apple: \"A scrollable view.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Show part of the next item at the edge, so people see there is more."
      },
      {
        "guidance": false,
        "description": "Put a scroll view inside another one that scrolls the same way."
      },
      {
        "guidance": false,
        "description": "Build your own scrolling. People expect the system feel."
      }
    ],
    "accessibility": [
      {
        "name": "Scroll by assistive tech",
        "category": "Keyboard",
        "criterion": "2.1.1 Keyboard",
        "requirement": "reachable",
        "description": "VoiceOver and Full Keyboard Access scroll it with no extra code."
      }
    ],
    "anatomy": [
      {
        "name": "Content",
        "required": true,
        "description": "What scrolls."
      },
      {
        "name": "Indicators",
        "required": false,
        "description": "The scroll bars."
      }
    ]
  },
  "props": [
    {
      "name": "axes",
      "type": "'vertical' | 'horizontal'",
      "description": "Which way it scrolls. init(_:content:).",
      "default": "'vertical'"
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "What scrolls.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "ScrollViewReader", "note": "iOS 14.0. Apple: \"A view that provides programmatic scrolling, by working with a proxy to scroll to known child views.\""},
        {"name": "defaultScrollAnchor", "note": "`.defaultScrollAnchor(_:)`, iOS 17.0. Apple: \"Associates an anchor to control which part of the scroll view’s content should be rendered by default.\""},
        {"name": "onScrollGeometryChange", "note": "`.onScrollGeometryChange(for:of:action:)`, iOS 18.0. Apple: \"Adds an action to be performed when a value, created from a scroll geometry, changes.\""},
        {"name": "onScrollPhaseChange", "note": "`.onScrollPhaseChange(_:)`, iOS 18.0. Apple: \"Adds an action to perform when the scroll phase of the first scroll view in the hierarchy changes.\""},
        {"name": "onScrollTargetVisibilityChange", "note": "`.onScrollTargetVisibilityChange(idType:threshold:_:)`, iOS 18.0. Apple: \"Adds an action to be called with information about what views would be considered visible.\""},
        {"name": "onScrollVisibilityChange", "note": "`.onScrollVisibilityChange(threshold:_:)`, iOS 18.0. Apple: \"Adds an action to be called when the view crosses the threshold to be considered on/off screen.\""},
        {"name": "scrollInputBehavior", "note": "`.scrollInputBehavior(_:for:)`, iOS 18.0. Apple: \"Enables or disables scrolling in scrollable views when using particular inputs.\""},
        {"name": "scrollPosition", "note": "`.scrollPosition(id:anchor:)`, iOS 17.0. Apple: \"Associates a binding to be updated when a scroll view within this view scrolls.\""},
        {"name": "scrollTargetBehavior", "note": "`.scrollTargetBehavior(_:)`, iOS 17.0. Apple: \"Sets the scroll behavior of views scrollable in the provided axes.\""},
        {"name": "scrollTargetLayout", "note": "`.scrollTargetLayout(isEnabled:)`, iOS 17.0. Apple: \"Configures the outermost layout as a scroll target layout.\""},
        {"name": "scrollTransition", "note": "`.scrollTransition(_:axis:transition:)`, iOS 17.0. Apple: \"Applies the given transition, animating between the phases of the transition as this view appears and disappears within the visible region of the containing scroll view.\""},
        {"name": "scrollBounceBehavior", "note": "`.scrollBounceBehavior(_:axes:)`, iOS 16.4. Apple: \"Configures the bounce behavior of scrollable views along the specified axis.\""},
        {"name": "scrollClipDisabled", "note": "`.scrollClipDisabled(_:)`, iOS 17.0. Apple: \"Sets whether a scroll view clips its content to its bounds.\""},
        {"name": "scrollContentBackground", "note": "`.scrollContentBackground(_:)`, iOS 16.0. Apple: \"Specifies the visibility of the background for scrollable views within this view.\""},
        {"name": "scrollDisabled", "note": "`.scrollDisabled(_:)`, iOS 16.0. Apple: \"Disables or enables scrolling in scrollable views.\""},
        {"name": "scrollIndicators", "note": "`.scrollIndicators(_:axes:)`, iOS 16.0. Apple: \"Sets the visibility of scroll indicators within this view.\""},
        {"name": "scrollIndicatorsFlash", "note": "`.scrollIndicatorsFlash(onAppear:)`, iOS 17.0. Apple: \"Flashes the scroll indicators of a scrollable view when it appears.\""}
      ]
    }
  }
};
