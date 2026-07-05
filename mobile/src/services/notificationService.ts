import PushNotification from 'react-native-push-notification';

export const configurePushNotifications = () => {
  PushNotification.configure({
    onNotification: (notification) => {
      console.log('Notification received:', notification);
      notification.finish('UIBackgroundFetchResultNoData');
    },
    onRegistered: (token) => {
      console.log('Device token registered:', token);
    },
    senderID: 'YOUR_GCM_SENDER_ID',
    requestPermissions: true,
  });
};

export const sendLocalNotification = (
  title: string,
  message: string,
  delayMs = 0
) => {
  PushNotification.localNotificationSchedule({
    title,
    message,
    bigText: message,
    playSound: true,
    soundName: 'default',
    date: new Date(Date.now() + delayMs),
  });
};

export const sendAnalysisNotification = (repoName: string) => {
  sendLocalNotification(
    'Analysis Complete',
    `Code analysis for ${repoName} is complete`,
    2000
  );
};

export const sendAlertNotification = (alertTitle: string, severity: string) => {
  const titlePrefix = severity === 'critical' ? '🚨' : '⚠️';
  sendLocalNotification(
    `${titlePrefix} ${alertTitle}`,
    `An alert has been triggered for your CodePulse AI system`,
    0
  );
};
