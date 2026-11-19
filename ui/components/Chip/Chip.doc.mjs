/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/chip (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Chip",
  "displayName": "Chip",
  "platforms": {
    "android": "androidx.compose.material3.FilterChip",
    "ios": null,
    "web": null
  },
  "group": "Chip",
  "category": "Form Controls",
  "keywords": [
    "chip",
    "tag",
    "filter",
    "pill",
    "token"
  ],
  "usage": {
    "description": "A chip is a small part with a label and often an icon. Assist chips guide a task. Filter chips narrow content and can be selected. Input chips show what the user entered and can be removed. Suggestion chips offer next steps.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use FilterChip for options the user turns on and off."
      },
      {
        "guidance": true,
        "description": "Use InputChip with a remove icon for entered items."
      },
      {
        "guidance": false,
        "description": "Use a chip as the main action. Use a button."
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
        "description": "Google: anything a user can tap is at least 48dp. Material sets this on the chip only when it has a click handler (https://developer.android.com/develop/ui/compose/accessibility/api-defaults)."
      },
      {
        "name": "Text contrast",
        "category": "Color contrast",
        "criterion": "1.4.3 Contrast (Minimum)",
        "requirement": "4.5:1",
        "description": "Text has at least 4.5:1 contrast with its fill. The colours come from the tokens, never typed in."
      }
    ],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "The chip shape."
      },
      {
        "name": "Label",
        "required": true,
        "description": "The words."
      },
      {
        "name": "Leading icon",
        "required": false,
        "description": "At the start."
      },
      {
        "name": "Trailing icon",
        "required": false,
        "description": "At the end, like a remove X."
      }
    ]
  },
  "props": [
    {
      "name": "selected",
      "type": "boolean",
      "description": "Filter chip: true when it is on.",
      "required": true
    },
    {
      "name": "onClick",
      "type": "() => void",
      "description": "Runs when the user taps the chip.",
      "required": true
    },
    {
      "name": "label",
      "type": "@Composable () -> Unit",
      "description": "The words on the chip.",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "leadingIcon",
      "type": "@Composable () -> Unit",
      "description": "An icon at the start."
    },
    {
      "name": "trailingIcon",
      "type": "@Composable () -> Unit",
      "description": "An icon at the end."
    }
  ],
  "platformApi": {
    "android": {
      "family": "Chip",
      "variants": [
        {
          "name": "AssistChip",
          "note": "Helps the user do a task linked to the content, like add an event to the calendar."
        },
        {
          "name": "ElevatedAssistChip",
          "note": "An AssistChip with a shadow and no border. Use it on a busy background."
        },
        {
          "name": "ElevatedFilterChip",
          "note": "A FilterChip with a shadow and no border. Use it on a busy background."
        },
        {
          "name": "InputChip",
          "note": "A piece of input the user gave, like a contact in a To field. It can have an avatar and a remove icon."
        },
        {
          "name": "SuggestionChip",
          "note": "A suggestion made from the content, like a smart reply."
        },
        {
          "name": "ElevatedSuggestionChip",
          "note": "A SuggestionChip with a shadow and no border. Use it on a busy background."
        }
      ],
      "supporting": [
        {
          "name": "AssistChipDefaults",
          "use": "Default colours, border, elevation, height and shape for assist chips."
        },
        {
          "name": "FilterChipDefaults",
          "use": "Default colours, border, elevation, height and shape for filter chips."
        },
        {
          "name": "InputChipDefaults",
          "use": "Default colours, border, elevation, sizes and shape for input chips."
        },
        {
          "name": "SuggestionChipDefaults",
          "use": "Default colours, border, elevation, height and shape for suggestion chips."
        },
        {
          "name": "ChipColors",
          "use": "The container, label and icon colours of an assist or suggestion chip, on and off."
        },
        {
          "name": "SelectableChipColors",
          "use": "The colours of a filter or input chip, selected and not, on and off."
        },
        {
          "name": "ChipElevation",
          "use": "The shadow of an assist or suggestion chip in each state."
        },
        {
          "name": "SelectableChipElevation",
          "use": "The shadow of a filter or input chip in each state."
        },
        {
          "name": "ChipBorder",
          "use": "The old chip border class.",
          "status": "deprecated",
          "replacement": "the chipBorder functions, like AssistChipDefaults.assistChipBorder() (Google: \"Maintained for binary compatibility. Use the chipBorder functions instead\")"
        }
      ]
    }
  }
};
