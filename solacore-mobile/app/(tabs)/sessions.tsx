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

import { t } from '../../i18n';
import { apiRequest } from '../../services/api';

type Session = {
  id: string;
  device_id: string;
  created_at: string;
  expires_at: string;
};

const SessionsScreen: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    try {
      const data = await apiRequest<Session[]>('/auth/sessions');
      setSessions(data);
      setError(null);
    } catch (_err) {
      setError(t('sessions.loadFailed'));
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      await fetchSessions();
      setIsLoading(false);
    };
    void load();
  }, [fetchSessions]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchSessions();
    setIsRefreshing(false);
  }, [fetchSessions]);

  const handleTerminate = useCallback(async (sessionId: string) => {
    try {
      await apiRequest(`/auth/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((session) => session.id !== sessionId));
    } catch (_err) {
      setError(t('sessions.terminateFailed'));
    }
  }, []);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />}
    >
      <Text style={styles.title}>{t('sessions.title')}</Text>
      <Text style={styles.subtitle}>{t('sessions.subtitle')}</Text>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} color="#1d4ed8" />
      ) : (
        <View style={styles.list}>
          {sessions.map((session) => (
            <View key={session.id} style={styles.card}>
              <Text style={styles.sessionTitle}>{`${t('sessions.session')} ${session.id}`}</Text>
              <Text
                style={styles.sessionMeta}
              >{`${t('sessions.device')}: ${session.device_id}`}</Text>
              <Text
                style={styles.sessionMeta}
              >{`${t('sessions.created')}: ${session.created_at}`}</Text>
              <Text
                style={styles.sessionMeta}
              >{`${t('sessions.expires')}: ${session.expires_at}`}</Text>
              <Pressable onPress={() => handleTerminate(session.id)} style={styles.terminateButton}>
                <Text style={styles.terminateButtonText}>{t('sessions.terminate')}</Text>
              </Pressable>
            </View>
          ))}
          {sessions.length === 0 && (
            <Text style={styles.emptyText}>{t('sessions.noSessions')}</Text>
          )}
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
  sessionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
  },
  sessionMeta: {
    color: '#64748b',
    marginBottom: 4,
  },
  terminateButton: {
    marginTop: 12,
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  terminateButtonText: {
    color: '#b91c1c',
    fontWeight: '600',
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

export default SessionsScreen;
