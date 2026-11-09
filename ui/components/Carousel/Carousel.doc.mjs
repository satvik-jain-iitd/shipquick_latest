/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/carousel (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Carousel",
  "displayName": "Carousel",
  "platforms": {
    "android": "androidx.compose.material3.carousel.HorizontalMultiBrowseCarousel",
    "ios": null,
    "web": "@astryxdesign/core/Carousel"
  },
  "platformUsage": {
    "android": {
      "description": "Multi-browse shows items of mixed sizes. Uncontained shows one size that runs past the edge.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use multi-browse to browse many items at once."
        }
      ],
      "accessibility": [
        {
          "name": "Icon name",
          "category": "Semantics",
          "criterion": "1.1.1 Non-text Content",
          "requirement": "contentDescription",
          "description": "An icon with no words next to it needs a contentDescription that names the action, like \"Add to favorites\"."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on each clickable item only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    }
  },
  "group": "Carousel",
  "category": "Content",
  "keywords": [
    "carousel",
    "gallery",
    "slider",
    "photos"
  ],
  "usage": {
    "description": "A carousel is a list of items the user scrolls sideways, sized to the window. It is for related visual content, like photos.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Keep the text on each item short."
      },
      {
        "guidance": false,
        "description": "Hide needed content in an item the user may never scroll to."
      }
    ],
    "accessibility": [],
    "anatomy": [
      {
        "name": "Item",
        "required": true,
        "description": "One card of content, often an image."
      },
      {
        "name": "Text",
        "required": false,
        "description": "Short words that fit the item."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "CarouselState",
      "description": "The current item and scroll. Create it with rememberCarouselState.",
      "required": true
    },
    {
      "name": "preferredItemWidth",
      "type": "Dp",
      "description": "Multi-browse: the width the biggest item tries to have.",
      "required": true
    },
    {
      "name": "itemSpacing",
      "type": "Dp",
      "description": "The space between items.",
      "default": "CarouselDefaults.ItemSpacing"
    },
    {
      "name": "content",
      "type": "@Composable CarouselItemScope.(itemIndex: Int) -> Unit",
      "description": "One item, given its index.",
      "required": true
    }
  ]
};
