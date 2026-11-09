/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/search-bar (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "SearchBar",
  "displayName": "Search bar",
  "platforms": {
    "android": "androidx.compose.material3.SearchBar",
    "ios": null,
    "web": null
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
    "description": "A search bar is a search field that stays on screen. The user types words to find results in the app. Use it when search is the main job of the app. Google marks SearchBar as experimental.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use SearchBarDefaults.InputField for the field."
      },
      {
        "guidance": true,
        "description": "Show suggestions or results in its content when it is expanded."
      },
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
      },
      {
        "name": "Icon name",
        "category": "Semantics",
        "criterion": "1.1.1 Non-text Content",
        "requirement": "contentDescription",
        "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
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
    }
  ]
};
