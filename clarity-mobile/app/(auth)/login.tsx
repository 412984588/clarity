import * as AppleAuthentication from 'expo-apple-authentication';
import * as AuthSession from 'expo-auth-session';
import * as Google from 'expo-auth-session/providers/google';
import * as WebBrowser from 'expo-web-browser';
import { Link } from 'expo-router';
import React, { useEffect, useMemo, useState } from 'react';
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

import { apiRequest } from '../../services/api';
import { getDeviceFingerprint } from '../../services/auth';
import { useAuth } from '../../stores/authStore';

WebBrowser.maybeCompleteAuthSession();

const decodeJwtEmail = (token: string): string | null => {
  const payload = token.split('.')[1];
  if (!payload) {
    return null;
  }

  const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
  if (typeof globalThis.atob !== 'function') {
    return null;
  }

  try {
    const decoded = globalThis.atob(normalized);
    const data = JSON.parse(decoded) as { email?: string };
    return typeof data.email === 'string' ? data.email : null;
  } catch {
    return null;
  }
};

const LoginScreen: React.FC = () => {
  const { login, error, isLoading, setSession } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [oauthError, setOauthError] = useState<string | null>(null);

  const [request, response, promptAsync] = Google.useAuthRequest({
    responseType: 'id_token',
    scopes: ['openid', 'profile', 'email'],
    clientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID,
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID,
    webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID,
    redirectUri: AuthSession.makeRedirectUri(),
  });

  useEffect(() => {
    const handleGoogleResponse = async () => {
      if (response?.type !== 'success') {
        return;
      }

      const idToken =
        (response.authentication as { idToken?: string } | null)?.idToken ??
        (response.params?.id_token as string | undefined);
      if (!idToken) {
        setOauthError('Google login did not return an id token.');
        return;
      }

      try {
        const deviceFingerprint = await getDeviceFingerprint();
        const data = await apiRequest<{ access_token: string; refresh_token: string }>(
          '/auth/oauth/google',
          {
            method: 'POST',
            auth: false,
            body: { id_token: idToken, device_fingerprint: deviceFingerprint },
          }
        );
        const decodedEmail = decodeJwtEmail(idToken);
        await setSession(data.access_token, data.refresh_token, decodedEmail);
        setOauthError(null);
      } catch (_err) {
        setOauthError('Google login failed. Please try again.');
      }
    };

    void handleGoogleResponse();
  }, [response, setSession]);

  const handleLogin = async () => {
    if (!email || !password) {
      return;
    }
    await login(email.trim(), password);
  };

  const handleAppleLogin = async () => {
    setOauthError(null);
    try {
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.EMAIL,
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
        ],
      });

      if (!credential.identityToken) {
        setOauthError('Apple login did not return an identity token.');
        return;
      }

      const deviceFingerprint = await getDeviceFingerprint();
      const data = await apiRequest<{ access_token: string; refresh_token: string }>(
        '/auth/oauth/apple',
        {
          method: 'POST',
          auth: false,
          body: { id_token: credential.identityToken, device_fingerprint: deviceFingerprint },
        }
      );

      await setSession(data.access_token, data.refresh_token, credential.email ?? undefined);
    } catch (_err) {
      setOauthError('Apple login failed. Please try again.');
    }
  };

  const isFormValid = useMemo(() => email.length > 0 && password.length > 0, [email, password]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>Welcome Back</Text>
        <Text style={styles.subtitle}>Sign in to continue to Clarity.</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="you@example.com"
            autoCapitalize="none"
            keyboardType="email-address"
            style={styles.input}
            editable={!isLoading}
          />

          <Text style={styles.label}>Password</Text>
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            secureTextEntry
            style={styles.input}
            editable={!isLoading}
          />

          {(error || oauthError) && (
            <Text style={styles.errorText}>{oauthError ?? error}</Text>
          )}

          <Pressable
            onPress={handleLogin}
            style={[styles.primaryButton, (!isFormValid || isLoading) && styles.disabledButton]}
            disabled={!isFormValid || isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryButtonText}>Login</Text>
            )}
          </Pressable>

          <Pressable
            onPress={() => promptAsync()}
            style={[styles.secondaryButton, (!request || isLoading) && styles.disabledButton]}
            disabled={!request || isLoading}
          >
            <Text style={styles.secondaryButtonText}>Continue with Google</Text>
          </Pressable>

          {Platform.OS === 'ios' && (
            <Pressable onPress={handleAppleLogin} style={styles.appleButton} disabled={isLoading}>
              <Text style={styles.appleButtonText}>Continue with Apple</Text>
            </Pressable>
          )}

          <View style={styles.linksRow}>
            <Link href="/register" style={styles.linkText}>
              Create account
            </Link>
            <Link href="/forgot" style={styles.linkText}>
              Forgot password?
            </Link>
          </View>
          <View style={styles.singleLinkRow}>
            <Link href="/reset" style={styles.linkText}>
              Have a reset token?
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
  secondaryButton: {
    borderWidth: 1,
    borderColor: '#cbd5f5',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  secondaryButtonText: {
    color: '#1d4ed8',
    fontWeight: '600',
  },
  appleButton: {
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  appleButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
  linksRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  singleLinkRow: {
    marginTop: 12,
    alignItems: 'center',
  },
  linkText: {
    color: '#1d4ed8',
    fontWeight: '600',
  },
});

export default LoginScreen;
