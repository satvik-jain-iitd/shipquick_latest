/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/slider (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Slider",
  "displayName": "Slider",
  "platforms": {
    "android": "androidx.compose.material3.Slider",
    "ios": null,
    "web": "@astryxdesign/core/Slider"
  },
  "group": "Slider",
  "category": "Form Controls",
  "keywords": [
    "slider",
    "range",
    "volume",
    "value"
  ],
  "usage": {
    "description": "A slider lets the user pick a value from a range, like volume, a price range or a rating. It has a track, a thumb and optional tick marks.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use steps for a small set of values."
      },
      {
        "guidance": true,
        "description": "Show the value in words near the slider."
      },
      {
        "guidance": false,
        "description": "Use a slider when the exact number matters. Use a text field."
      }
    ],
    "accessibility": [
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "48dp",
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on the thumb only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      },
      {
        "name": "Value is read out",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "label and value",
        "description": "Give the slider a label so the screen reader says what the value is for."
      }
    ],
    "anatomy": [
      {
        "name": "Track",
        "required": true,
        "description": "The bar of the range."
      },
      {
        "name": "Thumb",
        "required": true,
        "description": "The part the user drags."
      },
      {
        "name": "Tick marks",
        "required": false,
        "description": "Show the steps."
      }
    ]
  },
  "props": [
    {
      "name": "value",
      "type": "number",
      "description": "The current value.",
      "required": true
    },
    {
      "name": "onValueChange",
      "type": "(value: number) => void",
      "description": "Runs with each new value.",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "steps",
      "type": "number",
      "description": "How many stops between the ends. 0 means smooth.",
      "default": "0"
    },
    {
      "name": "onValueChangeFinished",
      "type": "() => void",
      "description": "Runs when the user lets go."
    }
  ]
};
