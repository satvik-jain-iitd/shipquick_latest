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
      "variants": [
        {"name": "chart3DCameraProjection", "note": "`.chart3DCameraProjection(_:)`, iOS 26.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chart3dcameraprojection(_:)"},
        {"name": "chart3DPose", "note": "`.chart3DPose(_:)`, iOS 26.0. Apple: \"Associates a binding to be updated when the 3D chart’s pose is changed by an interaction.\""},
        {"name": "chart3DRenderingStyle", "note": "`.chart3DRenderingStyle(_:)`, not on iOS. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chart3drenderingstyle(_:)", "status": "unavailable-ios", "replacement": "nothing on iOS (a visionOS 26 render style for 3D charts; Apple offers it on visionOS only)"},
        {"name": "chartAngleSelection", "note": "`.chartAngleSelection(value:)`, iOS 17.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chartangleselection(value:)"},
        {"name": "chartBackground", "note": "`.chartBackground(alignment:content:)`, iOS 16.0. Apple: \"Adds a background to a view that contains a chart.\""},
        {"name": "chartForegroundStyleScale", "note": "`.chartForegroundStyleScale(_:)`, iOS 16.0. Apple: \"Configures the foreground style scale for charts.\""},
        {"name": "chartGesture", "note": "`.chartGesture(_:)`, iOS 17.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chartgesture(_:)"},
        {"name": "chartLegend", "note": "`.chartLegend(_:)`, iOS 16.0. Apple: \"Configures the legend for charts.\""},
        {"name": "chartLineStyleScale", "note": "`.chartLineStyleScale(_:)`, iOS 16.0. Apple: \"Configures the line style scale for charts.\""},
        {"name": "chartOverlay", "note": "`.chartOverlay(alignment:content:)`, iOS 16.0. Apple: \"Adds an overlay to a view that contains a chart.\""},
        {"name": "chartPlotStyle", "note": "`.chartPlotStyle(content:)`, iOS 16.0. Apple: \"Configures the plot area of charts.\""},
        {"name": "chartScrollableAxes", "note": "`.chartScrollableAxes(_:)`, iOS 17.0. Apple: \"Configures the scrollable behavior of charts in this view.\""},
        {"name": "chartScrollPosition", "note": "`.chartScrollPosition(initialX:)`, iOS 17.0. Apple: \"Sets the initial scroll position along the x-axis. Once the user scrolls the scroll view, the value provided to this modifier will have no effect.\""},
        {"name": "chartScrollTargetBehavior", "note": "`.chartScrollTargetBehavior(_:)`, iOS 17.0. Apple: \"Sets the scroll behavior of the scrollable chart.\""},
        {"name": "chartSymbolScale", "note": "`.chartSymbolScale(_:)`, iOS 16.0. Apple: \"Configures the symbol scale for charts.\""},
        {"name": "chartSymbolSizeScale", "note": "`.chartSymbolSizeScale(_:)`, iOS 16.0. Apple: \"Configures the symbol size scale for charts.\""},
        {"name": "chartXAxis", "note": "`.chartXAxis(_:)`, iOS 16.0. Apple: \"Sets the visibility of the x axis.\""},
        {"name": "chartXAxisLabel", "note": "`.chartXAxisLabel(_:position:alignment:spacing:)`, iOS 16.0. Apple: \"Adds x axis label for charts in the view.\""},
        {"name": "chartXAxisStyle", "note": "`.chartXAxisStyle(content:)`, iOS 17.0. Apple: \"Configures the x axis content of charts.\""},
        {"name": "chartXScale", "note": "`.chartXScale(domain:range:type:)`, iOS 16.0. Apple: \"Configures the x scale for charts.\""},
        {"name": "chartXSelection", "note": "`.chartXSelection(range:)`, iOS 17.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chartxselection(range:)"},
        {"name": "chartXVisibleDomain", "note": "`.chartXVisibleDomain(length:)`, iOS 17.0. Apple: \"Sets the length of the visible domain in the X dimension.\""},
        {"name": "chartYAxis", "note": "`.chartYAxis(_:)`, iOS 16.0. Apple: \"Sets the visibility of the y axis.\""},
        {"name": "chartYAxisLabel", "note": "`.chartYAxisLabel(_:position:alignment:spacing:)`, iOS 16.0. Apple: \"Adds y axis label for charts in the view.\""},
        {"name": "chartYAxisStyle", "note": "`.chartYAxisStyle(content:)`, iOS 17.0. Apple: \"Configures the y axis content of charts.\""},
        {"name": "chartYScale", "note": "`.chartYScale(domain:range:type:)`, iOS 16.0. Apple: \"Configures the y scale for charts.\""},
        {"name": "chartYSelection", "note": "`.chartYSelection(range:)`, iOS 17.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chartyselection(range:)"},
        {"name": "chartYVisibleDomain", "note": "`.chartYVisibleDomain(length:)`, iOS 17.0. Apple: \"Sets the length of the visible domain in the Y dimension.\""},
        {"name": "chartZAxis", "note": "`.chartZAxis(_:)`, iOS 26.0. Apple: \"Sets the visibility of the z axis.\""},
        {"name": "chartZAxisLabel", "note": "`.chartZAxisLabel(_:position:alignment:spacing:)`, iOS 26.0. Apple: \"Adds z axis label for charts in the view. It effects 3D charts only.\""},
        {"name": "chartZScale", "note": "`.chartZScale(domain:range:type:)`, iOS 26.0. Apple: \"Configures the z scale for 3D charts.\""},
        {"name": "chartZSelection", "note": "`.chartZSelection(range:)`, iOS 26.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/chartzselection(range:)"}
      ],
      "supporting": [
        {"name": "Chart", "use": "iOS 16.0. Apple: \"A SwiftUI view that displays a chart.\""},
        {"name": "BarMark", "use": "iOS 16.0. Apple: \"Chart content that represents data using bars.\""},
        {"name": "LineMark", "use": "iOS 16.0. Apple: \"Chart content that represents data using a sequence of connected line segments.\""},
        {"name": "PointMark", "use": "iOS 16.0. Apple: \"Chart content that represents data using points.\""},
        {"name": "AreaMark", "use": "iOS 16.0. Apple: \"Chart content that represents data using the area of one or more regions.\""},
        {"name": "RuleMark", "use": "iOS 16.0. Apple: \"Chart content that represents data using a single horizontal or vertical rule.\""},
        {"name": "SectorMark", "use": "iOS 17.0. Apple: \"A sector of a pie or donut chart, which shows how individual categories make up a meaningful total.\""}
      ]
    }
  }
};
