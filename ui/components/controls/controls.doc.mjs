/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "controls",
  "displayName": "Controls",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Controls",
  "category": "Action",
  "keywords": [
    "control center",
    "controls",
    "lock screen control",
    "action button",
    "control widget"
  ],
  "usage": {
    "description": "A control is a button or toggle of the app in Control Center, on the Lock Screen or on the Action button."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use WidgetKit controls: https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "ControlWidget",
          "use": "iOS 18.0. Apple: \"The configuration and content of a control widget to display in system spaces such as Control Center, the Lock Screen, and the Action Button.\""
        },
        {
          "name": "ControlWidgetButton",
          "use": "iOS 18.0. Apple: \"A control template representing a button.\""
        },
        {
          "name": "ControlWidgetToggle",
          "use": "iOS 18.0. Apple: \"A control template representing a toggle.\""
        }
      ]
    }
  }
};
