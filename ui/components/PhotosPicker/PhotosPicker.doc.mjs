/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "PhotosPicker",
  "displayName": "Photos picker",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "PhotosPicker",
  "category": "Overlay",
  "keywords": [
    "photos picker",
    "photo library",
    "shared album",
    "pick photos",
    "photos ui"
  ],
  "usage": {
    "description": "Modifiers that present the system Photos picker and the shared album sheets from PhotosUI, and set the picker's look. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "PhotosPicker",
      "variants": [
        {"name": "photosPicker", "note": "`.photosPicker(isPresented:selection:matching:preferredItemEncoding:)`, iOS 16.0. Apple: \"Presents a Photos picker that selects a `PhotosPickerItem`.\""},
        {"name": "photosPickerAccessoryVisibility", "note": "`.photosPickerAccessoryVisibility(_:edges:)`, iOS 17.0. Apple: \"Sets the accessory visibility of the Photos picker. Accessories include anything between the content and the edge, like the navigation bar or the sidebar.\""},
        {"name": "photosPickerDisabledCapabilities", "note": "`.photosPickerDisabledCapabilities(_:)`, iOS 17.0. Apple: \"Disables capabilities of the Photos picker.\""},
        {"name": "photosPickerMetadataOptions", "note": "`.photosPickerMetadataOptions(_:)`, iOS 27.0. Apple: \"Sets metadata options for the Photos picker.\""},
        {"name": "photosPickerSearchText", "note": "`.photosPickerSearchText(_:)`, iOS 27.0. Apple: \"Sets search text of the Photos picker.\""},
        {"name": "photosPickerStyle", "note": "`.photosPickerStyle(_:)`, iOS 17.0. Apple: \"Sets the mode of the Photos picker.\""},
        {"name": "photosReferenceImageViewer", "note": "`.photosReferenceImageViewer(asset:onProcessingCompletion:)`, iOS 27.0. Apple: \"Presents an image viewer for an asset in a photo library that contains Apple Reference Image data when `asset` is set.\""},
        {"name": "photosSharedAlbumCreationSheet", "note": "`.photosSharedAlbumCreationSheet(isPresented:defaultTitle:defaultSharingPolicy:photoLibrary:onCompletion:)`, iOS 27.0. Apple: \"Presents a view for allowing the user to create a new shared album.\""},
        {"name": "photosSharedAlbumCustomizationSheet", "note": "`.photosSharedAlbumCustomizationSheet(isPresented:albumIdentifier:photoLibrary:onCompletion:)`, iOS 27.0. Apple: \"Presents a view for allowing the user to customize a specified shared album.\""},
        {"name": "photosSharedAlbumPostingSheet", "note": "`.photosSharedAlbumPostingSheet(isPresented:items:defaultAlbumIdentifier:photoLibrary:completion:)`, iOS 27.0. Apple: \"Presents an “Add to Shared Album” sheet that allows the user to post the given items to a shared album.\""},
        {"name": "postToPhotosSharedAlbumSheet", "note": "`.postToPhotosSharedAlbumSheet(isPresented:items:photoLibrary:defaultAlbumIdentifier:completion:)`, iOS 26.0. Apple: \"Presents an “Add to Shared Album” sheet that allows the user to post the given items to a shared album.\"", "status": "deprecated", "replacement": "View"}
      ]
    }
  }
};
