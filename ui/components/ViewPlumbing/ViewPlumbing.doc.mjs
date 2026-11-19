/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "ViewPlumbing",
  "displayName": "View plumbing",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "ViewPlumbing",
  "category": "Utility",
  "keywords": [
    "any view",
    "empty view",
    "tuple view",
    "subview",
    "plumbing",
    "type erasure"
  ],
  "usage": {
    "description": "These types hold views together. They draw nothing of their own. SwiftUI makes most of them for you. Use the SwiftUI type as Apple ships it. Do not redraw it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "ViewPlumbing",
      "variants": [
        {"name": "AnyView", "note": "iOS 13.0. Apple: \"A type-erased view.\""},
        {"name": "DebugReplaceableView", "note": "iOS 26.0. Apple: \"Erases view opaque result types in debug builds.\""},
        {"name": "EditableCollectionContent", "note": "iOS 16.0. Apple: \"An opaque wrapper view that adds editing capabilities to a row in a list.\""},
        {"name": "EmptyView", "note": "iOS 13.0. Apple: \"A view that doesn’t contain any content.\""},
        {"name": "EquatableView", "note": "iOS 13.0. Apple: \"A view type that compares itself against its previous value and prevents its child updating if its new value is the same as its old value.\""},
        {"name": "GroupElementsOfContent", "note": "iOS 18.0. Apple: \"Transforms the subviews of a given view into a resulting content view.\""},
        {"name": "GroupSectionsOfContent", "note": "iOS 18.0. Apple: \"Transforms the sections of a given view into a resulting content view.\""},
        {"name": "LabeledControlGroupContent", "note": "iOS 16.0. Apple: \"A view that represents the body of a control group with a specified label.\""},
        {"name": "LabeledToolbarItemGroupContent", "note": "iOS 16.0. Apple: \"A view that represents the view of a toolbar item group with a specified label.\""},
        {"name": "ModifiedContent", "note": "iOS 13.0. Apple: \"A value with a modifier applied to it.\""},
        {"name": "OutlineSubgroupChildren", "note": "iOS 14.0. Apple: \"A type-erased view representing the children in an outline subgroup.\""},
        {"name": "PlaceholderContentView", "note": "iOS 17.0. Apple: \"A placeholder used to construct an inline modifier, transition, or other helper type.\""},
        {"name": "PresentedWindowContent", "note": "iOS 16.0. Apple: \"A view that represents the content of a presented window.\""},
        {"name": "PreviewModifierContent", "note": "iOS 18.0. Apple: \"The type-erased content of a preview.\""},
        {"name": "SubscriptionView", "note": "iOS 13.0. Apple: \"A view that subscribes to a publisher with an action.\""},
        {"name": "Subview", "note": "iOS 18.0. Apple: \"An opaque value representing a subview of another view.\""},
        {"name": "SubviewsCollection", "note": "iOS 18.0. Apple: \"An opaque collection representing the subviews of view.\""},
        {"name": "SubviewsCollectionSlice", "note": "iOS 18.0. Apple: \"A slice of a SubviewsCollection.\""},
        {"name": "TupleContent", "note": "iOS 26.0. Apple: \"Content created from a tuple of content to be treated as siblings.\""},
        {"name": "TupleView", "note": "iOS 13.0. Apple: \"A View created from a swift tuple of View values.\""},
        {"name": "modifier", "note": "`.modifier(_:)`, iOS 13.0. Apple: \"Applies a modifier to a view and returns a new view.\""}
      ]
    }
  }
};
