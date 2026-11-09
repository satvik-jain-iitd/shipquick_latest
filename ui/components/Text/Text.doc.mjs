/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Text",
  "displayName": "Text",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.Text",
    "web": null
  },
  "group": "Text",
  "category": "Content",
  "keywords": [
    "text",
    "copy",
    "words",
    "paragraph",
    "heading"
  ],
  "usage": {
    "description": "Text shows read-only words, one line or many.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use the type tokens for font and size, so the text still grows with the person's text size setting."
      },
      {
        "guidance": false,
        "description": "Use Text for words people must edit. Use a text field instead."
      }
    ],
    "accessibility": [
      {
        "name": "Text size",
        "category": "Content",
        "criterion": "1.4.4 Resize Text",
        "requirement": "200% text size",
        "description": "Text grows with the person's text size setting. Never fix the font size; use the type tokens."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Body text has at least 4.5:1 contrast with what is behind it."
      }
    ],
    "anatomy": [
      {
        "name": "Words",
        "required": true,
        "description": "The string shown."
      }
    ]
  },
  "platformUsage": {
    "ios": {
      "description": "Apple: \"A view that displays one or more lines of read-only text.\" With the type tokens, Text follows Dynamic Type.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Let people select useful text, like an error code, with textSelection(.enabled)."
        }
      ]
    }
  },
  "props": [
    {
      "name": "content",
      "type": "string",
      "description": "The words to show. init(_:) looks them up for translation; init(verbatim:) shows them as they are.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "allowsTightening", "note": "`.allowsTightening(_:)`, iOS 13.0. Apple: \"Sets whether text in this view can compress the space between characters when necessary to fit text in a line.\""},
        {"name": "attributedTextFormattingDefinition", "note": "`.attributedTextFormattingDefinition(_:)`, iOS 26.0. Apple: \"Apply a text formatting definition to nested views.\""},
        {"name": "baselineOffset", "note": "`.baselineOffset(_:)`, iOS 16.0. Apple: \"Sets the vertical offset for the text relative to its baseline in this view.\""},
        {"name": "bold", "note": "`.bold(_:)`, iOS 16.0. Apple: \"Applies a bold font weight to the text in this view.\""},
        {"name": "dataDetection", "note": "`.dataDetection(_:options:)`, iOS 27.0. Apple: \"Asynchronously detects data in the view’s content and styles them to indicate they are clickable.\""},
        {"name": "dynamicTypeSize", "note": "`.dynamicTypeSize(_:)`, iOS 15.0. Apple: \"Sets the Dynamic Type size within the view to the given value.\""},
        {"name": "flipsForRightToLeftLayoutDirection", "note": "`.flipsForRightToLeftLayoutDirection(_:)`, iOS 13.0. Apple: \"Sets whether this view mirrors its contents horizontally when the layout direction is right-to-left.\""},
        {"name": "font", "note": "`.font(_:)`, iOS 13.0. Apple: \"Sets the default font for text in this view.\""},
        {"name": "fontDesign", "note": "`.fontDesign(_:)`, iOS 16.1. Apple: \"Sets the font design of the text in this view.\""},
        {"name": "fontWeight", "note": "`.fontWeight(_:)`, iOS 16.0. Apple: \"Sets the font weight of the text in this view.\""},
        {"name": "fontWidth", "note": "`.fontWidth(_:)`, iOS 16.0. Apple: \"Sets the font width of the text in this view.\""},
        {"name": "italic", "note": "`.italic(_:)`, iOS 16.0. Apple: \"Applies italics to the text in this view.\""},
        {"name": "kerning", "note": "`.kerning(_:)`, iOS 16.0. Apple: \"Sets the spacing, or kerning, between characters for the text in this view.\""},
        {"name": "lineHeight", "note": "`.lineHeight(_:)`, iOS 26.0. Apple: \"A modifier for the default line height in the view hierarchy.\""},
        {"name": "lineLimit", "note": "`.lineLimit(_:)`, iOS 16.0. Apple: \"Sets to a closed range the number of lines that text can occupy in this view.\""},
        {"name": "lineSpacing", "note": "`.lineSpacing(_:)`, iOS 13.0. Apple: \"Sets the amount of space between lines of text in this view.\""},
        {"name": "minimumScaleFactor", "note": "`.minimumScaleFactor(_:)`, iOS 13.0. Apple: \"Sets the minimum amount that text in this view scales down to fit in the available space.\""},
        {"name": "monospaced", "note": "`.monospaced(_:)`, iOS 16.0. Apple: \"Modifies the fonts of all child views to use the fixed-width variant of the current font, if possible.\""},
        {"name": "monospacedDigit", "note": "`.monospacedDigit()`, iOS 15.0. Apple: \"Modifies the fonts of all child views to use fixed-width digits, if possible, while leaving other characters proportionally spaced.\""},
        {"name": "multilineTextAlignment", "note": "`.multilineTextAlignment(_:)`, iOS 13.0. Apple: \"Sets the alignment of a text view that contains multiple lines of text.\""},
        {"name": "strikethrough", "note": "`.strikethrough(_:pattern:color:)`, iOS 16.0. Apple: \"Applies a strikethrough to the text in this view.\""},
        {"name": "textCase", "note": "`.textCase(_:)`, iOS 14.0. Apple: \"Sets a transform for the case of the text contained in this view when displayed.\""},
        {"name": "textRenderer", "note": "`.textRenderer(_:)`, iOS 18.0. Apple: \"Returns a new view such that any text views within it will use `renderer` to draw themselves.\""},
        {"name": "textScale", "note": "`.textScale(_:isEnabled:)`, iOS 17.0. Apple: \"Applies a text scale to text in the view.\""},
        {"name": "textSelection", "note": "`.textSelection(_:)`, iOS 15.0. Apple: \"Controls whether people can select text within this view.\""},
        {"name": "textSelectionAffinity", "note": "`.textSelectionAffinity(_:)`, iOS 18.0. Apple: \"Sets the direction of a selection or cursor relative to a text character.\""},
        {"name": "tracking", "note": "`.tracking(_:)`, iOS 16.0. Apple: \"Sets the tracking for the text in this view.\""},
        {"name": "truncationMode", "note": "`.truncationMode(_:)`, iOS 13.0. Apple: \"Sets the truncation mode for lines of text that are too long to fit in the available space.\""},
        {"name": "typesettingLanguage", "note": "`.typesettingLanguage(_:isEnabled:)`, iOS 17.0. Apple: \"Specifies the language for typesetting.\""},
        {"name": "underline", "note": "`.underline(_:pattern:color:)`, iOS 16.0. Apple: \"Applies an underline to the text in this view.\""},
        {"name": "writingDirection", "note": "`.writingDirection(strategy:)`, iOS 26.0. Apple: \"A modifier for the default text writing direction strategy in the view hierarchy.\""}
      ]
    }
  }
};
