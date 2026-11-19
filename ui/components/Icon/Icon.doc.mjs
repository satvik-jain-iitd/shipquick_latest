/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Icon",
  "displayName": "Icon",
  "platforms": {
    "android": "androidx.compose.material3.Icon",
    "ios": null,
    "web": null
  },
  "group": "Icon",
  "category": "Content",
  "keywords": [
    "icon",
    "symbol",
    "glyph"
  ],
  "usage": {
    "description": "An icon is a small picture that stands for an action or a thing. Material 3 tints it with the content colour of what is behind it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Give a content description when the icon means something on its own."
      },
      {
        "guidance": true,
        "description": "Pass null when text next to it already says the same."
      },
      {
        "guidance": false,
        "description": "Set the tint by hand. Let it come from the theme."
      }
    ],
    "accessibility": [
      {
        "name": "Text alternative",
        "category": "Semantics",
        "criterion": "1.1.1 Non-text Content",
        "requirement": "a content description or null",
        "description": "A meaningful icon has a content description. A decorative one has null."
      },
      {
        "name": "Icon contrast",
        "category": "Color contrast",
        "criterion": "1.4.11 Non-text Contrast",
        "requirement": "3:1",
        "description": "An icon that carries meaning has at least 3:1 contrast with what is behind it."
      }
    ]
  },
  "props": [
    {
      "name": "imageVector",
      "type": "ImageVector",
      "description": "The icon. Other overloads take a Painter or an ImageBitmap.",
      "required": true
    },
    {
      "name": "contentDescription",
      "type": "string | null",
      "description": "What the icon means, for screen readers. null when it is only decoration.",
      "required": true
    }
  ]
};
