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
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "searchable", "note": "`.searchable(text:placement:prompt:)`, iOS 16.0. Apple: \"Marks this view as searchable, which configures the display of a search field.\""},
        {"name": "searchCompletion", "note": "`.searchCompletion(_:)`, iOS 15.0. Apple: \"Associates a fully formed string with the value of this view when used as a search suggestion.\""},
        {"name": "searchDictationBehavior", "note": "`.searchDictationBehavior(_:)`, iOS 17.0. Apple: \"Configures the dictation behavior for any search fields configured by the searchable modifier.\""},
        {"name": "searchPresentationToolbarBehavior", "note": "`.searchPresentationToolbarBehavior(_:)`, iOS 17.1. Apple: \"Configures the search toolbar presentation behavior for any searchable modifiers within this view.\""},
        {"name": "searchScopes", "note": "`.searchScopes(_:scopes:)`, iOS 16.0. Apple: \"Configures the search scopes for this view.\""},
        {"name": "searchSelection", "note": "`.searchSelection(_:)`, iOS 26.0. Apple: \"Binds the selection of the search field associated with the nearest searchable modifier to the given `TextSelection` value.\""},
        {"name": "searchSuggestions", "note": "`.searchSuggestions(_:)`, iOS 16.0. Apple: \"Configures the search suggestions for this view.\""},
        {"name": "searchToolbarBehavior", "note": "`.searchToolbarBehavior(_:)`, iOS 26.0. Apple: \"Configures the behavior for search in the toolbar.\""},
        {"name": "searchFocused", "note": "`.searchFocused(_:)`, iOS 18.0. Apple: \"Modifies this view by binding the focus state of the search field associated with the nearest searchable modifier to the given Boolean value.\""}
      ]
    },
    "android": {
      "variants": [
        {
          "name": "SearchBarDefaults.InputField",
          "note": "The text field of a search bar: query, onSearch, and leading and trailing icons. Pass it as the bar's inputField."
        },
        {
          "name": "TopSearchBar",
          "note": "A search bar at the top of the screen that can scroll away with the content. Pass a SearchBarScrollBehavior."
        },
        {
          "name": "ExpandedFullScreenSearchBar",
          "note": "The full-screen view a SearchBar opens into, with the results. Use it on phones."
        },
        {
          "name": "DockedSearchBar",
          "note": "A search bar whose results open in a box under it, not over the whole screen. Use it on tablets and wide screens."
        },
        {
          "name": "ExpandedDockedSearchBar",
          "note": "The box under a search bar that shows results, for wide screens. It goes with a collapsed SearchBar and the same SearchBarState."
        }
      ],
      "supporting": [
        {
          "name": "SearchBarState",
          "use": "Says if the bar is collapsed or expanded. Call animateToExpanded(), animateToCollapsed() or snapTo() from a coroutine."
        },
        {
          "name": "rememberSearchBarState",
          "use": "Creates and keeps a SearchBarState across recompositions."
        },
        {
          "name": "SearchBarValue",
          "use": "The two states of a search bar: Collapsed and Expanded."
        },
        {
          "name": "SearchBarScrollBehavior",
          "use": "Links a TopSearchBar to a scrolling list, so the bar scrolls away and back. Make one with SearchBarDefaults.enterAlwaysSearchBarScrollBehavior()."
        },
        {
          "name": "SearchBarDefaults",
          "use": "Default colours, shapes, elevation, window insets, the InputField and the scroll behaviour for search bars."
        },
        {
          "name": "SearchBarColors",
          "use": "The container, divider and input field colours of a search bar. Make one with SearchBarDefaults.colors()."
        }
      ]
    }
  }
};
