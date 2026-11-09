/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Image",
  "displayName": "Image",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.Image",
    "web": null
  },
  "group": "Image",
  "category": "Content",
  "keywords": [
    "image",
    "picture",
    "photo",
    "icon",
    "symbol"
  ],
  "usage": {
    "description": "Image shows one picture: an asset from the app, a photo, or an SF Symbol. Apple: \"A view that displays an image.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use Image only to show a picture. For a picture people tap, put it inside a Button."
      },
      {
        "guidance": true,
        "description": "For an icon, use an SF Symbol with systemName. It scales with text and tints with the theme."
      },
      {
        "guidance": false,
        "description": "Add tap or drag gestures to an Image to make a control."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "A picture that carries meaning gets a label. A picture that is only decoration uses init(decorative:), so VoiceOver skips it."
      }
    ],
    "anatomy": [
      {
        "name": "Picture",
        "required": true,
        "description": "The image or symbol itself."
      }
    ]
  },
  "props": [
    {
      "name": "name",
      "type": "string",
      "description": "The image name in the app's asset catalog. init(_:bundle:)."
    },
    {
      "name": "systemName",
      "type": "string",
      "description": "The SF Symbol name, like \"star.fill\". init(systemName:)."
    },
    {
      "name": "isDecorative",
      "type": "boolean",
      "description": "true uses init(decorative:): an unlabeled image that VoiceOver skips.",
      "default": "false"
    }
  ]
};
