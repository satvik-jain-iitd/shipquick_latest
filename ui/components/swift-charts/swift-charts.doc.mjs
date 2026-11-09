/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "swift-charts",
  "displayName": "Swift Charts",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Swift Charts",
  "category": "Data Visualization",
  "keywords": [
    "chart",
    "graph",
    "bar chart",
    "line chart",
    "pie chart",
    "swift charts"
  ],
  "usage": {
    "description": "Charts show data as bars, lines, points or areas."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use Swift Charts, Apple's chart framework: https://developer.apple.com/documentation/charts. Build every chart from its marks. Do not draw a chart with shapes or Canvas."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "Chart",
          "use": "iOS 16.0. Apple: \"A SwiftUI view that displays a chart.\""
        },
        {
          "name": "BarMark",
          "use": "iOS 16.0. Apple: \"Chart content that represents data using bars.\""
        },
        {
          "name": "LineMark",
          "use": "iOS 16.0. Apple: \"Chart content that represents data using a sequence of connected line segments.\""
        },
        {
          "name": "PointMark",
          "use": "iOS 16.0. Apple: \"Chart content that represents data using points.\""
        },
        {
          "name": "AreaMark",
          "use": "iOS 16.0. Apple: \"Chart content that represents data using the area of one or more regions.\""
        },
        {
          "name": "RuleMark",
          "use": "iOS 16.0. Apple: \"Chart content that represents data using a single horizontal or vertical rule.\""
        },
        {
          "name": "SectorMark",
          "use": "iOS 17.0. Apple: \"A sector of a pie or donut chart, which shows how individual categories make up a meaningful total.\""
        }
      ]
    }
  }
};
