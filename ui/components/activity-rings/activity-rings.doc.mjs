/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
export default {
  "type": "component",
  "name": "activity-rings",
  "displayName": "Activity rings",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "Activity rings",
  "category": "Data Visualization",
  "keywords": [
    "activity rings",
    "move",
    "exercise",
    "stand",
    "health"
  ],
  "usage": {
    "description": "Activity rings show Move, Exercise and Stand progress."
  },
  "props": [],
  "platformUsage": {
    "ios": {
      "description": "Use HealthKitUI's HKActivityRingView: https://developer.apple.com/documentation/healthkitui/hkactivityringview. Never draw your own rings."
    }
  },
  "platformApi": {
    "ios": {
      "supporting": [
        {
          "name": "HKActivityRingView",
          "use": "iOS 9.3. Apple: \"A view that uses the Move, Exercise, and Stand activity rings to display data from a HealthKit activity summary object.\""
        }
      ]
    }
  }
};
