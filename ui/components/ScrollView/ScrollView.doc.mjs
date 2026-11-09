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
        {"name": "scrollEdgeEffectHidden", "note": "`.scrollEdgeEffectHidden(_:for:)`, iOS 26.0. Apple: \"Hides any scroll edge effects for scroll views within this hierarchy.\""},
        {"name": "scrollEdgeEffectStyle", "note": "`.scrollEdgeEffectStyle(_:for:)`, iOS 26.0. Apple: \"Configures the scroll edge effect style for scroll views within this hierarchy.\""}
      ]
    }
  }
};
