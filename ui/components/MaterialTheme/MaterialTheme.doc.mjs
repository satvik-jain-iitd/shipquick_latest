/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "MaterialTheme",
  "displayName": "Material theme",
  "platforms": {
    "android": "androidx.compose.material3.MaterialTheme",
    "ios": null,
    "web": null
  },
  "group": "Theme",
  "category": "Utility",
  "keywords": [
    "theme",
    "colour",
    "typography",
    "shapes",
    "brand"
  ],
  "usage": {
    "description": "MaterialTheme gives every Material 3 part below it the same colours, type and shapes. Wrap the whole app in it once. Build its colour scheme, type scale and shapes from the tokens in design/tokens.json.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Wrap the app once, at the root."
      },
      {
        "guidance": true,
        "description": "Read values from MaterialTheme.colorScheme, .typography and .shapes."
      },
      {
        "guidance": false,
        "description": "Hard-code a colour, a font size or a corner radius in a screen."
      }
    ],
    "accessibility": [
      {
        "name": "Colour pairs",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Each on-colour (like onPrimary) has at least 4.5:1 contrast with its colour, in light and dark."
      }
    ]
  },
  "props": [
    {
      "name": "colorScheme",
      "type": "ColorScheme",
      "description": "The colour roles, from the tokens."
    },
    {
      "name": "typography",
      "type": "Typography",
      "description": "The type scale, from the tokens."
    },
    {
      "name": "shapes",
      "type": "Shapes",
      "description": "The shape scale, from the tokens."
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The app.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "supporting": [
        {
          "name": "ColorScheme",
          "use": "The named colour roles of the theme, like primary and onPrimary. Make one with lightColorScheme() or darkColorScheme(), or dynamicLightColorScheme() and dynamicDarkColorScheme() on Android 12 and later."
        },
        {
          "name": "contentColorFor",
          "use": "Gives the matching content colour for a background colour of the scheme, like onPrimary for primary."
        },
        {
          "name": "Typography",
          "use": "The type scale of the theme: display, headline, title, body and label, each in large, medium and small."
        },
        {
          "name": "Shapes",
          "use": "The shape scale of the theme: extraSmall, small, medium, large and extraLarge."
        },
        {
          "name": "ShapeDefaults",
          "use": "The default value of each shape in the scale."
        },
        {
          "name": "RippleDefaults",
          "use": "The default ripple alpha values."
        },
        {
          "name": "RippleConfiguration",
          "use": "Changes the ripple colour or alpha for one part of the screen, set through LocalRippleConfiguration. Use it only when the default ripple cannot be seen."
        },
        {
          "name": "ExperimentalMaterial3Api",
          "use": "Marks M3 API that may still change. Opt in with @OptIn(ExperimentalMaterial3Api::class) where you call it; experimental rows are marked in docs/research/android-m3-api.md."
        },
        {
          "name": "MaterialTheme",
          "use": "Reads the current theme inside any composable: MaterialTheme.colorScheme, MaterialTheme.typography and MaterialTheme.shapes."
        }
      ]
    }
  }
};
