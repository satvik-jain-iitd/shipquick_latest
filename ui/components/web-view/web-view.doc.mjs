/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "web-view",
  "displayName": "Web view",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Web view",
  "category": "Content",
  "keywords": [
    "web view",
    "browser",
    "html",
    "web page",
    "wkwebview"
  ],
  "usage": {
    "description": "A web view shows a web page inside the app."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use WebKit: https://developer.apple.com/documentation/webkit/wkwebview. On iOS 26 and later, SwiftUI code uses WebKit's WebView and WebPage. Before iOS 26, wrap WKWebView. To open a link in a browser instead, use Link."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "WebView",
          "use": "iOS 26.0. Apple: \"A view that displays some web content.\""
        },
        {
          "name": "WebPage",
          "use": "iOS 26.0. Apple: \"An object that controls and manages the behavior of interactive web content.\""
        },
        {
          "name": "WKWebView",
          "use": "iOS 8.0. Apple: \"An object that displays interactive web content, such as for an in-app browser.\""
        }
      ]
    }
  }
};
