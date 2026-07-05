import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  FlatList,
  TextInput,
} from 'react-native';
import { apiService } from '../services/apiService';

interface AnalysisResult {
  id: string;
  file: string;
  patterns: number;
  timestamp: string;
}

export default function AnalysisScreen() {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;

    setLoading(true);
    try {
      const response = await apiService.post('/analysis/start', {
        repository_url: repoUrl,
      });
      setAnalyses([response.data, ...analyses]);
      setRepoUrl('');
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysisItem = ({ item }: { item: AnalysisResult }) => (
    <View style={styles.analysisCard}>
      <Text style={styles.fileName}>{item.file}</Text>
      <Text style={styles.patterns}>{item.patterns} patterns found</Text>
      <Text style={styles.timestamp}>
        {new Date(item.timestamp).toLocaleDateString()}
      </Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.inputSection}>
        <Text style={styles.sectionTitle}>Analyze Code Repository</Text>

        <TextInput
          style={styles.input}
          placeholder="Enter repository URL"
          placeholderTextColor="#999"
          value={repoUrl}
          onChangeText={setRepoUrl}
          editable={!loading}
        />

        <TouchableOpacity
          style={[styles.analyzeButton, loading && styles.disabledButton]}
          onPress={handleAnalyze}
          disabled={loading}
        >
          <Text style={styles.analyzeButtonText}>
            {loading ? 'Analyzing...' : 'Start Analysis'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.resultsSection}>
        <Text style={styles.sectionTitle}>Recent Analyses</Text>

        {analyses.length === 0 ? (
          <Text style={styles.emptyText}>No analyses yet</Text>
        ) : (
          <FlatList
            data={analyses}
            renderItem={renderAnalysisItem}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
          />
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  inputSection: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 14,
    color: '#333',
  },
  analyzeButton: {
    backgroundColor: '#667eea',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  analyzeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  disabledButton: {
    opacity: 0.6,
  },
  resultsSection: {
    padding: 20,
  },
  analysisCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#667eea',
  },
  fileName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  patterns: {
    fontSize: 12,
    color: '#667eea',
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 10,
    color: '#999',
  },
  emptyText: {
    color: '#999',
    textAlign: 'center',
    marginVertical: 20,
  },
});
