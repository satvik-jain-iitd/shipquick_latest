/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/slider (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Slider",
  "displayName": "Slider",
  "platforms": {
    "android": "androidx.compose.material3.Slider",
    "ios": "SwiftUI.Slider",
    "web": "@astryxdesign/core/Slider"
  },
  "platformUsage": {
    "android": {
      "accessibility": [
        {
          "name": "Touch target",
          "category": "Content",
          "criterion": "2.5.8 Target Size (Minimum)",
          "requirement": "48dp",
          "description": "Google: anything a user can tap is at least 48dp. Material sets this on the thumb only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
        }
      ]
    },
    "ios": {
      "description": "On iOS, Slider(value:in:step:onEditingChanged:) binds a number inside a range.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Put the minimum on the leading side (Apple HIG, Sliders)."
        },
        {
          "guidance": true,
          "description": "Give it a label with Slider(value:in:label:onEditingChanged:), so VoiceOver can name it."
        }
      ],
      "accessibility": [
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
  "group": "Slider",
  "category": "Form Controls",
  "keywords": [
    "slider",
    "range",
    "volume",
    "value"
  ],
  "usage": {
    "description": "A slider lets the user pick a value from a range, like volume, a price range or a rating. It has a track, a thumb and optional tick marks.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use steps for a small set of values."
      },
      {
        "guidance": true,
        "description": "Show the value in words near the slider."
      },
      {
        "guidance": false,
        "description": "Use a slider when the exact number matters. Use a text field."
      }
    ],
    "accessibility": [
      {
        "name": "Value is read out",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "label and value",
        "description": "Give the slider a label so the screen reader says what the value is for."
      }
    ],
    "anatomy": [
      {
        "name": "Track",
        "required": true,
        "description": "The bar of the range."
      },
      {
        "name": "Thumb",
        "required": true,
        "description": "The part the user drags."
      },
      {
        "name": "Tick marks",
        "required": false,
        "description": "Show the steps."
      }
    ]
  },
  "props": [
    {
      "name": "value",
      "type": "number",
      "description": "The current value.",
      "required": true
    },
    {
      "name": "onValueChange",
      "type": "(value: number) => void",
      "description": "Runs with each new value.",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "valueRange",
      "type": "ClosedFloatingPointRange<Float>",
      "description": "The lowest and highest value, like 0f..100f.",
      "default": "0f..1f"
    },
    {
      "name": "steps",
      "type": "number",
      "description": "How many stops between the two ends of valueRange. 0 means smooth.",
      "default": "0"
    },
    {
      "name": "onValueChangeFinished",
      "type": "() => void",
      "description": "Runs when the user lets go."
    },
    {
      "name": "value",
      "type": "Binding<Double>",
      "description": "The current value.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "in",
      "type": "ClosedRange<Double>",
      "description": "The lowest and highest value.",
      "platform": "ios",
      "default": "0...1"
    },
    {
      "name": "step",
      "type": "Double",
      "description": "The distance between stops.",
      "platform": "ios",
      "default": "1"
    },
    {
      "name": "onEditingChanged",
      "type": "(Bool) -> Void",
      "description": "Runs with true when a drag starts and false when it ends.",
      "platform": "ios",
      "default": "{ _ in }"
    }
  ],
  "platformApi": {
    "android": {
      "variants": [
        {
          "name": "RangeSlider",
          "note": "A slider with two thumbs, for a start and an end value, like a price range."
        },
        {
          "name": "SliderDefaults.Thumb",
          "note": "The default thumb. Pass it to the thumb slot to change only its colours or size."
        },
        {
          "name": "SliderDefaults.Track",
          "note": "The default track, with its stop and tick marks. Pass it to the track slot to change only its colours."
        }
      ],
      "supporting": [
        {
          "name": "SliderDefaults",
          "use": "Default colours, Thumb, Track, tick size and stop mark size for sliders. Make colours with SliderDefaults.colors()."
        },
        {
          "name": "SliderColors",
          "use": "The thumb, track and tick colours of a slider, active and inactive, on and off."
        },
        {
          "name": "SliderState",
          "use": "Holds a slider's value, valueRange, steps and onValueChangeFinished. Pass it to the Slider that takes a state."
        },
        {
          "name": "rememberSliderState",
          "use": "Creates and keeps a SliderState across recompositions."
        },
        {
          "name": "RangeSliderState",
          "use": "Holds a range slider's activeRangeStart, activeRangeEnd, valueRange and steps."
        },
        {
          "name": "rememberRangeSliderState",
          "use": "Creates and keeps a RangeSliderState across recompositions."
        },
        {
          "name": "SliderPositions",
          "use": "The old holder of tick positions.",
          "status": "deprecated",
          "replacement": "SliderState (Google: \"Not necessary with the introduction of Slider state\")"
        }
      ]
    }
  }
};
