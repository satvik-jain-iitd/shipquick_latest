/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ColorPicker",
  "displayName": "ColorPicker",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.ColorPicker",
    "web": null
  },
  "group": "ColorPicker",
  "category": "Form Controls",
  "keywords": [
    "color",
    "colour",
    "picker",
    "color well",
    "swatch"
  ],
  "usage": {
    "description": "ColorPicker opens the system colour picker and shows the chosen colour. Apple: \"A control used to select a color from the system color picker UI.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the system picker. People get a familiar look and their saved colours."
      },
      {
        "guidance": false,
        "description": "Use it for brand colours. Those come from the tokens."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "The title is the spoken name; VoiceOver also reads the chosen colour."
      }
    ],
    "anatomy": [
      {
        "name": "Title",
        "required": true,
        "description": "The words that name the setting."
      },
      {
        "name": "Well",
        "required": true,
        "description": "The swatch that shows the colour and opens the picker."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "string",
      "description": "The words. init(_:selection:supportsOpacity:).",
      "required": true
    },
    {
      "name": "selection",
      "type": "Binding<Color>",
      "description": "The chosen colour, kept by the screen.",
      "required": true
    },
    {
      "name": "supportsOpacity",
      "type": "boolean",
      "description": "Lets people pick a see-through colour.",
      "default": "true"
    }
  ]
};
