/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Button",
  "displayName": "Button",
  "platforms": {
    "android": "androidx.compose.material3.Button",
    "ios": "SwiftUI.Button",
    "web": "@astryxdesign/core/Button"
  },
  "group": "Button",
  "category": "Action",
  "keywords": ["button", "btn", "cta", "submit", "action", "press"],
  "usage": {
    "description": "A button starts an action when the user presses it. Use it to save, send, confirm or start a task.",
    "bestPractices": [
      {"guidance": true, "description": "Keep one primary button per screen. Use secondary or ghost for the rest."},
      {"guidance": true, "description": "Name the action in the label, like \"Save changes\", not \"OK\"."},
      {"guidance": false, "description": "Use a button only to go to another page. Use a link instead."}
    ],
    "accessibility": [
      {"name": "Touch target", "category": "Content", "criterion": "2.5.8 Target Size (Minimum)", "requirement": "the feel.touchTarget token","description": "The pressable area is at least the feel.touchTarget token in design/tokens.json, even when the drawn button is smaller."},
      {"name": "Text label", "category": "Color contrast", "criterion": "1.4.3 Contrast (Minimum)", "requirement": "4.5:1", "description": "The label text has at least 4.5:1 contrast with the button fill in every state."}
    ],
    "anatomy": [
      {"name": "Container", "required": true, "description": "The pressable shape. Its fill shows the variant."},
      {"name": "Label", "required": true, "description": "The words for the action. Also the accessible name."},
      {"name": "Spinner", "required": false, "description": "Shows while the action runs."}
    ]
  },
  "props": [
    {"name": "label", "type": "string", "description": "The words on the button. Screen readers read them too.", "required": true},
    {"name": "variant", "type": "'primary' | 'secondary' | 'ghost' | 'destructive'", "description": "How strong the button looks. Primary is for the one main action.", "default": "'secondary'"},
    {"name": "size", "type": "'sm' | 'md' | 'lg'", "description": "How big the button is. The touch target never drops below the token.", "default": "'md'"},
    {"name": "isDisabled", "type": "boolean", "description": "Greys the button out and ignores presses.", "default": "false"},
    {"name": "isLoading", "type": "boolean", "description": "Shows a spinner and ignores presses until the action ends.", "default": "false"},
    {"name": "onClick", "type": "() => void", "description": "Runs when the user presses the button."},
    {"name": "type", "type": "'button' | 'submit' | 'reset'", "description": "The HTML button type. Web only.", "default": "'button'"}
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "pasteDestination", "note": "`.pasteDestination(for:action:validator:)`, iOS 27.0. Apple: \"Specifies an action that adds validated items to a view in response to the system’s Paste command.\""},
        {"name": "renameAction", "note": "`.renameAction(_:)`, iOS 16.0. Apple: \"Sets a closure to run for the rename action.\""}
      ]
    },
    "android": {
      "variants": [
        {
          "name": "FilledTonalButton",
          "note": "Less strong than Button, stronger than OutlinedButton. Use it for a second action that still matters, like Next in a set-up flow."
        },
        {
          "name": "ElevatedButton",
          "note": "A tonal button with a shadow. Use it only when the button must stand apart from a busy background."
        },
        {
          "name": "OutlinedButton",
          "note": "A border and no fill. Use it for an important action that is not the main one."
        },
        {
          "name": "TextButton",
          "note": "Text only, the weakest look. Use it in dialogs, in cards, and for minor actions."
        }
      ],
      "supporting": [
        {
          "name": "ButtonDefaults",
          "use": "The default colours, elevation, shape, padding and sizes for each button type. Take values from it, never type your own."
        },
        {
          "name": "ButtonColors",
          "use": "The colours of a button when it is on or off. Make one with ButtonDefaults.buttonColors() or the colour function of its type."
        },
        {
          "name": "ButtonElevation",
          "use": "The shadow of a button in each state. Make one with ButtonDefaults.buttonElevation() or the elevation function of its type."
        }
      ]
    }
  }
};
