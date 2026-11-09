/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "notifications",
  "displayName": "Notifications",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Notifications",
  "category": "Feedback & Status",
  "keywords": [
    "notification",
    "push",
    "local notification",
    "alert banner"
  ],
  "usage": {
    "description": "A notification tells people about something new while the app is closed."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use the UserNotifications framework: https://developer.apple.com/documentation/usernotifications."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "UNUserNotificationCenter",
          "use": "iOS 10.0. Apple: \"The central object for managing notification-related activities for your app or app extension.\""
        },
        {
          "name": "UNNotificationRequest",
          "use": "iOS 10.0. Apple: \"A request to schedule a local notification, which includes the content of the notification and the trigger conditions for delivery.\""
        }
      ]
    }
  }
};
