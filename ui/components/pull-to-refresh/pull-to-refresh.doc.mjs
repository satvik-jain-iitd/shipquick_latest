/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */
/** Framework topic (docs/research/framework-topics.md). Facts from Google: https://developer.android.com/develop/ui/compose/components/pull-to-refresh and current.txt of material3 1.4.0 (AOSP 5113b82a). */
export default {
  "type": "component",
  "name": "pull-to-refresh",
  "displayName": "Pull to refresh",
  "platforms": {
    "android": null,
    "ios": null,
    "web": null
  },
  "group": "List",
  "category": "Table & List",
  "keywords": [
    "pull to refresh",
    "refresh",
    "reload",
    "swipe down"
  ],
  "usage": {
    "description": "Pull to refresh lets people reload a scrolling list by pulling it down."
  },
  "props": [],
  "platformUsage": {
    "android": {
      "description": "Use PullToRefreshBox from Compose Material 3: https://developer.android.com/develop/ui/compose/components/pull-to-refresh. Wrap the list in it, set isRefreshing while the load runs, and start the load in onRefresh.",
      "bestPractices": [
        {
          "guidance": true,
          "description": "Set isRefreshing back to false when the load ends, or the indicator stays."
        },
        {
          "guidance": true,
          "description": "Also offer a refresh action in a menu, for people who cannot pull."
        }
      ]
    }
  },
  "platformApi": {
    "android": {
      "family": "PullToRefresh",
      "variants": [
        {
          "name": "PullToRefreshBox",
          "note": "Wraps a scrolling list so the user can pull it down to reload. Pass isRefreshing and onRefresh. This is Google's pull to refresh for Compose: https://developer.android.com/develop/ui/compose/components/pull-to-refresh"
        },
        {
          "name": "PullToRefreshDefaults.Indicator",
          "note": "The default spinner that comes down as the user pulls."
        },
        {
          "name": "PullToRefreshDefaults.IndicatorBox",
          "note": "The container that moves and clips the indicator. Use it to put your own indicator in place of the spinner."
        }
      ],
      "supporting": [
        {
          "name": "PullToRefreshState",
          "use": "How far the user has pulled (distanceFraction). Call animateToThreshold() and animateToHidden() from a coroutine."
        },
        {
          "name": "rememberPullToRefreshState",
          "use": "Creates and keeps a PullToRefreshState across recompositions."
        },
        {
          "name": "PullToRefreshDefaults",
          "use": "Default colours, shape, elevation, threshold and the Indicator and IndicatorBox for pull to refresh."
        }
      ]
    }
  }
};
