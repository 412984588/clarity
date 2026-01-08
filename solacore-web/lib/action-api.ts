import { api } from "@/lib/api";

export const completeAction = async (sessionId: string): Promise<void> => {
  await api.patch(`/actions/${sessionId}/complete`);
};

export const uncompleteAction = async (sessionId: string): Promise<void> => {
  await api.patch(`/actions/${sessionId}/uncomplete`);
};
