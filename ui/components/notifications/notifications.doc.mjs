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
    },
    "android": {
      "description": "Use Android notifications: https://developer.android.com/develop/ui/views/notifications. Build one with NotificationCompat.Builder, post it on a NotificationChannel, and ask for the POST_NOTIFICATIONS permission on Android 13 and later.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Create one channel per kind of message, so people can turn each kind off."
        },
        {
          "guidance": true,
          "description": "Set a content intent, so a tap opens the right screen."
        }
      ]
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
    },
    "android": {
      "supporting": [
        {
          "name": "NotificationCompat.Builder",
          "use": "Builds the notification: setSmallIcon, setContentTitle, setContentText, setPriority and setContentIntent."
        },
        {
          "name": "NotificationManagerCompat",
          "use": "Posts, updates and cancels notifications with notify() and cancel()."
        },
        {
          "name": "NotificationChannel",
          "use": "A channel for one kind of message, with its own importance. Create it before you post, on Android 8 and later."
        },
        {
          "name": "POST_NOTIFICATIONS",
          "use": "The runtime permission to post notifications on Android 13 and later."
        }
      ]
    }
  }
};
