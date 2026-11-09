/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Surface",
  "displayName": "Surface",
  "platforms": {
    "android": "androidx.compose.material3.Surface",
    "ios": null,
    "web": null
  },
  "group": "Surface",
  "category": "Container",
  "keywords": [
    "surface",
    "container",
    "background",
    "elevation"
  ],
  "usage": {
    "description": "Surface is the base container under cards, sheets and bars: shape, colour, elevation and border. It also sets the content colour for what is inside.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it only when no other part fits, like a plain coloured area."
      },
      {
        "guidance": false,
        "description": "Rebuild a card or a sheet from a Surface."
      }
    ],
    "accessibility": [
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its container."
      }
    ]
  },
  "props": [
    {
      "name": "shape",
      "type": "Shape",
      "description": "The outline. Take it from MaterialTheme.shapes."
    },
    {
      "name": "tonalElevation",
      "type": "Dp",
      "description": "Tints the colour to show height."
    },
    {
      "name": "onClick",
      "type": "() -> Unit",
      "description": "Makes the surface clickable. An overload takes it."
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "What is inside.",
      "required": true
    }
  ]
};
