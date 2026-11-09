/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Grid",
  "displayName": "Grid",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Grid",
  "category": "Layout",
  "keywords": [
    "grid",
    "lazy grid",
    "columns",
    "rows",
    "gallery"
  ],
  "usage": {
    "description": "Grid places views in rows and columns. Lazy grids make only the cells on screen. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "Grid", "note": "iOS 16.0. Apple: \"A container view that arranges other views in a two dimensional layout.\""},
        {"name": "GridRow", "note": "iOS 16.0. Apple: \"A horizontal row in a two dimensional grid container.\""},
        {"name": "LazyHGrid", "note": "iOS 14.0. Apple: \"A container view that arranges its child views in a grid that grows horizontally, creating items only as needed.\""},
        {"name": "LazyVGrid", "note": "iOS 14.0. Apple: \"A container view that arranges its child views in a grid that grows vertically, creating items only as needed.\""},
        {"name": "gridCellAnchor", "note": "`.gridCellAnchor(_:)`, iOS 16.0. Apple: \"Specifies a custom alignment anchor for a view that acts as a grid cell.\""},
        {"name": "gridCellColumns", "note": "`.gridCellColumns(_:)`, iOS 16.0. Apple: \"Tells a view that acts as a cell in a grid to span the specified number of columns.\""},
        {"name": "gridCellUnsizedAxes", "note": "`.gridCellUnsizedAxes(_:)`, iOS 16.0. Apple: \"Asks grid layouts not to offer the view extra size in the specified axes.\""},
        {"name": "gridColumnAlignment", "note": "`.gridColumnAlignment(_:)`, iOS 16.0. Apple: \"Overrides the default horizontal alignment of the grid column that the view appears in.\""}
      ]
    }
  }
};
