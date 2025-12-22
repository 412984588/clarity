import { Link } from 'expo-router';
import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '../../stores/authStore';

const SettingsScreen: React.FC = () => {
  const { user, logout, isLoading } = useAuth();

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Account</Text>
        <Text style={styles.label}>Signed in as</Text>
        <Text style={styles.email}>{user?.email ?? 'Unknown user'}</Text>

        <Pressable
          onPress={logout}
          style={[styles.logoutButton, isLoading && styles.disabledButton]}
          disabled={isLoading}
        >
          <Text style={styles.logoutText}>Log out</Text>
        </Pressable>
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Security</Text>
        <Link href="/(tabs)/devices" style={styles.linkRow}>
          Manage Devices
        </Link>
        <Link href="/(tabs)/sessions" style={styles.linkRow}>
          Active Sessions
        </Link>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f8fafc',
    gap: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#0f172a',
    shadowOpacity: 0.06,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 2,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 12,
  },
  label: {
    fontSize: 13,
    color: '#94a3b8',
  },
  email: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginTop: 4,
  },
  logoutButton: {
    marginTop: 16,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  logoutText: {
    color: '#b91c1c',
    fontWeight: '600',
  },
  linkRow: {
    paddingVertical: 12,
    color: '#1d4ed8',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
});

export default SettingsScreen;
