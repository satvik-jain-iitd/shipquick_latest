/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/switch (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Switch",
  "displayName": "Switch",
  "platforms": {
    "android": "androidx.compose.material3.Switch",
    "ios": "SwiftUI.Toggle",
    "web": "@astryxdesign/core/Switch"
  },
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Make the whole row toggleable with its label."
        }
      ],
      "accessibility": [
        {
          "name": "State is read out",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "role and state",
          "description": "Screen readers say the role and the state (on, off, selected). Put the click on the whole row with its label, and pass a null click to the control (Google's api-defaults page)."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on the switch only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS the twin is Toggle. Toggle(\"Wi-Fi\", isOn: $isOn) shows the words and the switch as one row.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put the words in the Toggle's own label, so the whole row is one control."
        }
      ],
      "accessibility": [
        {
          "name": "VoiceOver",
          "category": "Semantics",
          "criterion": "4.1.2 Name, Role, Value",
          "requirement": "a spoken name and state",
          "description": "VoiceOver reads the label, the role, and on or off, as one element."
        },
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "44 by 44 pt",
          "description": "Apple: a control needs a hit region of at least 44 by 44 pt (HIG, Buttons). The feel.touchTarget.ios token is 44pt."
        }
      ]
    }
  },
  "group": "Switch",
  "category": "Form Controls",
  "keywords": [
    "switch",
    "toggle",
    "on off",
    "setting"
  ],
  "usage": {
    "description": "A switch turns one thing on or off, like a setting or a feature. The user drags the thumb or taps the switch.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it for a setting that takes effect at once."
      },
      {
        "guidance": false,
        "description": "Use a switch for a choice that waits for a Save button. Use a checkbox."
      }
    ],
    "accessibility": [
      {
        "name": "Shape contrast",
        "category": "Color contrast",
        "criterion": "1.4.11 Non-text Contrast",
        "requirement": "3:1",
        "description": "The edge or the mark that shows state has at least 3:1 contrast with what is behind it."
      }
    ],
    "anatomy": [
      {
        "name": "Track",
        "required": true,
        "description": "The background."
      },
      {
        "name": "Thumb",
        "required": true,
        "description": "The part that moves."
      },
      {
        "name": "Icon",
        "required": false,
        "description": "Inside the thumb."
      }
    ]
  },
  "props": [
    {
      "name": "checked",
      "type": "boolean",
      "description": "True when it is on.",
      "required": true
    },
    {
      "name": "onCheckedChange",
      "type": "((checked: boolean) => void) | null",
      "description": "Runs with the new value. Pass null when the whole row handles the tap.",
      "required": true
    },
    {
      "name": "thumbContent",
      "type": "@Composable () -> Unit",
      "description": "An icon inside the thumb."
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "The words for the setting.",
      "platform": "ios"
    },
    {
      "name": "isOn",
      "type": "Binding<Bool>",
      "description": "True when it is on.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "label",
      "type": "() -> some View",
      "description": "A custom label instead of words.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "toggleStyle", "note": "`.toggleStyle(_:)`, iOS 13.0. Apple: \"Sets the style for toggles in a view hierarchy.\""}
      ]
    }
  }
};
