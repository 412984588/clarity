import { Stack } from 'expo-router';
import React from 'react';

const SessionLayout: React.FC = () => (
  <Stack
    screenOptions={{
      headerShown: true,
      headerBackTitle: 'Back',
      headerStyle: { backgroundColor: '#f8fafc' },
      headerTintColor: '#1d4ed8',
    }}
  />
);

export default SessionLayout;
