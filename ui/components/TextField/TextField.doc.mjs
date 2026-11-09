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
        {"name": "autocorrectionDisabled", "note": "`.autocorrectionDisabled(_:)`, iOS 13.0. Apple: \"Sets whether to disable autocorrection for this view.\""},
        {"name": "findDisabled", "note": "`.findDisabled(_:)`, iOS 16.0. Apple: \"Prevents find and replace operations in a text editor.\""},
        {"name": "findNavigator", "note": "`.findNavigator(isPresented:)`, iOS 16.0. Apple: \"Programmatically presents the find and replace interface for text editor views.\""},
        {"name": "keyboardType", "note": "`.keyboardType(_:)`, iOS 13.0. Apple: \"Sets the keyboard type for this view.\""},
        {"name": "replaceDisabled", "note": "`.replaceDisabled(_:)`, iOS 16.0. Apple: \"Prevents replace operations in a text editor.\""},
        {"name": "scrollDismissesKeyboard", "note": "`.scrollDismissesKeyboard(_:)`, iOS 16.0. Apple: \"Configures the behavior in which scrollable content interacts with the software keyboard.\""},
        {"name": "textContentType", "note": "`.textContentType(_:)`, iOS 13.0. Apple: \"Sets the text content type for this view, which the system uses to offer suggestions while the user enters text on an iOS or tvOS device.\""},
        {"name": "textInputAutocapitalization", "note": "`.textInputAutocapitalization(_:)`, iOS 15.0. Apple: \"Sets how often the shift key in the keyboard is automatically enabled.\""},
        {"name": "textInputBorderShape", "note": "`.textInputBorderShape(_:)`, iOS 27.0. Apple: \"Sets the border shape for text input controls in the view hierarchy.\""},
        {"name": "textInputCompletion", "note": "`.textInputCompletion(_:)`, not on iOS. Apple: \"Associates a fully formed string with the value of this view when used as a text input suggestion\"", "status": "unavailable-ios", "replacement": "searchCompletion"},
        {"name": "textInputFormattingControlVisibility", "note": "`.textInputFormattingControlVisibility(_:for:)`, iOS 26.0. Apple: \"Specifies which system text formatting controls are available for people to format text.\""},
        {"name": "textInputSuggestions", "note": "`.textInputSuggestions(_:)`, not on iOS. Apple: \"Configures the text input suggestions for this view.\"", "status": "unavailable-ios", "replacement": "searchSuggestions"},
        {"name": "writingToolsAffordanceVisibility", "note": "`.writingToolsAffordanceVisibility(_:)`, iOS 18.4. Apple: \"Specifies whether the system should show the Writing Tools affordance for text input views affected by the environment.\""},
        {"name": "writingToolsBehavior", "note": "`.writingToolsBehavior(_:)`, iOS 18.0. Apple: \"Specifies the Writing Tools behavior for text and text input in the environment.\""}
      ]
    }
  }
};
