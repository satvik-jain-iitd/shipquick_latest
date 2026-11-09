/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "WideNavigationRail",
  "displayName": "Wide navigation rail",
  "platforms": {
    "android": "androidx.compose.material3.WideNavigationRail",
    "ios": null,
    "web": null
  },
  "group": "NavigationRail",
  "category": "Navigation",
  "keywords": [
    "navigation",
    "rail",
    "drawer",
    "large screen"
  ],
  "usage": {
    "description": "WideNavigationRail is the newer rail for medium and large screens. It is collapsed (icons only) or expanded (icons with labels, like a drawer).",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Let the user expand it with a menu button in its header."
      },
      {
        "guidance": true,
        "description": "Use the modal form when it should open over the content."
      },
      {
        "guidance": false,
        "description": "Use it on a phone in portrait. Use a navigation bar."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "the feel.touchTarget token",
        "description": "Each control in it is at least the feel.touchTarget token in design/tokens.json."
      },
      {
        "name": "Reading order",
        "category": "Keyboard",
        "criterion": "1.3.2 Meaningful Sequence",
        "requirement": "order on screen",
        "description": "TalkBack reads the parts in the order they show on screen."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "WideNavigationRailState",
      "description": "Says if the rail is collapsed or expanded. Make it with rememberWideNavigationRailState()."
    },
    {
      "name": "header",
      "type": "@Composable () -> Unit",
      "description": "An optional top part, like the menu button and a FAB."
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The WideNavigationRailItem items.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "ModalWideNavigationRail",
          "note": "A wide rail that opens over the content, with a scrim, when expanded. Set hideOnCollapse to hide it fully when collapsed."
        },
        {
          "name": "WideNavigationRailItem",
          "note": "One destination in a WideNavigationRail. Its label sits under the icon when collapsed and beside it when expanded."
        }
      ],
      "supporting": [
        {
          "name": "WideNavigationRailDefaults",
          "use": "Default colours, shapes, arrangement and window insets for WideNavigationRail and its modal form."
        },
        {
          "name": "WideNavigationRailItemDefaults",
          "use": "Default colours and icon position for WideNavigationRailItem."
        },
        {
          "name": "WideNavigationRailColors",
          "use": "The container, content and modal scrim colours of a WideNavigationRail."
        },
        {
          "name": "WideNavigationRailState",
          "use": "Says if the rail is collapsed or expanded. Call expand(), collapse(), toggle() or snapTo() from a coroutine."
        },
        {
          "name": "rememberWideNavigationRailState",
          "use": "Creates and keeps a WideNavigationRailState, with the first value you give."
        },
        {
          "name": "WideNavigationRailValue",
          "use": "The two states of a wide rail: Collapsed and Expanded."
        },
        {
          "name": "ModalWideNavigationRailProperties",
          "use": "Window settings for ModalWideNavigationRail: shouldDismissOnBackPress and securePolicy."
        }
      ]
    }
  }
};
