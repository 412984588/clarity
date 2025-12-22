import { Stack } from 'expo-router';
import React from 'react';

const AuthLayout: React.FC = () => (
  <Stack
    screenOptions={{
      headerShown: false,
    }}
  />
);

export default AuthLayout;
