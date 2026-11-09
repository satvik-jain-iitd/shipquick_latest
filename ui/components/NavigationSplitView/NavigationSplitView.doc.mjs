/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "NavigationSplitView",
  "displayName": "NavigationSplitView",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.NavigationSplitView",
    "web": null
  },
  "group": "NavigationSplitView",
  "category": "Navigation",
  "keywords": [
    "split",
    "sidebar",
    "columns",
    "master detail",
    "ipad"
  ],
  "usage": {
    "description": "NavigationSplitView shows two or three columns. A choice in one column shows its content in the next. Apple: \"A view that presents views in two or three columns, where selections in leading columns control presentations in subsequent columns.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it on iPad and wide screens. On iPhone in portrait it folds into one stack."
      },
      {
        "guidance": true,
        "description": "Keep the current choice highlighted in each column, so people know where they are."
      },
      {
        "guidance": false,
        "description": "Use it for a flow of steps. Use a NavigationStack."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "Each column is read in order, sidebar first."
      }
    ],
    "anatomy": [
      {
        "name": "Sidebar",
        "required": true,
        "description": "The first column, the top-level choices."
      },
      {
        "name": "Content",
        "required": false,
        "description": "An optional middle column."
      },
      {
        "name": "Detail",
        "required": true,
        "description": "The last column, the chosen item."
      }
    ]
  },
  "props": [
    {
      "name": "sidebar",
      "type": "() -> some View",
      "description": "The first column.",
      "required": true
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "The middle column, for three columns. init(sidebar:content:detail:)."
    },
    {
      "name": "detail",
      "type": "() -> some View",
      "description": "The last column.",
      "required": true
    },
    {
      "name": "columnVisibility",
      "type": "Binding<NavigationSplitViewVisibility>",
      "description": "Which columns show, kept by the screen."
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "navigationSplitViewStyle", "note": "`.navigationSplitViewStyle(_:)`, iOS 16.0. Apple: \"Sets the style for navigation split views within this view.\""}
      ]
    }
  }
};
