/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "PresentationModifiers",
  "displayName": "Presentation modifiers",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "PresentationModifiers",
  "category": "Overlay",
  "keywords": [
    "present",
    "file importer",
    "photos picker",
    "store sheet",
    "modal"
  ],
  "usage": {
    "description": "Modifiers that present system screens, like a file picker or a photos picker. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Presentation modifiers",
      "variants": [
        {"name": "activityBackgroundTint", "note": "`.activityBackgroundTint(_:)`, iOS 16.0. Apple: \"Sets the tint color for the background of a Live Activity that appears on the Lock Screen.\""},
        {"name": "activitySystemActionForegroundColor", "note": "`.activitySystemActionForegroundColor(_:)`, iOS 16.1. Apple: \"The text color for the auxiliary action button that the system shows next to a Live Activity on the Lock Screen.\""},
        {"name": "appStoreMerchandising", "note": "`.appStoreMerchandising(isPresented:kind:onDismiss:)`, iOS 26.0. Apple: \"Display a merchandising view.\""},
        {"name": "appStoreOverlay", "note": "`.appStoreOverlay(isPresented:configuration:)`, iOS 14.0. Apple: \"Presents a StoreKit overlay when a given condition is true.\""},
        {"name": "certificateSheet", "note": "`.certificateSheet(trust:title:message:help:)`, iOS 18.4. Apple: \"Displays a certificate sheet using the provided certificate trust.\""},
        {"name": "contactAccessButtonCaption", "note": "`.contactAccessButtonCaption(_:)`, iOS 18.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contactaccessbuttoncaption(_:)"},
        {"name": "contactAccessButtonStyle", "note": "`.contactAccessButtonStyle(_:)`, iOS 18.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/contactaccessbuttonstyle(_:)"},
        {"name": "contactAccessPicker", "note": "`.contactAccessPicker(isPresented:completionHandler:)`, iOS 18.0. Apple: \"Modally present UI which allows the user to select which contacts your app has access to.\""},
        {"name": "documentBrowserContextMenu", "note": "`.documentBrowserContextMenu(_:)`, iOS 18.1. Apple: \"Adds to a `DocumentLaunchView` actions that accept a list of selected files as their parameter.\""},
        {"name": "documentLaunchSubtitle", "note": "`.documentLaunchSubtitle(_:)`, iOS 27.0. Apple: \"Sets the subtitle displayed beneath the title on the document launch card.\""},
        {"name": "documentLaunchTitle", "note": "`.documentLaunchTitle(_:)`, iOS 27.0. Apple: \"Sets the title displayed on the document launch card.\""},
        {"name": "familyActivityPicker", "note": "`.familyActivityPicker(isPresented:selection:)`, iOS 15.0. Apple: \"Presents an activity picker view as a sheet.\""},
        {"name": "fileDialogBrowserOptions", "note": "`.fileDialogBrowserOptions(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter`, `fileImporter`, or `fileMover` to provide a refined URL search experience: include or exclude hidden files, allow searching by tag, etc.\""},
        {"name": "fileDialogConfirmationLabel", "note": "`.fileDialogConfirmationLabel(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter`, `fileImporter`, or `fileMover` with a custom confirmation button label.\""},
        {"name": "fileDialogCustomizationID", "note": "`.fileDialogCustomizationID(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter`, `fileImporter`, or `fileMover` to persist and restore the file dialog configuration.\""},
        {"name": "fileDialogDefaultDirectory", "note": "`.fileDialogDefaultDirectory(_:)`, iOS 17.0. Apple: \"Configures the `fileExporter`, `fileImporter`, or `fileMover` to open with the specified default directory.\""},
        {"name": "fileDialogImportsUnresolvedAliases", "note": "`.fileDialogImportsUnresolvedAliases(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter`, `fileImporter`, or `fileMover` behavior when a user chooses an alias.\""},
        {"name": "fileDialogMessage", "note": "`.fileDialogMessage(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter`, `fileImporter`, or `fileMover` with a custom message that is presented to the user, similar to a title.\""},
        {"name": "fileDialogURLEnabled", "note": "`.fileDialogURLEnabled(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileImporter` or `fileMover` to conditionally disable presented URLs.\""},
        {"name": "fileExporter", "note": "`.fileExporter(isPresented:item:contentTypes:defaultFilename:onCompletion:onCancellation:)`, iOS 17.0. Apple: \"Presents a system dialog allowing the user to export a `Transferable` item to a file on disk.\""},
        {"name": "fileExporterFilenameLabel", "note": "`.fileExporterFilenameLabel(_:)`, iOS 17.0. Apple: \"On macOS, configures the `fileExporter` with a label for the file name field.\""},
        {"name": "fileImporter", "note": "`.fileImporter(isPresented:allowedContentTypes:allowsMultipleSelection:onCompletion:)`, iOS 14.0. Apple: \"Presents a system dialog for allowing the user to import multiple files.\""},
        {"name": "fileMover", "note": "`.fileMover(isPresented:file:onCompletion:)`, iOS 14.0. Apple: \"Presents a system dialog for allowing the user to move an existing file to a new location.\""},
        {"name": "foveatedStreamingPauseSheet", "note": "`.foveatedStreamingPauseSheet(session:)`, not on iOS. Apple: \"Tells the system to present a sheet with controls for resuming or ending the foveated streaming session when it pauses.\"", "status": "unavailable-ios", "replacement": "nothing on iOS (visionOS foveated streaming only)"},
        {"name": "gameSaveSyncingAlert", "note": "`.gameSaveSyncingAlert(directory:finishedLoading:)`, iOS 26.0. Apple: \"Presents a modal view while the game synced directory loads.\""},
        {"name": "manageSubscriptionsSheet", "note": "`.manageSubscriptionsSheet(isPresented:)`, iOS 15.0. Apple: \"Presents the App Store sheet for managing subscriptions.\""},
        {"name": "musicSubscriptionOffer", "note": "`.musicSubscriptionOffer(isPresented:options:onLoadCompletion:)`, iOS 15.0. Apple: \"Initiates the process of presenting a sheet with subscription offers for Apple Music when the `isPresented` binding is `true`.\""},
        {"name": "offerCodeRedemption", "note": "`.offerCodeRedemption(options:isPresented:onCompletion:)`, iOS 27.0. Apple: \"Presents a sheet that enables customers to redeem offer codes that you configure in App Store Connect.\""},
        {"name": "photosPicker", "note": "`.photosPicker(isPresented:selection:matching:preferredItemEncoding:)`, iOS 16.0. Apple: \"Presents a Photos picker that selects a `PhotosPickerItem`.\""},
        {"name": "photosPickerAccessoryVisibility", "note": "`.photosPickerAccessoryVisibility(_:edges:)`, iOS 17.0. Apple: \"Sets the accessory visibility of the Photos picker. Accessories include anything between the content and the edge, like the navigation bar or the sidebar.\""},
        {"name": "photosPickerDisabledCapabilities", "note": "`.photosPickerDisabledCapabilities(_:)`, iOS 17.0. Apple: \"Disables capabilities of the Photos picker.\""},
        {"name": "photosPickerSearchText", "note": "`.photosPickerSearchText(_:)`, iOS 27.0. Apple: \"Sets search text of the Photos picker.\""},
        {"name": "photosPickerStyle", "note": "`.photosPickerStyle(_:)`, iOS 17.0. Apple: \"Sets the mode of the Photos picker.\""},
        {"name": "photosReferenceImageViewer", "note": "`.photosReferenceImageViewer(asset:onProcessingCompletion:)`, iOS 27.0. Apple: \"Presents an image viewer for an asset in a photo library that contains Apple Reference Image data when `asset` is set.\""},
        {"name": "photosSharedAlbumCreationSheet", "note": "`.photosSharedAlbumCreationSheet(isPresented:defaultTitle:defaultSharingPolicy:photoLibrary:onCompletion:)`, iOS 27.0. Apple: \"Presents a view for allowing the user to create a new shared album.\""},
        {"name": "photosSharedAlbumCustomizationSheet", "note": "`.photosSharedAlbumCustomizationSheet(isPresented:albumIdentifier:photoLibrary:onCompletion:)`, iOS 27.0. Apple: \"Presents a view for allowing the user to customize a specified shared album.\""},
        {"name": "photosSharedAlbumPostingSheet", "note": "`.photosSharedAlbumPostingSheet(isPresented:items:defaultAlbumIdentifier:photoLibrary:completion:)`, iOS 27.0. Apple: \"Presents an “Add to Shared Album” sheet that allows the user to post the given items to a shared album.\""},
        {"name": "quickLookPreview", "note": "`.quickLookPreview(_:)`, iOS 14.0. Apple: \"Presents a Quick Look preview of the contents of a single URL.\""},
        {"name": "recordingEditor", "note": "`.recordingEditor(_:)`, iOS 27.0. Apple: \"Presents the recording editor for the given recording URL.\""},
        {"name": "refundRequestSheet", "note": "`.refundRequestSheet(for:isPresented:onDismiss:)`, iOS 15.0. Apple: \"Display the refund request sheet for the given transaction.\""},
        {"name": "translationPresentation", "note": "`.translationPresentation(isPresented:text:attachmentAnchor:arrowEdge:replacementAction:)`, iOS 17.4. Apple: \"Presents a translation popover when a given condition is true.\""},
        {"name": "translationTask", "note": "`.translationTask(_:action:)`, iOS 18.0. Apple: \"Adds a task to perform before this view appears or when the translation configuration changes.\""},
        {"name": "postToPhotosSharedAlbumSheet", "note": "`.postToPhotosSharedAlbumSheet(isPresented:items:photoLibrary:defaultAlbumIdentifier:completion:)`, iOS 26.0. Apple: \"Presents an “Add to Shared Album” sheet that allows the user to post the given items to a shared album.\"", "status": "deprecated", "replacement": "View"}
      ]
    }
  }
};
