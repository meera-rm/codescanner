import React, { useEffect, useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useAuthStore } from '../store/authStore';
import { apiService } from '../services/apiService';

export default function DashboardScreen() {
  const { user } = useAuthStore();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await apiService.get('/dashboard/summary');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Welcome Section */}
      <View style={styles.section}>
        <Text style={styles.greeting}>
          Hello, {user?.name || 'User'}!
        </Text>
        <Text style={styles.subtitle}>
          Welcome to CodePulse AI
        </Text>
      </View>

      {/* Stats Cards */}
      {dashboardData && (
        <>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {dashboardData.monitoring.health.toFixed(1)}%
              </Text>
              <Text style={styles.statLabel}>System Health</Text>
            </View>

            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {dashboardData.ai_insights.total_patterns}
              </Text>
              <Text style={styles.statLabel}>Patterns Found</Text>
            </View>
          </View>

          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {dashboardData.monitoring.active_alerts}
              </Text>
              <Text style={styles.statLabel}>Active Alerts</Text>
            </View>

            <View style={styles.statCard}>
              <Text style={styles.statValue}>
                {dashboardData.enterprise.usage_percentage.toFixed(0)}%
              </Text>
              <Text style={styles.statLabel}>Plan Usage</Text>
            </View>
          </View>
        </>
      )}

      {/* Action Buttons */}
      <View style={styles.actionSection}>
        <TouchableOpacity style={styles.button}>
          <Text style={styles.buttonText}>Analyze Code</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.button, styles.secondaryButton]}>
          <Text style={styles.secondaryButtonText}>View Reports</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  section: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#999',
  },
  statsGrid: {
    flexDirection: 'row',
    padding: 10,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    margin: 10,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
  },
  actionSection: {
    padding: 20,
  },
  button: {
    backgroundColor: '#667eea',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: '#f0f0f0',
  },
  secondaryButtonText: {
    color: '#667eea',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
