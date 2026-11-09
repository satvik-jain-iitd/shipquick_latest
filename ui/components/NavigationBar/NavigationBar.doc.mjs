/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/navigation-bar (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "NavigationBar",
  "displayName": "Navigation bar",
  "platforms": {
    "android": "androidx.compose.material3.NavigationBar",
    "ios": "SwiftUI.TabView",
    "web": null
  },
  "platformUsage": {
    "android": {
      "description": "Each NavigationBarItem is one place.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use it on compact windows. Use a navigation rail on large ones."
        }
      ],
      "accessibility": [
        {
          "name": "State is read out",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "role and state",
          "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on each item only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS the twin is the tab bar: a TabView with one Tab per place. Apple: Tab is \"the content for a tab and the tab's associated tab item in a tab view.\" Tab needs iOS 18; tabItem(_:) is deprecated.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Bind selection, and give each Tab a value: Tab(\"Home\", systemImage: \"house\", value: .home) { ... }."
        },
        {
          "guidance": true,
          "description": "Keep the tab bar on every screen of a section (Apple HIG, Tab bars)."
        },
        {
          "guidance": false,
          "description": "Use a tab for an action, like writing a message. Tabs are for places."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "Each tab's title is its spoken name, and VoiceOver says which tab is selected."
        },
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
  "group": "Navigation",
  "category": "Navigation",
  "keywords": [
    "navigation bar",
    "bottom navigation",
    "tabs",
    "tab bar"
  ],
  "usage": {
    "description": "A navigation bar at the bottom lets the user switch between the app's main places.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it for three to five places of equal weight."
      },
      {
        "guidance": false,
        "description": "Use it for fewer than three or more than five places."
      }
    ],
    "accessibility": [],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "The bar."
      },
      {
        "name": "Item",
        "required": true,
        "description": "One place: icon, label, selected mark."
      }
    ]
  },
  "props": [
    {
      "name": "content",
      "type": "@Composable RowScope.() -> Unit",
      "description": "The NavigationBarItems.",
      "required": true
    },
    {
      "name": "selected",
      "type": "boolean",
      "description": "NavigationBarItem: true for the place on screen now.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "() => void",
      "description": "NavigationBarItem: runs when the user taps the place. Go there here.",
      "required": true
    },
    {
      "name": "icon",
      "type": "@Composable () -> Unit",
      "description": "NavigationBarItem: the icon for the place.",
      "required": true
    },
    {
      "name": "label",
      "type": "@Composable () -> Unit",
      "description": "NavigationBarItem: the words under the icon."
    },
    {
      "name": "selection",
      "type": "Binding<SelectionValue>",
      "description": "The tab on screen now.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "content",
      "type": "() -> some TabContent",
      "description": "The Tabs.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "Tab: the words under the icon.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "systemImage",
      "type": "String",
      "description": "Tab: the SF Symbol name for the icon.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "value",
      "type": "SelectionValue",
      "description": "Tab: the value selection holds when this tab is on screen.",
      "platform": "ios",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "supporting": [
        {"name": "DefaultTabLabel", "use": "iOS 18.0. Apple: \"The default label to use for a tab or tab section.\""},
        {"name": "TabContentBuilder.Content", "use": "iOS 18.0. Apple: \"A view representation of the content of a builder-based tab view with selection.\""}
      ]
    },
    "android": {
      "variants": [
        {
          "name": "NavigationBarItem",
          "note": "One destination in a NavigationBar: an icon, an optional label, and selected and onClick."
        },
        {
          "name": "ShortNavigationBar",
          "note": "A newer, shorter bottom bar for three to five destinations."
        },
        {
          "name": "ShortNavigationBarItem",
          "note": "One destination in a ShortNavigationBar. Its iconPosition puts the label under the icon or beside it."
        }
      ],
      "supporting": [
        {
          "name": "NavigationBarDefaults",
          "use": "Default container colour, elevation and window insets for NavigationBar."
        },
        {
          "name": "NavigationBarItemDefaults",
          "use": "Default colours for NavigationBarItem. Make them with NavigationBarItemDefaults.colors()."
        },
        {
          "name": "NavigationBarItemColors",
          "use": "The icon, text and indicator colours of a NavigationBarItem, selected and not."
        },
        {
          "name": "ShortNavigationBarDefaults",
          "use": "Default colours, arrangement and window insets for ShortNavigationBar."
        },
        {
          "name": "ShortNavigationBarItemDefaults",
          "use": "Default colours for ShortNavigationBarItem."
        },
        {
          "name": "ShortNavigationBarArrangement",
          "use": "How ShortNavigationBar spreads its items: EqualWeight (each item gets the same width) or Centered (the items sit in the middle)."
        },
        {
          "name": "NavigationItemColors",
          "use": "The icon, text and indicator colours that ShortNavigationBarItem and WideNavigationRailItem use, selected and not."
        },
        {
          "name": "NavigationItemIconPosition",
          "use": "Where an item's icon sits next to its label: Top (label below) or Start (label beside)."
        }
      ]
    }
  }
};
