/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "collection-view",
  "displayName": "Collection view",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Collection view",
  "category": "Table & List",
  "keywords": [
    "collection view",
    "grid",
    "compositional layout",
    "uicollectionview"
  ],
  "usage": {
    "description": "A collection view shows many items in a custom layout."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use UIKit's UICollectionView only when a SwiftUI List, Grid or lazy grid cannot do the job: https://developer.apple.com/documentation/uikit/uicollectionview."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "UICollectionView",
          "use": "iOS 6.0. Apple: \"An object that manages an ordered collection of data items and presents them using customizable layouts.\""
        },
        {
          "name": "UICollectionViewCompositionalLayout",
          "use": "iOS 13.0. Apple: \"A layout object that lets you combine items in highly adaptive and flexible visual arrangements.\""
        },
        {
          "name": "UICollectionViewDiffableDataSource",
          "use": "iOS 13.0. Apple: \"The object you use to manage data and provide cells for a collection view.\""
        }
      ]
    }
  }
};
