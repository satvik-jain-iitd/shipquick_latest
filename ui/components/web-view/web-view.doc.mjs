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
      "family": "web-view",
      "variants": [
        {"name": "webViewBackForwardNavigationGestures", "note": "`.webViewBackForwardNavigationGestures(_:)`, iOS 26.0. Apple: \"Determines whether horizontal swipe gestures trigger backward and forward page navigation.\""},
        {"name": "webViewContentBackground", "note": "`.webViewContentBackground(_:)`, iOS 26.0. Apple: \"Specifies the visibility of the webpage’s natural background color within this view.\""},
        {"name": "webViewContextMenu", "note": "`.webViewContextMenu(menu:)`, not on iOS. Apple: \"Adds an item-based context menu to a WebView, replacing the default set of context menu items.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (replaces a WebView's menu on Mac only; Apple offers it on macOS only)"},
        {"name": "webViewElementFullscreenBehavior", "note": "`.webViewElementFullscreenBehavior(_:)`, iOS 26.0. Apple: \"Determines whether a web view can display content full screen.\""},
        {"name": "webViewLinkPreviews", "note": "`.webViewLinkPreviews(_:)`, iOS 26.0. Apple: \"Determines whether pressing a link displays a preview of the destination for the link.\""},
        {"name": "webViewMagnificationGestures", "note": "`.webViewMagnificationGestures(_:)`, iOS 26.0. Apple: \"Determines whether magnify gestures change the view’s magnification.\""},
        {"name": "webViewOnScrollGeometryChange", "note": "`.webViewOnScrollGeometryChange(for:of:action:)`, iOS 26.0. Apple: \"Adds an action to be performed when a value, created from a scroll geometry, changes.\""},
        {"name": "webViewScrollInputBehavior", "note": "`.webViewScrollInputBehavior(_:for:)`, iOS 26.0. Apple: \"Enables or disables scrolling in web views when using particular inputs.\""},
        {"name": "webViewScrollPosition", "note": "`.webViewScrollPosition(_:)`, iOS 26.0. Apple: \"Associates a binding to a scroll position with the web view.\""},
        {"name": "webViewTextSelection", "note": "`.webViewTextSelection(_:)`, iOS 26.0. Apple: \"Determines whether to allow people to select or otherwise interact with text.\""},
        {"name": "onWebViewImmersiveEnvironmentRequest", "note": "`.onWebViewImmersiveEnvironmentRequest(shouldAllow:present:dismiss:)`, not on iOS. Apple: \"Manages the lifecycle of immersive environments requested by websites.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS volume or immersive space; iOS has no 3D space around the app)"}
      ],
      "supporting": [
        {"name": "WebView", "use": "iOS 26.0. Apple: \"A view that displays some web content.\""},
        {"name": "WebPage", "use": "iOS 26.0. Apple: \"An object that controls and manages the behavior of interactive web content.\""},
        {"name": "WKWebView", "use": "iOS 8.0. Apple: \"An object that displays interactive web content, such as for an in-app browser.\""}
      ]
    }
  }
};
