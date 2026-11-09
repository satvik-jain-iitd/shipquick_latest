/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "PageControl",
  "displayName": "PageControl",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.PageTabViewStyle",
    "web": null
  },
  "group": "PageControl",
  "category": "Navigation",
  "keywords": [
    "page",
    "dots",
    "pager",
    "carousel",
    "onboarding"
  ],
  "usage": {
    "description": "A page control is the row of dots under swipeable pages. In SwiftUI it is a TabView with the page style. Apple: \"A TabViewStyle that displays a paged scrolling TabView.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it for an ordered set of pages, like onboarding. Center the dots near the bottom."
      },
      {
        "guidance": false,
        "description": "Show more than about 10 dots. Use a grid instead."
      },
      {
        "guidance": false,
        "description": "Use it for pages that are not in order. Use a sidebar or a split view."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "VoiceOver reads the page number and the count."
      }
    ],
    "anatomy": [
      {
        "name": "Pages",
        "required": true,
        "description": "The views people swipe between."
      },
      {
        "name": "Dots",
        "required": true,
        "description": "The page indicators; the current one is highlighted."
      }
    ]
  },
  "props": [
    {
      "name": "indexDisplayMode",
      "type": "'automatic' | 'always' | 'never'",
      "description": "When the dots show. automatic: when there is more than one page.",
      "default": "'automatic'"
    },
    {
      "name": "selection",
      "type": "Binding<Hashable>",
      "description": "The current page, kept by the screen. TabView(selection:content:)."
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "The pages.",
      "required": true
    }
  ]
};
