/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "StateModifiers",
  "displayName": "State modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "StateModifiers",
  "category": "Utility",
  "keywords": [
    "environment",
    "preference",
    "state",
    "id",
    "tag",
    "model container"
  ],
  "usage": {
    "description": "Modifiers that pass data down or up the view tree. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "variants": [
        {"name": "anchorPreference", "note": "`.anchorPreference(key:value:transform:)`, iOS 13.0. Apple: \"Sets a value for the specified preference key, the value is a function of a geometry value tied to the current coordinate space, allowing readers of the value to convert the geometry to their local coordinates.\""},
        {"name": "backgroundPreferenceValue", "note": "`.backgroundPreferenceValue(_:_:)`, iOS 13.0. Apple: \"Reads the specified preference value from the view, using it to produce a second view that is applied as the background of the original view.\""},
        {"name": "defaultAppStorage", "note": "`.defaultAppStorage(_:)`, iOS 14.0. Apple: \"The default store used by `AppStorage` contained within the view.\""},
        {"name": "environment", "note": "`.environment(_:_:)`, iOS 13.0. Apple: \"Sets the environment value of the specified key path to the given value.\""},
        {"name": "environmentObject", "note": "`.environmentObject(_:)`, iOS 13.0. Apple: \"Supplies an observable object to a view’s hierarchy.\""},
        {"name": "equatable", "note": "`.equatable()`, iOS 13.0. Apple: \"Prevents the view from updating its child view when its new value is the same as its old value.\""},
        {"name": "id", "note": "`.id(_:)`, iOS 13.0. Apple: \"Binds a view’s identity to the given proxy value.\""},
        {"name": "modelContainer", "note": "`.modelContainer(_:)`, iOS 17.0. Apple: \"Sets the model container and associated model context in this view’s environment.\""},
        {"name": "modelContext", "note": "`.modelContext(_:)`, iOS 17.0. Apple: \"Sets the model context in this view’s environment.\""},
        {"name": "onPreferenceChange", "note": "`.onPreferenceChange(_:perform:)`, iOS 13.0. Apple: \"Adds an action to perform when the specified preference key’s value changes.\""},
        {"name": "overlayPreferenceValue", "note": "`.overlayPreferenceValue(_:_:)`, iOS 13.0. Apple: \"Reads the specified preference value from the view, using it to produce a second view that is applied as an overlay to the original view.\""},
        {"name": "preference", "note": "`.preference(key:value:)`, iOS 13.0. Apple: \"Sets a value for the given preference.\""},
        {"name": "tag", "note": "`.tag(_:includeOptional:)`, iOS 13.0. Apple: \"Sets the unique tag value of this view.\""},
        {"name": "transformAnchorPreference", "note": "`.transformAnchorPreference(key:value:transform:)`, iOS 13.0. Apple: \"Sets a value for the specified preference key, the value is a function of the key’s current value and a geometry value tied to the current coordinate space, allowing readers of the value to convert the geometry to their local coordinates.\""},
        {"name": "transformEnvironment", "note": "`.transformEnvironment(_:transform:)`, iOS 13.0. Apple: \"Transforms the environment value of the specified key path with the given function.\""},
        {"name": "transformPreference", "note": "`.transformPreference(_:_:)`, iOS 13.0. Apple: \"Applies a transformation to a preference value.\""}
      ]
    }
  }
};
