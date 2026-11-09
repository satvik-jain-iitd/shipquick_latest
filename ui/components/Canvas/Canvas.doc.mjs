/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Canvas",
  "displayName": "Canvas",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Canvas",
  "category": "Utility",
  "keywords": [
    "canvas",
    "drawing",
    "immediate mode",
    "custom drawing"
  ],
  "usage": {
    "description": "Canvas draws shapes, text and images by code, one frame at a time. App screens are built from library components, so app code does not draw its own UI. Canvas is for a chart or a game surface that no library component covers.",
    "bestPractices": [
      {
        "guidance": false,
        "description": "Do not use: Canvas. Use Shape types or a library component instead (rule 38: hand-drawn UI in app code is refused)."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Canvas",
      "variants": [
        {"name": "Canvas", "note": "iOS 15.0. Apple: \"A view type that supports immediate mode drawing.\""}
      ]
    }
  }
};
