/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "DocumentLaunchView",
  "displayName": "Document launch view",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "DocumentLaunchView",
  "category": "Utility",
  "keywords": [
    "document",
    "launch",
    "document group",
    "file picker"
  ],
  "usage": {
    "description": "DocumentLaunchView is the first screen of an app that opens documents, with a button to make a new one or open one. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "DocumentLaunchView",
      "variants": [
        {"name": "DocumentLaunchView", "note": "iOS 18.0. Apple: \"A view to present when launching document-related user experience.\""},
        {"name": "documentBrowserContextMenu", "note": "`.documentBrowserContextMenu(_:)`, iOS 18.1. Apple: \"Adds to a `DocumentLaunchView` actions that accept a list of selected files as their parameter.\""},
        {"name": "documentLaunchSubtitle", "note": "`.documentLaunchSubtitle(_:)`, iOS 27.0. Apple: \"Sets the subtitle displayed beneath the title on the document launch card.\""},
        {"name": "documentLaunchTitle", "note": "`.documentLaunchTitle(_:)`, iOS 27.0. Apple: \"Sets the title displayed on the document launch card.\""}
      ],
      "supporting": [
        {"name": "DefaultDocumentGroupLaunchActions", "use": "iOS 18.0. Apple: \"The default actions for the document group launch scene and the document launch view.\""}
      ]
    }
  }
};
