/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "FileDialogs",
  "displayName": "File dialogs",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "FileDialogs",
  "category": "Overlay",
  "keywords": [
    "file importer",
    "file exporter",
    "file mover",
    "file dialog",
    "open file",
    "save file"
  ],
  "usage": {
    "description": "Modifiers that present the system file dialogs: import, export and move a file, plus the options of those dialogs. Each entry is a SwiftUI view modifier. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "File dialogs",
      "variants": [
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
        {"name": "fileMover", "note": "`.fileMover(isPresented:file:onCompletion:)`, iOS 14.0. Apple: \"Presents a system dialog for allowing the user to move an existing file to a new location.\""}
      ]
    }
  }
};
