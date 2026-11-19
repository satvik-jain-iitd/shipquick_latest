/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Facts from Google: https://developer.android.com/develop/ui/compose/text/user-input (read 9 Nov 2026). Props are Compose parameters. */
export default {
  "type": "component",
  "name": "TextField",
  "displayName": "Text field",
  "platforms": {
    "android": "androidx.compose.material3.TextField",
    "ios": "SwiftUI.TextField",
    "web": "@astryxdesign/core/TextInput"
  },
  "platformUsage": {
    "android": {
      "description": "TextField is filled. OutlinedTextField has a border. SecureTextField hides a password. Google says the value-based fields are deprecated: use the state-based ones with TextFieldState.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Use the state-based field: rememberTextFieldState()."
        },
        {
          "guidance": true,
          "description": "Set keyboardOptions, like KeyboardType.Email for an email."
        },
        {
          "guidance": false,
          "description": "Use BasicTextField for a form. It has no label or error styling."
        }
      ],
      "accessibility": [
        {
          "name": "Errors",
          "category": "Content",
          "criterion": "3.3.1 Error Identification",
          "requirement": "words, not colour only",
          "description": "Set isError and put the reason in supportingText, so the error is said in words."
        }
      ]
    },
    "ios": {
      "description": "On iOS, TextField(_:text:prompt:) binds a String. SecureField hides a password. Pass axis: .vertical for a field that grows to more lines.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Bind text to a String held in @State."
        },
        {
          "guidance": true,
          "description": "Set keyboardType(_:), textContentType(_:) and submitLabel(_:), like .emailAddress for an email."
        },
        {
          "guidance": false,
          "description": "Use a TextField for a password. Use SecureField."
        }
      ],
      "accessibility": [
        {
          "name": "Errors",
          "category": "Content",
          "criterion": "3.3.1 Error Identification",
          "requirement": "the error in words",
          "description": "Put the error in a Text under the field, so VoiceOver reads it in words."
        }
      ]
    }
  },
  "group": "Text field",
  "category": "Data Input",
  "keywords": [
    "text field",
    "input",
    "form",
    "password",
    "email"
  ],
  "usage": {
    "description": "A text field lets the user type and change text.",
    "bestPractices": [],
    "accessibility": [
      {
        "name": "Label",
        "category": "Content",
        "criterion": "3.3.2 Labels or Instructions",
        "requirement": "visible label",
        "description": "Every input has words that say what to enter. A placeholder alone is not a label."
      }
    ],
    "anatomy": [
      {
        "name": "Container",
        "required": true,
        "description": "Filled or outlined."
      },
      {
        "name": "Label",
        "required": true,
        "description": "Says what to type."
      },
      {
        "name": "Input",
        "required": true,
        "description": "The text."
      },
      {
        "name": "Supporting text",
        "required": false,
        "description": "Help or the error."
      }
    ]
  },
  "props": [
    {
      "name": "state",
      "type": "TextFieldState",
      "description": "The text. Create it with rememberTextFieldState().",
      "required": true
    },
    {
      "name": "enabled",
      "type": "boolean",
      "description": "When false, the part is greyed out and ignores the user.",
      "default": "true"
    },
    {
      "name": "label",
      "type": "@Composable TextFieldLabelScope.() -> Unit",
      "description": "Says what to type."
    },
    {
      "name": "placeholder",
      "type": "@Composable () -> Unit",
      "description": "Hint text while empty."
    },
    {
      "name": "supportingText",
      "type": "@Composable () -> Unit",
      "description": "Help or the error reason below."
    },
    {
      "name": "isError",
      "type": "boolean",
      "description": "Shows the error style.",
      "default": "false"
    },
    {
      "name": "keyboardOptions",
      "type": "KeyboardOptions",
      "description": "The keyboard type and action, like KeyboardType.Email.",
      "default": "KeyboardOptions.Default"
    },
    {
      "name": "titleKey",
      "type": "LocalizedStringKey",
      "description": "Says what to type. VoiceOver reads it.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "text",
      "type": "Binding<String>",
      "description": "The text.",
      "platform": "ios",
      "required": true
    },
    {
      "name": "prompt",
      "type": "Text?",
      "description": "Hint text while empty.",
      "platform": "ios",
      "default": "nil"
    },
    {
      "name": "axis",
      "type": "Axis",
      "description": "Pass .vertical to let the field grow to more lines.",
      "platform": "ios"
    }
  ],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "TextFieldLink", "note": "not on iOS. Apple: \"A control that requests text input from the user when pressed.\"", "status": "unavailable-ios", "replacement": "TextField"},
        {"name": "SecureField", "note": "iOS 13.0. Apple: \"A control into which people securely enter private text.\""},
        {"name": "TextEditor", "note": "iOS 14.0. Apple: \"A view that can display and edit long-form text.\""},
        {"name": "TextInputBorderShape", "note": "iOS 27.0. Apple: \"A shape used to draw the border of a text input control.\""},
        {"name": "onSubmit", "note": "`.onSubmit(of:_:)`, iOS 15.0. Apple: \"Adds an action to perform when the user submits a value to this view.\""},
        {"name": "submitLabel", "note": "`.submitLabel(_:)`, iOS 15.0. Apple: \"Sets the submit label for this view.\""},
        {"name": "submitScope", "note": "`.submitScope(_:)`, iOS 15.0. Apple: \"Prevents submission triggers originating from this view to invoke a submission action configured by a submission modifier higher up in the view hierarchy.\""},
        {"name": "textEditorStyle", "note": "`.textEditorStyle(_:)`, iOS 17.0. Apple: \"Sets the style for text editors within this view.\""},
        {"name": "textFieldStyle", "note": "`.textFieldStyle(_:)`, iOS 13.0. Apple: \"Sets the style for text fields within this view.\""},
        {"name": "autocorrectionDisabled", "note": "`.autocorrectionDisabled(_:)`, iOS 13.0. Apple: \"Sets whether to disable autocorrection for this view.\""},
        {"name": "findDisabled", "note": "`.findDisabled(_:)`, iOS 16.0. Apple: \"Prevents find and replace operations in a text editor.\""},
        {"name": "findNavigator", "note": "`.findNavigator(isPresented:)`, iOS 16.0. Apple: \"Programmatically presents the find and replace interface for text editor views.\""},
        {"name": "keyboardType", "note": "`.keyboardType(_:)`, iOS 13.0. Apple: \"Sets the keyboard type for this view.\""},
        {"name": "replaceDisabled", "note": "`.replaceDisabled(_:)`, iOS 16.0. Apple: \"Prevents replace operations in a text editor.\""},
        {"name": "textContentType", "note": "`.textContentType(_:)`, iOS 13.0. Apple: \"Sets the text content type for this view, which the system uses to offer suggestions while the user enters text on an iOS or tvOS device.\""},
        {"name": "textInputAutocapitalization", "note": "`.textInputAutocapitalization(_:)`, iOS 15.0. Apple: \"Sets how often the shift key in the keyboard is automatically enabled.\""},
        {"name": "textInputBorderShape", "note": "`.textInputBorderShape(_:)`, iOS 27.0. Apple: \"Sets the border shape for text input controls in the view hierarchy.\""},
        {"name": "textInputCompletion", "note": "`.textInputCompletion(_:)`, not on iOS. Apple: \"Associates a fully formed string with the value of this view when used as a text input suggestion\"", "status": "unavailable-ios", "replacement": "searchCompletion"},
        {"name": "textInputFormattingControlVisibility", "note": "`.textInputFormattingControlVisibility(_:for:)`, iOS 26.0. Apple: \"Specifies which system text formatting controls are available for people to format text.\""},
        {"name": "textInputSuggestions", "note": "`.textInputSuggestions(_:)`, not on iOS. Apple: \"Configures the text input suggestions for this view.\"", "status": "unavailable-ios", "replacement": "searchSuggestions"},
        {"name": "writingToolsAffordanceVisibility", "note": "`.writingToolsAffordanceVisibility(_:)`, iOS 18.4. Apple: \"Specifies whether the system should show the Writing Tools affordance for text input views affected by the environment.\""},
        {"name": "writingToolsBehavior", "note": "`.writingToolsBehavior(_:)`, iOS 18.0. Apple: \"Specifies the Writing Tools behavior for text and text input in the environment.\""},
        {"name": "autocapitalization", "note": "`.autocapitalization(_:)`, iOS 13.0. Apple: \"Sets whether to apply auto-capitalization to this view.\"", "status": "deprecated", "replacement": "textInputAutocapitalization"},
        {"name": "disableAutocorrection", "note": "`.disableAutocorrection(_:)`, iOS 13.0. Apple: \"Sets whether to disable autocorrection for this view.\"", "status": "deprecated", "replacement": "autocorrectionDisabled"}
      ]
    },
    "android": {
      "family": "ExposedDropdownMenu",
      "variants": [
        {
          "name": "TextFieldDefaults.Container",
          "note": "The default container (fill and indicator line) of a filled field. Use it inside DecorationBox only when you build on BasicTextField."
        },
        {
          "name": "TextFieldDefaults.DecorationBox",
          "note": "The label, icons and container of a filled field around a BasicTextField. Use it only when TextField cannot do the job."
        },
        {
          "name": "TextFieldDefaults.ContainerBox",
          "note": "The old name of the filled container.",
          "status": "deprecated",
          "replacement": "TextFieldDefaults.Container (Google: \"Renamed to TextFieldDefaults.Container\")"
        },
        {
          "name": "ExposedDropdownMenuBox",
          "note": "Holds a read-only or editable text field and the menu of choices that opens under it. Use it to pick one value from a list."
        },
        {
          "name": "ExposedDropdownMenuBoxScope.ExposedDropdownMenu",
          "note": "The menu inside ExposedDropdownMenuBox. It is as wide as the field and opens under it."
        },
        {
          "name": "ExposedDropdownMenuDefaults.TrailingIcon",
          "note": "The arrow icon at the end of the field. It turns when the menu opens."
        }
      ],
      "supporting": [
        {
          "name": "TextFieldDefaults",
          "use": "Default colours, shapes, sizes, padding and the decorator for filled fields. Make colours with TextFieldDefaults.colors()."
        },
        {
          "name": "TextFieldColors",
          "use": "The text, container, cursor, icon, label and indicator colours of a field in each state, including error."
        },
        {
          "name": "TextFieldLabelPosition",
          "use": "Where the label sits: Attached (inside the field, it moves up when the field has focus or text) or Above (always above the field)."
        },
        {
          "name": "TextFieldLabelScope",
          "use": "The scope of the label slot. Its labelMinimizedProgress says how far the label has moved to its small form."
        },
        {
          "name": "ExposedDropdownMenuBoxScope",
          "use": "The scope inside ExposedDropdownMenuBox. Put menuAnchor on the text field so the menu opens from it."
        },
        {
          "name": "ExposedDropdownMenuAnchorType",
          "use": "What the anchor is, for menuAnchor: PrimaryNotEditable (a read-only field), PrimaryEditable (a field the user types in) or SecondaryEditable (an icon inside an editable field)."
        },
        {
          "name": "ExposedDropdownMenuDefaults",
          "use": "Default colours, padding and the trailing icon for exposed dropdown menus."
        }
      ]
    }
  }
};
