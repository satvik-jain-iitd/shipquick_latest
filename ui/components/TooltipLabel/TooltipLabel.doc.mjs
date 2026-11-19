/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: current.txt of material3 1.4.0 (AOSP 5113b82a) and https://developer.android.com/reference/kotlin/androidx/compose/material3/package-summary (read 9 Nov 2026). Props are Compose parameters. The folder is not Label: ui/components/Label is the iOS Label doc, a different part. */
export default {
  "type": "component",
  "name": "Label",
  "displayName": "Label (tooltip label)",
  "platforms": {
    "android": "androidx.compose.material3.Label",
    "ios": null,
    "web": null
  },
  "group": "Tooltip",
  "category": "Overlay",
  "keywords": [
    "label",
    "tooltip",
    "hover",
    "hint"
  ],
  "usage": {
    "description": "Label adds a small label tooltip to its content. It shows when the user hovers, focuses or long-presses the content.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use it to name an icon-only control in a few words."
      },
      {
        "guidance": false,
        "description": "Put the only copy of important information in it."
      }
    ],
    "accessibility": [
      {
        "name": "Not the only name",
        "category": "Semantics",
        "criterion": "4.1.2 Name, Role, Value",
        "requirement": "an accessible name on the control",
        "description": "The control inside still has its own content description."
      }
    ]
  },
  "props": [
    {
      "name": "label",
      "type": "@Composable TooltipScope.() -> Unit",
      "description": "The tooltip to show, like a PlainTooltip.",
      "required": true
    },
    {
      "name": "isPersistent",
      "type": "boolean",
      "description": "Keeps the label open until the user dismisses it.",
      "default": "false"
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The part the label belongs to.",
      "required": true
    }
  ]
};
