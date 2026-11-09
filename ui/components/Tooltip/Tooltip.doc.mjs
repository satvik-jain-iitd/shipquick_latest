/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/components/tooltip (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "Tooltip",
  "displayName": "Tooltip",
  "platforms": {
    "android": "androidx.compose.material3.TooltipBox",
    "ios": null,
    "web": "@astryxdesign/core/Tooltip"
  },
  "platformUsage": {
    "android": {
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use PlainTooltip to name an icon button's action."
        },
        {
          "guidance": true,
          "description": "Use TooltipDefaults' position providers to place it."
        }
      ],
      "accessibility": [
        {
          "name": "Not the only name",
          "category": "Semantics",
          "criterion": "1.4.13 Content on Hover or Focus",
          "requirement": "dismissible, stays",
          "description": "The tooltip can be closed and stays while the user looks at it. The icon still has its own contentDescription."
        }
      ]
    }
  },
  "group": "Tooltip",
  "category": "Overlay",
  "keywords": [
    "tooltip",
    "hint",
    "help",
    "long press"
  ],
  "usage": {
    "description": "A tooltip adds a short note to a button or other part. A plain tooltip says what an icon button does. A rich tooltip says more and can have a title, a link and buttons.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Hide the only copy of needed words in a tooltip."
      }
    ],
    "accessibility": [
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
        "name": "Anchor",
        "required": true,
        "description": "The part the tooltip points at."
      },
      {
        "name": "Container",
        "required": true,
        "description": "The tooltip box."
      },
      {
        "name": "Title",
        "required": false,
        "description": "Rich tooltip only."
      },
      {
        "name": "Action",
        "required": false,
        "description": "Rich tooltip only."
      }
    ]
  },
  "props": [
    {
      "name": "positionProvider",
      "type": "PopupPositionProvider",
      "description": "Where the tooltip sits next to its anchor. Use a TooltipDefaults provider.",
      "required": true
    },
    {
      "name": "tooltip",
      "type": "@Composable TooltipScope.() -> Unit",
      "description": "The tooltip: PlainTooltip or RichTooltip.",
      "required": true
    },
    {
      "name": "state",
      "type": "TooltipState",
      "description": "Shows and hides the tooltip. Create it with rememberTooltipState().",
      "required": true
    },
    {
      "name": "content",
      "type": "@Composable () -> Unit",
      "description": "The anchor the tooltip belongs to.",
      "required": true
    }
  ],
  "platformApi": {
    "android": {
      "family": "Tooltip",
      "variants": [
        {
          "name": "PlainTooltip",
          "note": "A short line of text that names an icon or a button. Put it in TooltipBox."
        },
        {
          "name": "RichTooltip",
          "note": "A tooltip with an optional title, more text and an optional action button. Put it in TooltipBox."
        }
      ],
      "supporting": [
        {
          "name": "TooltipState",
          "use": "Says if the tooltip shows. Call show() from a coroutine and dismiss() to hide it. isPersistent keeps it open."
        },
        {
          "name": "rememberTooltipState",
          "use": "Creates and keeps a TooltipState across recompositions."
        },
        {
          "name": "TooltipScope",
          "use": "The scope of tooltip content. Its drawCaret draws the small pointer to the anchor."
        },
        {
          "name": "TooltipDefaults",
          "use": "Default colours, shapes, caret shape and position providers for plain and rich tooltips."
        },
        {
          "name": "RichTooltipColors",
          "use": "The container, content, title and action colours of a RichTooltip. Make one with TooltipDefaults.richTooltipColors()."
        },
        {
          "name": "TooltipAnchorPosition",
          "use": "Where the tooltip sits next to its anchor: Above, Below, Start, End, Left or Right."
        },
        {
          "name": "DefaultTooltipCaretShape",
          "use": "The default pointer shape of a tooltip, with a caretSize. Get it from TooltipDefaults.caretShape()."
        }
      ]
    }
  }
};
