import { Tabs } from 'expo-router';
import React from 'react';

const TabsLayout: React.FC = () => (
  <Tabs
    screenOptions={{
      headerShown: true,
      tabBarActiveTintColor: '#1d4ed8',
      tabBarInactiveTintColor: '#94a3b8',
      tabBarStyle: { borderTopColor: '#e2e8f0' },
    }}
  >
    <Tabs.Screen
      name="settings"
      options={{
        title: 'Settings',
      }}
    />
    <Tabs.Screen
      name="paywall"
      options={{
        title: 'Paywall',
      }}
    />
    <Tabs.Screen
      name="devices"
      options={{
        title: 'Devices',
      }}
    />
    <Tabs.Screen
      name="sessions"
      options={{
        title: 'Sessions',
      }}
    />
  </Tabs>
);

export default TabsLayout;
