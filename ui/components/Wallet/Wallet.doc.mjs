/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "Wallet",
  "displayName": "Apple Pay and Wallet",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Wallet",
  "category": "Utility",
  "keywords": [
    "pass kit",
    "apple pay",
    "wallet",
    "pay later",
    "identity"
  ],
  "usage": {
    "description": "Modifiers for PassKit's Apple Pay and Wallet buttons: payment sheet callbacks, pay later views, add-to-Wallet and verify-identity buttons. Each entry is a SwiftUI view modifier from PassKit. Add it to a view as Apple ships it."
  },
  "props": [],
  "platformApi": {
    "ios": {
      "family": "Wallet",
      "variants": [
        {"name": "addOrderToWalletButtonStyle", "note": "`.addOrderToWalletButtonStyle(_:)`, iOS 17.0. Apple: \"Sets the button’s style.\""},
        {"name": "addPassToWalletButtonStyle", "note": "`.addPassToWalletButtonStyle(_:)`, iOS 16.0. Apple: \"Sets the style to be used by the button. (see `PKAddPassButtonStyle`).\""},
        {"name": "onApplePayCouponCodeChange", "note": "`.onApplePayCouponCodeChange(perform:)`, iOS 15.5. Apple: \"Called when a user has entered or updated a coupon code. This is required if the user is being asked to provide a coupon code.\""},
        {"name": "onApplePayPaymentMethodChange", "note": "`.onApplePayPaymentMethodChange(perform:)`, iOS 15.5. Apple: \"Called when a payment method has changed and asks for an update payment request. If this modifier isn’t provided Wallet will assume the payment method is valid.\""},
        {"name": "onApplePayShippingContactChange", "note": "`.onApplePayShippingContactChange(perform:)`, iOS 15.5. Apple: \"Called when a user selected a shipping address. This is required if the user is being asked to provide a shipping contact.\""},
        {"name": "onApplePayShippingMethodChange", "note": "`.onApplePayShippingMethodChange(perform:)`, iOS 15.5. Apple: \"Called when a user selected a shipping method. This is required if the user is being asked to provide a shipping method.\""},
        {"name": "payLaterViewAction", "note": "`.payLaterViewAction(_:)`, iOS 17.0. Apple: \"Sets the action on the PayLaterView. See `PKPayLaterAction`.\""},
        {"name": "payLaterViewDisplayStyle", "note": "`.payLaterViewDisplayStyle(_:)`, iOS 17.0. Apple: \"Sets the display style on the PayLaterView. See `PKPayLaterDisplayStyle`.\""},
        {"name": "payWithApplePayButtonDisableCardArt", "note": "`.payWithApplePayButtonDisableCardArt()`, iOS 26.0. Apple: \"Sets the features that should be allowed to show on the payment buttons.\""},
        {"name": "payWithApplePayButtonStyle", "note": "`.payWithApplePayButtonStyle(_:)`, iOS 16.0. Apple: \"Sets the style to be used by the button. (see `PayWithApplePayButtonStyle`).\""},
        {"name": "verifyIdentityWithWalletButtonStyle", "note": "`.verifyIdentityWithWalletButtonStyle(_:)`, iOS 16.0. Apple: \"Sets the style to be used by the button. (see `PKIdentityButtonStyle`).\""}
      ]
    }
  }
};
