/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/lists (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "List",
  "displayName": "List",
  "platforms": {
    "android": "androidx.compose.material3.ListItem",
    "ios": "SwiftUI.List",
    "web": "@astryxdesign/core/List"
  },
  "platformUsage": {
    "android": {
      "description": "For a long list or one of unknown length, use LazyColumn (a layout container): it only builds the rows on screen. Build each row with ListItem.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use LazyColumn or LazyRow for long lists."
        },
        {
          "guidance": false,
          "description": "Put a long list in a plain Column. It builds every row at once."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on a clickable row only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS, List shows rows of data in one scrolling column and only builds the rows on screen. listStyle(_:) sets the look, like .insetGrouped or .plain.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Pass the data with an id, like List(items, id: \\.id) { item in ... }."
        },
        {
          "guidance": true,
          "description": "Bind selection when the user can pick rows."
        },
        {
          "guidance": false,
          "description": "Put a long list in a ScrollView with a VStack. Use List."
        }
      ],
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
  },
  "group": "List",
  "category": "Table & List",
  "keywords": [
    "list",
    "row",
    "item",
    "lazy",
    "recycler"
  ],
  "usage": {
    "description": "A list shows a set of items.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Give each item a stable key."
      }
    ],
    "accessibility": [
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its fill. The colours come from the tokens, never typed in."
      }
    ],
    "anatomy": [
      {
        "name": "Leading",
        "required": false,
        "description": "An icon or a picture."
      },
      {
        "name": "Headline",
        "required": true,
        "description": "The main words."
      },
      {
        "name": "Supporting",
        "required": false,
        "description": "A second line."
      },
      {
        "name": "Trailing",
        "required": false,
        "description": "Meta text or a control."
      }
    ]
  },
  "props": [
    {
      "name": "headlineContent",
      "type": "@Composable () -> Unit",
      "description": "The main line of the row.",
      "required": true
    },
    {
      "name": "overlineContent",
      "type": "@Composable () -> Unit",
      "description": "A small line above."
    },
    {
      "name": "supportingContent",
      "type": "@Composable () -> Unit",
      "description": "A line below."
    },
    {
      "name": "leadingContent",
      "type": "@Composable () -> Unit",
      "description": "At the start, like an icon."
    },
    {
      "name": "trailingContent",
      "type": "@Composable () -> Unit",
      "description": "At the end, like a switch."
    },
    {
      "name": "data",
      "type": "RandomAccessCollection",
      "description": "The items, one row each.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "id",
      "type": "KeyPath<Data.Element, ID>",
      "description": "The stable id of each item.",
      "platform": "ios"
    },
    {
      "name": "rowContent",
      "type": "(Data.Element) -> some View",
      "description": "Builds one row from one item.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "selection",
      "type": "Binding<SelectionValue?>?",
      "description": "The picked row, when rows can be picked.",
      "platform": "ios",
      "default": "nil"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "deleteDisabled", "note": "`.deleteDisabled(_:)`, iOS 13.0. Apple: \"Adds a condition for whether the view’s view hierarchy is deletable.\""},
        {"name": "listRowHoverEffect", "note": "`.listRowHoverEffect(_:)`, not on iOS. Apple: \"Requests that the containing list row use the provided hover effect.\"", "status": "unavailable-ios", "replacement": "hoverEffect"},
        {"name": "listRowHoverEffectDisabled", "note": "`.listRowHoverEffectDisabled(_:)`, not on iOS. Apple: \"Requests that the containing list row have its hover effect disabled.\"", "status": "unavailable-ios", "replacement": "hoverEffectDisabled"},
        {"name": "moveDisabled", "note": "`.moveDisabled(_:)`, iOS 13.0. Apple: \"Adds a condition for whether the view’s view hierarchy is movable.\""},
        {"name": "refreshable", "note": "`.refreshable(action:)`, iOS 15.0. Apple: \"Adds an asynchronous handler that can update the data the view displays when a person initiates a request, such as by pulling to refresh.\""},
        {"name": "selectionDisabled", "note": "`.selectionDisabled(_:)`, iOS 17.0. Apple: \"Adds a condition that controls whether users can select this view.\""},
        {"name": "swipeActions", "note": "`.swipeActions(edge:allowsFullSwipe:content:)`, iOS 15.0. Apple: \"Adds custom swipe actions to a row in a list.\""},
        {"name": "swipeActionsContainer", "note": "`.swipeActionsContainer()`, iOS 27.0. Apple: \"Coordinates swipe action dismissal and mutual exclusion across rows in a container.\""}
      ]
    }
  }
};
