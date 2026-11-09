/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/search-bar (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SearchBar",
  "displayName": "Search bar",
  "platforms": {
    "android": "androidx.compose.material3.SearchBar",
    "ios": "SwiftUI.View.searchable(text:placement:prompt:)",
    "web": null
  },
  "platformUsage": {
    "android": {
      "description": "The search bar stays on screen. Use it when search is the main job of the app. Google marks SearchBar as experimental.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use SearchBarDefaults.InputField for the field."
        },
        {
          "guidance": true,
          "description": "Show suggestions or results in its content when it is expanded."
        }
      ],
      "accessibility": [
        {
          "name": "Icon name",
          "category": "Semantics",
          "criterion": "1.1.1 Non-text Content",
          "requirement": "contentDescription",
          "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
        }
      ]
    },
    "ios": {
      "description": "On iOS, add searchable(text:placement:prompt:) to the view inside a navigation container. Apple: \"Marks this view as searchable, which configures the display of a search field.\" The system places the field, often in the navigation bar.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Bind text to a String held in @State and filter the results as the user types."
        },
        {
          "guidance": true,
          "description": "Set a prompt that says what can be found, like \"Search recipes\" (Apple HIG, Search fields)."
        },
        {
          "guidance": true,
          "description": "Offer suggestions with searchSuggestions(_:)."
        }
      ],
      "accessibility": []
    }
  },
  "group": "Search",
  "category": "Data Input",
  "keywords": [
    "search",
    "find",
    "query",
    "filter"
  ],
  "usage": {
    "description": "A search field lets the user type words to find results in the app.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Use a plain text field when search is the main job."
      }
    ],
    "accessibility": [
      {
        "name": "Label",
        "category": "Content",
        "criterion": "3.3.2 Labels or Instructions",
        "requirement": "visible label",
        "description": "Every input has words that say what to enter. A placeholder alone is not a label."
      }
    ],
    "anatomy": [
      {
        "name": "Input field",
        "required": true,
        "description": "Where the user types."
      },
      {
        "name": "Leading icon",
        "required": false,
        "description": "Search or back."
      },
      {
        "name": "Results",
        "required": false,
        "description": "Shows when it is expanded."
      }
    ]
  },
  "props": [
    {
      "name": "inputField",
      "type": "@Composable () -> Unit",
      "description": "The field, usually SearchBarDefaults.InputField with query and onQueryChange.",
      "required": true
    },
    {
      "name": "expanded",
      "type": "boolean",
      "description": "True when results show below the field.",
      "required": true
    },
    {
      "name": "onExpandedChange",
      "type": "(expanded: boolean) => void",
      "description": "Runs with the new expanded value.",
      "required": true
    },
    {
      "name": "content",
      "type": "@Composable ColumnScope.() -> Unit",
      "description": "The results or suggestions.",
      "required": true
    },
    {
      "name": "text",
      "type": "Binding<String>",
      "description": "The words in the field.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "placement",
      "type": "SearchFieldPlacement",
      "description": "Where the field sits, like .navigationBarDrawer or .toolbar.",
      "platform": "ios",
      "default": ".automatic"
    },
    {
      "name": "prompt",
      "type": "Text?",
      "description": "The hint while the field is empty.",
      "platform": "ios",
      "default": "nil"
    }
  ]
};
