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
