import { Tabs } from 'expo-router';
import React from 'react';

import { t } from '../../i18n';
import { BILLING_ENABLED } from '../../services/config';

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
      name="home"
      options={{
        title: t('tabs.home'),
      }}
    />
    <Tabs.Screen
      name="settings"
      options={{
        title: t('tabs.settings'),
      }}
    />
    {BILLING_ENABLED && (
      <Tabs.Screen
        name="paywall"
        options={{
          title: t('tabs.paywall'),
        }}
      />
    )}
    <Tabs.Screen
      name="devices"
      options={{
        title: t('tabs.devices'),
      }}
    />
    <Tabs.Screen
      name="sessions"
      options={{
        title: t('tabs.sessions'),
      }}
    />
  </Tabs>
);

export default TabsLayout;
