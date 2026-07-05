import React from 'react';
import {
  View,
  StyleSheet,
  Text,
  ActivityIndicator,
} from 'react-native';

export default function SplashScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.logo}>CodePulse</Text>
      <Text style={styles.subtitle}>AI-Powered Code Analysis</Text>
      <ActivityIndicator
        size="large"
        color="#667eea"
        style={styles.spinner}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logo: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#e8edf7',
    marginBottom: 40,
  },
  spinner: {
    marginTop: 20,
  },
});
