/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "DragAndDrop",
  "displayName": "Drag and drop",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "DragAndDrop",
  "category": "Utility",
  "keywords": [
    "drag",
    "drop",
    "draggable",
    "drop destination",
    "reorder",
    "item provider"
  ],
  "usage": {
    "description": "Modifiers that start a drag, take a drop, or reorder items. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it.",
    "bestPractices": [
      {
        "guidance": true,
        "description": "Use `.draggable` and `.dropDestination` with Transferable types; keep `.onDrag` and `.onDrop` for item providers only."
      }
    ]
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Drag and drop",
      "variants": [
        {"name": "draggable", "note": "`.draggable(_:containerNamespace:_:)`, iOS 27.0. Apple: \"Activates this view as the source of a drag and drop operation, allowing to provide optional identifiable payload and specify the namespace of the drag container this view belongs to.\""},
        {"name": "dragConfiguration", "note": "`.dragConfiguration(_:)`, iOS 27.0. Apple: \"Configures a drag session.\""},
        {"name": "dragContainer", "note": "`.dragContainer(for:in:_:)`, iOS 27.0. Apple: \"A container with draggable views where the drag payload is based on multiple identifiers of dragged items.\""},
        {"name": "dragContainerSelection", "note": "`.dragContainerSelection(_:containerNamespace:)`, iOS 27.0. Apple: \"Provides multiple item selection support for drag containers.\""},
        {"name": "dragPreviewsFormation", "note": "`.dragPreviewsFormation(_:)`, not on iOS. Apple: \"Describes the way dragged previews are visually composed.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac drag previews only; iOS shows the system drag preview)"},
        {"name": "dropConfiguration", "note": "`.dropConfiguration(_:)`, iOS 27.0. Apple: \"Configures a drop session.\""},
        {"name": "dropDestination", "note": "`.dropDestination(for:isEnabled:action:)`, iOS 26.0. Apple: \"Defines the destination of a drag and drop operation that provides a drop operation proposal and handles the dropped content with a closure that you specify.\""},
        {"name": "dropPreviewsFormation", "note": "`.dropPreviewsFormation(_:)`, not on iOS. Apple: \"Describes the way previews for a drop are composed.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (Mac drop previews only; iOS shows the system drop preview)"},
        {"name": "itemProvider", "note": "`.itemProvider(_:)`, iOS 13.0. Apple: \"Provides a closure that vends the drag representation to be used for a particular data element.\""},
        {"name": "onDrag", "note": "`.onDrag(_:)`, iOS 13.4. Apple: \"Activates this view as the source of a drag and drop operation.\""},
        {"name": "onDragSessionUpdated", "note": "`.onDragSessionUpdated(_:)`, iOS 27.0. Apple: \"Specifies an action to perform on each update of an ongoing dragging operation activated by `draggable(_:)` or anther drag modifiers.\""},
        {"name": "onDrop", "note": "`.onDrop(of:delegate:)`, iOS 14.0. Apple: \"Defines the destination of a drag and drop operation using behavior controlled by the delegate that you provide.\""},
        {"name": "onDropSessionUpdated", "note": "`.onDropSessionUpdated(_:)`, iOS 27.0. Apple: \"Specifies an action to perform on each update of an ongoing drop operation activated by `dropDestination(_:)` or other drop modifiers.\""},
        {"name": "reorderContainer", "note": "`.reorderContainer(for:isEnabled:move:)`, iOS 27.0. Apple: \"Defines a container of reorderable views.\""},
        {"name": "springLoadingBehavior", "note": "`.springLoadingBehavior(_:)`, iOS 17.0. Apple: \"Sets the spring loading behavior this view.\""}
      ]
    }
  }
};
