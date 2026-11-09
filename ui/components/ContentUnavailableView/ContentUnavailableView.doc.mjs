/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ContentUnavailableView",
  "displayName": "Content unavailable view",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ContentUnavailableView",
  "category": "Feedback & Status",
  "keywords": [
    "empty state",
    "no results",
    "unavailable",
    "search empty"
  ],
  "usage": {
    "description": "ContentUnavailableView tells people there is nothing to show yet, like no search results. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "ContentUnavailableView", "note": "iOS 17.0. Apple: \"An interface, consisting of a label and additional content, that you display when the content of your app is unavailable to users.\""},
        {"name": "DocumentLaunchView", "note": "iOS 18.0. Apple: \"A view to present when launching document-related user experience.\""}
      ],
      "supporting": [
        {"name": "DefaultDocumentGroupLaunchActions", "use": "iOS 18.0. Apple: \"The default actions for the document group launch scene and the document launch view.\""},
        {"name": "SearchUnavailableContent.Actions", "use": "iOS 17.0. Apple: \"A view that represents the actions of a static `ContentUnavailableView.search` view.\""},
        {"name": "SearchUnavailableContent.Description", "use": "iOS 17.0. Apple: \"A view that represents the description of a static `ContentUnavailableView.search` view.\""},
        {"name": "SearchUnavailableContent.Label", "use": "iOS 17.0. Apple: \"A view that represents the label of a static placeholder search view.\""}
      ]
    }
  }
};
