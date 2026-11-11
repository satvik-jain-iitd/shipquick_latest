/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ContactAccess",
  "displayName": "Contact access",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ContactAccess",
  "category": "Overlay",
  "keywords": [
    "contacts",
    "contact access",
    "contact picker",
    "contacts ui"
  ],
  "usage": {
    "description": "Modifiers for limited contact access: the picker where people choose which contacts the app may see, and the look of the contact access button. Each entry is a SwiftUI view modifier from ContactsUI. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Contact access",
      "variants": [
        {"name": "contactAccessButtonCaption", "note": "`.contactAccessButtonCaption(_:)`, iOS 18.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contactaccessbuttoncaption(_:)"},
        {"name": "contactAccessButtonStyle", "note": "`.contactAccessButtonStyle(_:)`, iOS 18.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contactaccessbuttonstyle(_:)"},
        {"name": "contactAccessPicker", "note": "`.contactAccessPicker(isPresented:completionHandler:)`, iOS 18.0. Apple: \"Modally present UI which allows the user to select which contacts your app has access to.\""}
      ]
    }
  }
};
