/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Keyboard",
  "displayName": "Hardware keyboard",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Keyboard",
  "category": "Utility",
  "keywords": [
    "keyboard",
    "key press",
    "keyboard shortcut",
    "command",
    "modifier key"
  ],
  "usage": {
    "description": "Modifiers that answer a hardware keyboard: key presses, shortcuts and system commands. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it. The on-screen keyboard belongs to TextField.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Give every shortcut a visible control too; a keyboard is optional on iPhone and iPad."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Keyboard",
      "variants": [
        {"name": "keyboardShortcut", "note": "`.keyboardShortcut(_:)`, iOS 14.0. Apple: \"Assigns a keyboard shortcut to the modified control.\""},
        {"name": "modifierKeyAlternate", "note": "`.modifierKeyAlternate(_:_:)`, not on iOS. Apple: \"Builds a view to use in place of the modified view when the user presses the modifier key(s) indicated by the given set.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a Mac menu item that swaps while a modifier key is held)"},
        {"name": "onCommand", "note": "`.onCommand(_:perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the given selector.\"", "status": "unavailable-ios", "replacement": "onKeyPress"},
        {"name": "onDeleteCommand", "note": "`.onDeleteCommand(perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the system’s Delete command, or pressing either the ⌫ (backspace) or ⌦ (forward delete) keys while the view has focus.\"", "status": "unavailable-ios", "replacement": "swipeActions"},
        {"name": "onExitCommand", "note": "`.onExitCommand(perform:)`, not on iOS. Apple: \"Sets up an action that triggers in response to receiving the exit command while the view has focus.\"", "status": "unavailable-ios", "replacement": "onKeyPress"},
        {"name": "onKeyPress", "note": "`.onKeyPress(_:action:)`, iOS 17.0. Apple: \"Performs an action if the user presses a key on a hardware keyboard while the view has focus.\""},
        {"name": "onModifierKeysChanged", "note": "`.onModifierKeysChanged(mask:initial:_:)`, not on iOS. Apple: \"Performs an action whenever the user presses or releases a hardware modifier key.\"", "status": "unavailable-ios", "replacement": "onKeyPress"},
        {"name": "onMoveCommand", "note": "`.onMoveCommand(perform:)`, not on iOS. Apple: \"Adds an action to perform in response to a move command, like when the user presses an arrow key on a Mac keyboard, or taps the edge of the Siri Remote when controlling an Apple TV.\"", "status": "unavailable-ios", "replacement": "onKeyPress"},
        {"name": "onPlayPauseCommand", "note": "`.onPlayPauseCommand(perform:)`, not on iOS. Apple: \"Adds an action to perform in response to the system’s Play/Pause command.\"", "status": "unavailable-ios", "replacement": "onKeyPress"},
        {"name": "pageCommand", "note": "`.pageCommand(value:in:step:)`, not on iOS. Apple: \"Steps a value through a range in response to page up or page down commands.\"", "status": "unavailable-ios", "replacement": "onKeyPress"}
      ]
    }
  }
};
