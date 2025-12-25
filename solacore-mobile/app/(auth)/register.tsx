import { Link } from 'expo-router';
import React, { useMemo, useState } from 'react';
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

import { t } from '../../i18n';
import { useAuth } from '../../stores/authStore';

const getPasswordStrength = (password: string): { label: string; color: string } => {
  let score = 0;
  if (password.length >= 8) score += 1;
  if (/[A-Z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score >= 4) return { label: t('auth.strong'), color: '#16a34a' };
  if (score === 3) return { label: t('auth.good'), color: '#2563eb' };
  if (score === 2) return { label: t('auth.fair'), color: '#f59e0b' };
  return { label: t('auth.weak'), color: '#dc2626' };
};

const RegisterScreen: React.FC = () => {
  const { register, error, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const strength = useMemo(() => getPasswordStrength(password), [password]);
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleRegister = async () => {
    if (!email || !password || !confirmPassword) {
      setLocalError(t('auth.fillAllFields'));
      return;
    }

    if (!passwordsMatch) {
      setLocalError(t('auth.passwordsDoNotMatch'));
      return;
    }

    setLocalError(null);
    await register(email.trim(), password);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>{t('auth.createAccount')}</Text>
        <Text style={styles.subtitle}>{t('auth.startJourney')}</Text>

        <View style={styles.card}>
          <Text style={styles.label}>{t('common.email')}</Text>
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder={t('auth.emailPlaceholder')}
            autoCapitalize="none"
            keyboardType="email-address"
            style={styles.input}
            editable={!isLoading}
          />

          <Text style={styles.label}>{t('common.password')}</Text>
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder={t('auth.createPasswordPlaceholder')}
            secureTextEntry
            style={styles.input}
            editable={!isLoading}
          />

          <Text
            style={[styles.strengthText, { color: strength.color }]}
          >{`${t('auth.strength')}: ${strength.label}`}</Text>

          <Text style={styles.label}>{t('auth.confirmPassword')}</Text>
          <TextInput
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder={t('auth.reenterPasswordPlaceholder')}
            secureTextEntry
            style={styles.input}
            editable={!isLoading}
          />

          {(localError || error) && <Text style={styles.errorText}>{localError ?? error}</Text>}

          <Pressable
            onPress={handleRegister}
            style={[styles.primaryButton, isLoading && styles.disabledButton]}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryButtonText}>{t('auth.createAccount')}</Text>
            )}
          </Pressable>

          <View style={styles.linksRow}>
            <Text style={styles.helperText}>{t('auth.alreadyHaveAccount')}</Text>
            <Link href="/login" style={styles.linkText}>
              {t('auth.signIn')}
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
  strengthText: {
    marginTop: 8,
    fontSize: 13,
    fontWeight: '600',
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

export default RegisterScreen;
