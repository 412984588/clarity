import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { apiRequest } from '../../services/api';
import { getDeviceFingerprint } from '../../services/auth';

type Device = {
  id: string;
  device_name: string;
  platform: string;
  last_active_at: string;
  is_active: boolean;
};

const DevicesScreen: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = useCallback(async () => {
    try {
      const data = await apiRequest<Device[]>('/auth/devices');
      setDevices(data);
      setError(null);
    } catch (_err) {
      setError('Failed to load devices.');
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      await fetchDevices();
      setIsLoading(false);
    };
    void load();
  }, [fetchDevices]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchDevices();
    setIsRefreshing(false);
  }, [fetchDevices]);

  const handleRemove = useCallback(async (deviceId: string) => {
    try {
      const fingerprint = await getDeviceFingerprint();
      await apiRequest(`/auth/devices/${deviceId}`, {
        method: 'DELETE',
        headers: { 'X-Device-Fingerprint': fingerprint },
      });
      setDevices((prev) => prev.filter((device) => device.id !== deviceId));
    } catch (_err) {
      setError('Failed to remove device.');
    }
  }, []);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />}
    >
      <Text style={styles.title}>Devices</Text>
      <Text style={styles.subtitle}>Manage devices signed in to your account.</Text>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color="#1d4ed8" />
      ) : (
        <View style={styles.list}>
          {devices.map((device) => (
            <View key={device.id} style={styles.card}>
              <Text style={styles.deviceName}>{device.device_name}</Text>
              <Text style={styles.deviceMeta}>{device.platform}</Text>
              <Text style={styles.deviceMeta}>{`Last active: ${device.last_active_at}`}</Text>
              <Pressable
                onPress={() => handleRemove(device.id)}
                style={[
                  styles.removeButton,
                  device.is_active && styles.disabledButton,
                ]}
                disabled={device.is_active}
              >
                <Text style={styles.removeButtonText}>
                  {device.is_active ? 'Current Device' : 'Remove'}
                </Text>
              </Pressable>
            </View>
          ))}
          {devices.length === 0 && <Text style={styles.emptyText}>No devices found.</Text>}
        </View>
      )}

      {error && <Text style={styles.errorText}>{error}</Text>}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 6,
  },
  subtitle: {
    color: '#64748b',
    marginBottom: 16,
  },
  list: {
    gap: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 16,
    shadowColor: '#0f172a',
    shadowOpacity: 0.06,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 2,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
  },
  deviceMeta: {
    color: '#64748b',
    marginBottom: 4,
  },
  removeButton: {
    marginTop: 12,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  removeButtonText: {
    color: '#b91c1c',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
  emptyText: {
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 20,
  },
  errorText: {
    color: '#dc2626',
    marginTop: 16,
  },
  loader: {
    marginTop: 30,
  },
});

export default DevicesScreen;
