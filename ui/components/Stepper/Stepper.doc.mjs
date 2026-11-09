/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Stepper",
  "displayName": "Stepper",
  "platforms": {
    "android": null,
    "ios": "SwiftUI.Stepper",
    "web": null
  },
  "group": "Stepper",
  "category": "Form Controls",
  "keywords": [
    "stepper",
    "plus minus",
    "increment",
    "decrement",
    "quantity",
    "counter"
  ],
  "usage": {
    "description": "Stepper has a minus and a plus segment that change a number by a step. Apple: \"A control that performs increment and decrement actions.\"",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Show the value next to the stepper. The stepper itself does not show it."
      },
      {
        "guidance": true,
        "description": "Pair it with a text field when people may need big changes."
      }
    ],
    "accessibility": [
      {
        "name": "VoiceOver name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "a spoken name",
        "description": "The title is the spoken name. People swipe up or down to change the value."
      },
      {
        "name": "Touch target",
        "category": "Content",
        "criterion": "2.5.8 Target Size (Minimum)",
        "requirement": "44pt iOS",
        "description": "Each segment is at least the feel.touchTarget token."
      }
    ],
    "anatomy": [
      {
        "name": "Title",
        "required": true,
        "description": "Names the value."
      },
      {
        "name": "Minus and plus",
        "required": true,
        "description": "The two segments."
      }
    ]
  },
  "props": [
    {
      "name": "title",
      "type": "string",
      "description": "The words that name the value. init(_:value:in:step:onEditingChanged:).",
      "required": true
    },
    {
      "name": "value",
      "type": "Binding<Strideable>",
      "description": "The number, kept by the screen.",
      "required": true
    },
    {
      "name": "bounds",
      "type": "ClosedRange<Strideable>",
      "description": "The lowest and highest value (the `in:` label)."
    },
    {
      "name": "step",
      "type": "number",
      "description": "How much one tap changes the value.",
      "default": "1"
    }
  ]
};
