import { apiRequest } from './api';

export type AccountExport = Record<string, unknown>;

export const exportAccountData = async (): Promise<AccountExport> =>
  apiRequest<AccountExport>('/account/export');

export const deleteAccount = async (): Promise<void> => {
  await apiRequest('/account', { method: 'DELETE' });
};
