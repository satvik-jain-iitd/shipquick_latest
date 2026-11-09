/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "DisclosureGroup",
  "displayName": "DisclosureGroup",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.DisclosureGroup",
    "web": null
  },
  "group": "DisclosureGroup",
  "category": "Container",
  "keywords": [
    "disclosure",
    "expand",
    "collapse",
    "accordion",
    "more"
  ],
  "usage": {
    "description": "DisclosureGroup shows or hides more content when people tap its title. Apple: \"A view that shows or hides another content view, based on the state of a disclosure control.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Hide details until they matter. Keep the most used controls outside the group, always visible."
      },
      {
        "guidance": false,
        "description": "Hide something people need on every visit."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "The title is the spoken name. VoiceOver also says if the group is open or closed."
      }
    ],
    "anatomy": [
      {
        "name": "Title",
        "required": true,
        "description": "The words people tap to open or close it."
      },
      {
        "name": "Content",
        "required": true,
        "description": "What shows when it is open."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "string",
      "description": "The words on the title row. init(_:content:).",
      "required": true
    },
    {
      "name": "isExpanded",
      "type": "Binding<Bool>",
      "description": "Open or closed, kept by the screen. init(_:isExpanded:content:)."
    },
    {
      "name": "content",
      "type": "() -> some View",
      "description": "What shows when the group is open.",
      "required": true
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "disclosureGroupStyle", "note": "`.disclosureGroupStyle(_:)`, iOS 16.0. Apple: \"Sets the style for disclosure groups within this view.\""}
      ],
      "supporting": [
        {"name": "DisclosureGroupStyleConfiguration.Content", "use": "iOS 16.0. Apple: \"A type-erased content of a disclosure group.\""},
        {"name": "DisclosureGroupStyleConfiguration.Label", "use": "iOS 16.0. Apple: \"A type-erased label of a disclosure group.\""}
      ]
    }
  }
};
