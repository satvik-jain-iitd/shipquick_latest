/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "InAppPurchase",
  "displayName": "In-app purchase",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "InAppPurchase",
  "category": "Utility",
  "keywords": [
    "store kit",
    "in-app purchase",
    "subscription",
    "product view",
    "subscription store"
  ],
  "usage": {
    "description": "Modifiers for StoreKit's store, product and subscription views: offers, tasks that load products and entitlements, and the look of the subscription store. Each entry is a SwiftUI view modifier from StoreKit. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "In-app purchase",
      "variants": [
        {"name": "currentEntitlementTask", "note": "`.currentEntitlementTask(for:priority:action:)`, iOS 17.0. Apple: \"Declares the view as dependent on the entitlement of an In-App Purchase product, and returns a modified view.\""},
        {"name": "inAppPurchaseOptions", "note": "`.inAppPurchaseOptions(_:)`, iOS 17.0. Apple: \"Add a function to call before initiating a purchase from StoreKit view within this view, providing a set of options for the purchase.\""},
        {"name": "onInAppPurchaseCompletion", "note": "`.onInAppPurchaseCompletion(perform:)`, iOS 17.0. Apple: \"Add an action to perform when a purchase initiated from a StoreKit view within this view completes.\""},
        {"name": "onInAppPurchaseStart", "note": "`.onInAppPurchaseStart(perform:)`, iOS 17.0. Apple: \"Add an action to perform when a user triggers the purchase button on a StoreKit view within this view.\""},
        {"name": "preferredSubscriptionOffer", "note": "`.preferredSubscriptionOffer(_:)`, iOS 18.0. Apple: \"Selects a subscription offer to apply to a purchase that a customer makes from a subscription store view, a store view, or a product view.\""},
        {"name": "preferredSubscriptionPricingTerms", "note": "`.preferredSubscriptionPricingTerms(_:)`, iOS 26.4. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/preferredsubscriptionpricingterms(_:)"},
        {"name": "productDescription", "note": "`.productDescription(_:)`, iOS 17.0. Apple: \"Configure the visibility of labels displaying an in-app purchase product description within the view.\""},
        {"name": "productIconBorder", "note": "`.productIconBorder()`, iOS 17.0. Apple: \"Adds a standard border to an in-app purchase product’s icon .\""},
        {"name": "productViewStyle", "note": "`.productViewStyle(_:)`, iOS 17.0. Apple: \"Sets the style for In-App Purchase product views within a view.\""},
        {"name": "storeButton", "note": "`.storeButton(_:for:)`, iOS 17.0. Apple: \"Specifies the visibility of auxiliary buttons that store view and subscription store view instances may use.\""},
        {"name": "storeProductsTask", "note": "`.storeProductsTask(for:priority:action:)`, iOS 17.0. Apple: \"Declares the view as dependent on a collection of In-App Purchase products and returns a modified view.\""},
        {"name": "storeProductTask", "note": "`.storeProductTask(for:priority:action:)`, iOS 17.0. Apple: \"Declares the view as dependent on an In-App Purchase product and returns a modified view.\""},
        {"name": "subscriptionIntroductoryOffer", "note": "`.subscriptionIntroductoryOffer(applyOffer:compactJWS:)`, iOS 26.0. Apple: \"Selects the introductory offer eligibility preference to apply to a purchase a customer makes from a subscription store view.\""},
        {"name": "subscriptionOfferViewButtonVisibility", "note": "`.subscriptionOfferViewButtonVisibility(_:for:)`, iOS 26.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/subscriptionofferviewbuttonvisibility(_:for:)"},
        {"name": "subscriptionOfferViewDetailAction", "note": "`.subscriptionOfferViewDetailAction(_:)`, iOS 26.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/subscriptionofferviewdetailaction(_:)"},
        {"name": "subscriptionOfferViewStyle", "note": "`.subscriptionOfferViewStyle(_:)`, iOS 26.0. Apple's page gives no summary: https://developer.apple.com/documentation/swiftui/view/subscriptionofferviewstyle(_:)"},
        {"name": "subscriptionPromotionalOffer", "note": "`.subscriptionPromotionalOffer(offer:compactJWS:)`, iOS 26.0. Apple: \"Selects a promotional offer to apply to a purchase a customer makes from a subscription store view.\""},
        {"name": "subscriptionStatusTask", "note": "`.subscriptionStatusTask(for:priority:action:)`, iOS 17.0. Apple: \"Declares the view as dependent on the status of an auto-renewable subscription group, and returns a modified view.\""},
        {"name": "subscriptionStoreButtonLabel", "note": "`.subscriptionStoreButtonLabel(_:)`, iOS 17.0. Apple: \"Configures subscription store view instances within a view to use the provided button label.\""},
        {"name": "subscriptionStoreControlBackground", "note": "`.subscriptionStoreControlBackground(_:)`, iOS 17.0. Apple: \"Set a standard effect to use for the background of subscription store view controls within the view.\""},
        {"name": "subscriptionStoreControlIcon", "note": "`.subscriptionStoreControlIcon(icon:)`, iOS 17.0. Apple: \"Sets a view to use to decorate individual subscription options within a subscription store view.\""},
        {"name": "subscriptionStoreControlStyle", "note": "`.subscriptionStoreControlStyle(_:)`, iOS 17.0. Apple: \"Sets the control style for subscription store views within a view.\""},
        {"name": "subscriptionStoreOptionGroupStyle", "note": "`.subscriptionStoreOptionGroupStyle(_:)`, iOS 18.0. Apple: \"Sets the style subscription store views within this view use to display groups of subscription options.\""},
        {"name": "subscriptionStorePickerItemBackground", "note": "`.subscriptionStorePickerItemBackground(_:)`, iOS 17.0. Apple: \"Sets the background style for picker items of the subscription store view instances within a view.\""},
        {"name": "subscriptionStorePolicyDestination", "note": "`.subscriptionStorePolicyDestination(for:destination:)`, iOS 17.0. Apple: \"Configures a view as the destination for a policy button action in subscription store views.\""},
        {"name": "subscriptionStorePolicyForegroundStyle", "note": "`.subscriptionStorePolicyForegroundStyle(_:)`, iOS 17.0. Apple: \"Sets the style for the terms of service and privacy policy buttons within a subscription store view.\""},
        {"name": "subscriptionStoreSignInAction", "note": "`.subscriptionStoreSignInAction(_:)`, iOS 17.0. Apple: \"Adds an action to perform when a person uses the sign-in button on a subscription store view within a view.\""},
        {"name": "multiSeatDataSharingConsentSheet", "note": "`.multiSeatDataSharingConsentSheet(isPresented:subscriptionGroupID:onCompletion:)`, iOS 27.3. Apple: \"Presents the data sharing consent sheet, where a subscriber decides whether to share account-level data with you.\""},
        {"name": "multiSeatInvitationBehavior", "note": "`.multiSeatInvitationBehavior(_:)`, iOS 27.3. Apple: \"Sets the behavior of the Apple-owned invitation sheet that appears after a customer purchases a multi-seat subscription from a StoreKit view.\""},
        {"name": "multiSeatInvitationSheet", "note": "`.multiSeatInvitationSheet(isPresented:subscriptionGroupID:onCompletion:)`, iOS 27.3. Apple: \"Presents the Apple-owned multi-seat invitation sheet, allowing the subscriber to invite others to join their multi-seat subscription.\""}
      ]
    }
  }
};
