import { Link } from 'expo-router';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

const ForgotScreen: React.FC = () => (
  <View style={styles.container}>
    <View style={styles.card}>
      <Text style={styles.title}>Coming soon</Text>
      <Text style={styles.subtitle}>Password reset is on the way.</Text>
      <Link href="/login" style={styles.linkText}>
        Back to login
      </Link>
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#f8fafc',
  },
  card: {
    backgroundColor: '#fff',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#0f172a',
    shadowOpacity: 0.08,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 8 },
    elevation: 2,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: '#64748b',
    marginBottom: 16,
  },
  linkText: {
    color: '#1d4ed8',
    fontWeight: '600',
  },
});

export default ForgotScreen;
