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
      "name": "decorative",
      "type": "string",
      "description": "Apple's init(decorative:) label: the asset name of an unlabeled, decorative image that VoiceOver skips. Use it instead of name."
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "AsyncImage", "note": "iOS 15.0. Apple: \"A view that asynchronously loads and displays an image.\""},
        {"name": "symbolEffect", "note": "`.symbolEffect(_:options:isActive:)`, iOS 17.0. Apple: \"Returns a new view with a symbol effect added to it.\""},
        {"name": "symbolEffectsRemoved", "note": "`.symbolEffectsRemoved(_:)`, iOS 17.0. Apple: \"Returns a new view with its inherited symbol image effects either removed or left unchanged.\""},
        {"name": "symbolColorRenderingMode", "note": "`.symbolColorRenderingMode(_:)`, iOS 26.0. Apple: \"Sets the color rendering mode for symbol images.\""},
        {"name": "symbolRenderingMode", "note": "`.symbolRenderingMode(_:)`, iOS 15.0. Apple: \"Sets the rendering mode for symbol images within this view.\""},
        {"name": "symbolVariableValueMode", "note": "`.symbolVariableValueMode(_:)`, iOS 26.0. Apple: \"Sets the variable value mode mode for symbol images within this view.\""},
        {"name": "symbolVariant", "note": "`.symbolVariant(_:)`, iOS 15.0. Apple: \"Makes symbols within the view show a particular variant.\""},
        {"name": "imageScale", "note": "`.imageScale(_:)`, iOS 13.0. Apple: \"Scales images within the view according to one of the relative sizes available including small, medium, and large images sizes.\""}
      ]
    }
  }
};
