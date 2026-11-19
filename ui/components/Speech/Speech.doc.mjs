/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Speech",
  "displayName": "Speech",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Speech",
  "category": "Utility",
  "keywords": [
      "speech",
      "voiceover",
      "pitch",
      "punctuation",
      "spell out",
      "announcement"
  ],
  "usage": {
    "description": "Modifiers that shape how VoiceOver and other speech output read a view aloud: pitch, punctuation, spelling and announcement queueing. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Speech",
      "variants": [
        {"name": "speechAdjustedPitch", "note": "`.speechAdjustedPitch(_:)`, iOS 15.0. Apple: \"Raises or lowers the pitch of spoken text.\""},
        {"name": "speechAlwaysIncludesPunctuation", "note": "`.speechAlwaysIncludesPunctuation(_:)`, iOS 15.0. Apple: \"Sets whether VoiceOver should always speak all punctuation in the text view.\""},
        {"name": "speechAnnouncementsQueued", "note": "`.speechAnnouncementsQueued(_:)`, iOS 15.0. Apple: \"Controls whether to queue pending announcements behind existing speech rather than interrupting speech in progress.\""},
        {"name": "speechSpellsOutCharacters", "note": "`.speechSpellsOutCharacters(_:)`, iOS 15.0. Apple: \"Sets whether VoiceOver should speak the contents of the text view character by character.\""}
      ]
    }
  }
};
