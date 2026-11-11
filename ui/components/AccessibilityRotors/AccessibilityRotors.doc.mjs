/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "AccessibilityRotors",
  "displayName": "Accessibility rotors",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "AccessibilityRotors",
  "category": "Utility",
  "keywords": [
      "rotor",
      "voiceover",
      "accessibility rotor",
      "navigation",
      "custom rotor"
  ],
  "usage": {
    "description": "Modifiers that add a custom VoiceOver rotor and its entries, so a user can jump between related items. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Accessibility rotors",
      "variants": [
        {"name": "accessibilityRotor", "note": "`.accessibilityRotor(_:entries:)`, iOS 16.0. Apple: \"Create an Accessibility Rotor with the specified user-visible label, and entries generated from the content closure.\""},
        {"name": "accessibilityRotorEntry", "note": "`.accessibilityRotorEntry(id:in:)`, iOS 15.0. Apple: \"Defines an explicit identifier tying an Accessibility element for this view to an entry in an Accessibility Rotor.\""}
      ]
    }
  }
};
