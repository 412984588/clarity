import { Link, useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { apiRequest, type ApiError } from '../../services/api';

type ResetErrorDetails = {
  detail?: { error?: string } | string;
  message?: string;
};

const getResetErrorMessage = (error: unknown): string => {
  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    const apiError = error as ApiError;
    const details = apiError.details as ResetErrorDetails | undefined;
    const detailValue = details?.detail;

    if (detailValue && typeof detailValue === 'object') {
      const code = detailValue.error;
      if (typeof code === 'string') {
        return code;
      }
    }

    if (typeof detailValue === 'string') {
      return detailValue;
    }

    if (apiError.message) {
      return apiError.message;
    }
  }

  return 'Something went wrong. Please try again.';
};

const ResetScreen: React.FC = () => {
  const router = useRouter();
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleReset = async () => {
    if (!token.trim() || !newPassword || !confirmPassword) {
      setError('Please fill out all fields.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      await apiRequest<{ message: string }>('/auth/reset-password', {
        method: 'POST',
        auth: false,
        body: { token: token.trim(), new_password: newPassword },
      });
      router.replace('/login');
    } catch (err) {
      setError(getResetErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Set a new password</Text>
        <Text style={styles.subtitle}>Enter the token from your email to continue.</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Reset token</Text>
          <TextInput
            value={token}
            onChangeText={setToken}
            placeholder="Paste your reset token"
            autoCapitalize="none"
            style={styles.input}
            editable={!isLoading}
          />

          <Text style={styles.label}>New password</Text>
          <TextInput
            value={newPassword}
            onChangeText={setNewPassword}
            placeholder="Create a new password"
            secureTextEntry
            style={styles.input}
            editable={!isLoading}
          />

          <Text style={styles.label}>Confirm new password</Text>
          <TextInput
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="Re-enter new password"
            secureTextEntry
            style={styles.input}
            editable={!isLoading}
          />

          {error && <Text style={styles.errorText}>{error}</Text>}

          <Pressable
            onPress={handleReset}
            style={[styles.primaryButton, isLoading && styles.disabledButton]}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryButtonText}>Reset password</Text>
            )}
          </Pressable>

          <View style={styles.linksRow}>
            <Text style={styles.helperText}>Need a link instead?</Text>
            <Link href="/forgot" style={styles.linkText}>
              Request reset
            </Link>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 24,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#0f172a',
    shadowOpacity: 0.08,
    shadowRadius: 16,
    shadowOffset: { width: 0, height: 8 },
    elevation: 2,
  },
  label: {
    fontSize: 14,
    color: '#334155',
    marginBottom: 8,
    marginTop: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    color: '#0f172a',
    backgroundColor: '#fff',
  },
  errorText: {
    color: '#dc2626',
    marginTop: 12,
    fontSize: 14,
  },
  primaryButton: {
    backgroundColor: '#1d4ed8',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
  },
  primaryButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  disabledButton: {
    opacity: 0.6,
  },
  linksRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
    gap: 6,
  },
  helperText: {
    color: '#64748b',
  },
  linkText: {
    color: '#1d4ed8',
    fontWeight: '600',
  },
});

export default ResetScreen;
