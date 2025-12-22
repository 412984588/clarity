import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { t } from '../../i18n';
import { createSession, patchSession, streamMessage } from '../../services/solve';
import { updateStepEntry, getAllMessages } from '../../services/stepHistory';
import type {
  CrisisResponse,
  Message,
  SolveStep,
  StreamDoneEvent,
} from '../../types/solve';
import { SOLVE_STEPS, getStepIndex } from '../../types/solve';

// Step Progress Bar Component
const StepProgressBar: React.FC<{ currentStep: SolveStep }> = ({ currentStep }) => {
  const currentIndex = getStepIndex(currentStep);

  return (
    <View style={styles.progressContainer}>
      {SOLVE_STEPS.map((step, index) => {
        const isCompleted = index < currentIndex;
        const isCurrent = index === currentIndex;

        return (
          <View key={step.key} style={styles.stepItem}>
            <View
              style={[
                styles.stepCircle,
                isCompleted && styles.stepCompleted,
                isCurrent && styles.stepCurrent,
              ]}
            >
              {isCompleted ? (
                <Text style={styles.stepCheckmark}>✓</Text>
              ) : (
                <Text style={[styles.stepNumber, isCurrent && styles.stepNumberCurrent]}>
                  {index + 1}
                </Text>
              )}
            </View>
            <Text
              style={[
                styles.stepLabel,
                isCompleted && styles.stepLabelCompleted,
                isCurrent && styles.stepLabelCurrent,
              ]}
              numberOfLines={1}
            >
              {t(step.labelKey)}
            </Text>
            {index < SOLVE_STEPS.length - 1 && (
              <View style={[styles.stepLine, isCompleted && styles.stepLineCompleted]} />
            )}
          </View>
        );
      })}
    </View>
  );
};

// Message Bubble Component
const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      <Text style={[styles.messageText, isUser && styles.userMessageText]}>
        {message.content}
      </Text>
    </View>
  );
};

// Crisis Alert Component
const CrisisAlert: React.FC<{
  crisis: CrisisResponse;
  onDismiss: () => void;
}> = ({ crisis, onDismiss }) => (
  <View style={styles.crisisOverlay}>
    <View style={styles.crisisCard}>
      <Text style={styles.crisisTitle}>{t('solve.crisisTitle')}</Text>
      <Text style={styles.crisisMessage}>
        {crisis.message ?? t('solve.crisisMessage')}
      </Text>
      <View style={styles.crisisResources}>
        <Text style={styles.crisisResourceLabel}>{t('solve.crisisHotlines')}</Text>
        <Text style={styles.crisisResourceItem}>🇺🇸 US: {crisis.resources.US}</Text>
        <Text style={styles.crisisResourceItem}>🇪🇸 Spain: {crisis.resources.ES}</Text>
      </View>
      <Pressable style={styles.crisisButton} onPress={onDismiss}>
        <Text style={styles.crisisButtonText}>{t('common.confirm')}</Text>
      </Pressable>
    </View>
  </View>
);

// Options Card Component (for Options step)
const OptionsCards: React.FC<{
  options: string[];
  onSelect: (option: string) => void;
  disabled: boolean;
}> = ({ options, onSelect, disabled }) => (
  <View style={styles.optionsContainer}>
    <Text style={styles.optionsTitle}>{t('solve.selectOption')}</Text>
    {options.map((option, index) => (
      <Pressable
        key={index}
        style={[styles.optionCard, disabled && styles.optionCardDisabled]}
        onPress={() => onSelect(option)}
        disabled={disabled}
      >
        <Text style={styles.optionLetter}>{String.fromCharCode(65 + index)}</Text>
        <Text style={styles.optionText}>{option}</Text>
      </Pressable>
    ))}
  </View>
);

// Commit Form Component (for Commit step)
const CommitForm: React.FC<{
  onSubmit: (action: string, reminderTime?: string) => void;
  disabled: boolean;
}> = ({ onSubmit, disabled }) => {
  const [action, setAction] = useState('');
  const [enableReminder, setEnableReminder] = useState(false);
  const [reminderHours, setReminderHours] = useState('24');

  const handleSubmit = () => {
    if (!action.trim()) return;

    let reminderTime: string | undefined;
    if (enableReminder) {
      const hours = parseInt(reminderHours, 10) || 24;
      const date = new Date();
      date.setHours(date.getHours() + hours);
      reminderTime = date.toISOString();
    }

    onSubmit(action.trim(), reminderTime);
  };

  return (
    <View style={styles.commitContainer}>
      <Text style={styles.commitTitle}>{t('solve.commitTitle')}</Text>
      <Text style={styles.commitLabel}>{t('solve.firstStepAction')}</Text>
      <TextInput
        style={styles.commitInput}
        value={action}
        onChangeText={setAction}
        placeholder={t('solve.actionPlaceholder')}
        multiline
        editable={!disabled}
      />

      <Pressable
        style={styles.reminderToggle}
        onPress={() => setEnableReminder(!enableReminder)}
        disabled={disabled}
      >
        <View style={[styles.checkbox, enableReminder && styles.checkboxChecked]}>
          {enableReminder && <Text style={styles.checkboxCheck}>✓</Text>}
        </View>
        <Text style={styles.reminderLabel}>{t('solve.setReminder')}</Text>
      </Pressable>

      {enableReminder && (
        <View style={styles.reminderRow}>
          <Text style={styles.reminderText}>{t('solve.remindIn')}</Text>
          <TextInput
            style={styles.reminderInput}
            value={reminderHours}
            onChangeText={setReminderHours}
            keyboardType="number-pad"
            editable={!disabled}
          />
          <Text style={styles.reminderText}>{t('solve.hours')}</Text>
        </View>
      )}

      <Pressable
        style={[styles.commitButton, (!action.trim() || disabled) && styles.commitButtonDisabled]}
        onPress={handleSubmit}
        disabled={!action.trim() || disabled}
      >
        <Text style={styles.commitButtonText}>{t('solve.complete')}</Text>
      </Pressable>
    </View>
  );
};

// Main Session Screen
const SessionScreen: React.FC = () => {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const [sessionId, setSessionId] = useState<string | null>(id === 'new' ? null : id);
  const [currentStep, setCurrentStep] = useState<SolveStep>('receive');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [crisis, setCrisis] = useState<CrisisResponse | null>(null);
  const [options, setOptions] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const flatListRef = useRef<FlatList>(null);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      if (id === 'new') {
        setIsLoading(true);
        try {
          const session = await createSession();
          setSessionId(session.session_id);
          setCurrentStep(session.current_step);
          // Update URL without navigation
          router.setParams({ id: session.session_id });
        } catch (err) {
          setError(err instanceof Error ? err.message : t('solve.createFailed'));
        } finally {
          setIsLoading(false);
        }
      } else if (id) {
        // Load existing session history
        const history = await getAllMessages(id);
        setMessages(history);
      }
    };

    void initSession();
  }, [id, router]);

  // Parse options from assistant message
  const parseOptions = useCallback((content: string): string[] => {
    const optionPattern = /[A-D]\)\s*(.+?)(?=\n[A-D]\)|$)/gs;
    const matches = [...content.matchAll(optionPattern)];
    return matches.map((m) => m[1].trim()).filter(Boolean);
  }, []);

  // Handle sending a message
  const handleSend = useCallback(async () => {
    if (!sessionId || !inputText.trim() || isStreaming) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputText.trim(),
      step: currentStep,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsStreaming(true);
    setStreamingContent('');
    setError(null);

    // Save user message to history
    await updateStepEntry(sessionId, currentStep, userMessage);

    await streamMessage(sessionId, userMessage.content, currentStep, {
      onToken: (content) => {
        setStreamingContent((prev) => prev + content);
      },
      onDone: async (data: StreamDoneEvent) => {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: streamingContent,
          step: currentStep,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setStreamingContent('');
        setIsStreaming(false);

        // Save assistant message and mark step complete if transitioning
        await updateStepEntry(sessionId, currentStep, assistantMessage, !!data.next_step);

        if (data.next_step) {
          setCurrentStep(data.next_step);

          // Parse options if entering options step
          if (data.next_step === 'options') {
            const parsed = parseOptions(streamingContent);
            if (parsed.length > 0) {
              setOptions(parsed);
            }
          }
        }

        // Check if session is complete
        if (currentStep === 'commit' && !data.next_step) {
          setIsComplete(true);
        }
      },
      onCrisis: (data: CrisisResponse) => {
        setCrisis(data);
        setIsStreaming(false);
        setStreamingContent('');
      },
      onError: (err) => {
        setError(err.message);
        setIsStreaming(false);
        setStreamingContent('');
      },
    });
  }, [sessionId, inputText, currentStep, isStreaming, streamingContent, parseOptions]);

  // Handle option selection
  const handleOptionSelect = useCallback(
    async (option: string) => {
      if (!sessionId) return;

      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: option,
        step: currentStep,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setOptions([]);

      await updateStepEntry(sessionId, currentStep, userMessage);

      // Move to commit step
      setCurrentStep('commit');
    },
    [sessionId, currentStep]
  );

  // Handle commit form submission
  const handleCommit = useCallback(
    async (action: string, reminderTime?: string) => {
      if (!sessionId) return;

      setIsLoading(true);
      try {
        await patchSession(sessionId, {
          status: 'completed',
          first_step_action: action,
          reminder_time: reminderTime,
        });

        setIsComplete(true);

        Alert.alert(t('solve.sessionComplete'), t('solve.sessionCompleteMessage'), [
          { text: t('common.done'), onPress: () => router.back() },
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : t('solve.updateFailed'));
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, router]
  );

  // Render message item
  const renderMessage = useCallback(
    ({ item }: { item: Message }) => <MessageBubble message={item} />,
    []
  );

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages.length, streamingContent]);

  // Show loading state
  if (isLoading && !sessionId) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1d4ed8" />
        <Text style={styles.loadingText}>{t('solve.creating')}</Text>
      </View>
    );
  }

  return (
    <>
      <Stack.Screen
        options={{
          title: t('solve.sessionTitle'),
          headerBackTitle: t('common.back'),
        }}
      />

      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={90}
      >
        {/* Crisis Overlay */}
        {crisis && <CrisisAlert crisis={crisis} onDismiss={() => setCrisis(null)} />}

        {/* Step Progress */}
        <StepProgressBar currentStep={currentStep} />

        {/* Messages */}
        <FlatList
          ref={flatListRef}
          style={styles.messageList}
          contentContainerStyle={styles.messageListContent}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item) => item.id}
          ListFooterComponent={
            streamingContent ? (
              <View style={[styles.messageBubble, styles.assistantBubble]}>
                <Text style={styles.messageText}>{streamingContent}</Text>
                <ActivityIndicator size="small" color="#64748b" style={styles.streamingIndicator} />
              </View>
            ) : null
          }
        />

        {/* Error */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {/* Options Cards (for options step) */}
        {currentStep === 'options' && options.length > 0 && !isComplete && (
          <OptionsCards
            options={options}
            onSelect={handleOptionSelect}
            disabled={isStreaming || isLoading}
          />
        )}

        {/* Commit Form (for commit step) */}
        {currentStep === 'commit' && !isComplete && options.length === 0 && (
          <CommitForm onSubmit={handleCommit} disabled={isStreaming || isLoading} />
        )}

        {/* Input Area (for other steps) */}
        {!isComplete && currentStep !== 'commit' && options.length === 0 && (
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              value={inputText}
              onChangeText={setInputText}
              placeholder={t('solve.inputPlaceholder')}
              multiline
              editable={!isStreaming}
            />
            <Pressable
              style={[
                styles.sendButton,
                (!inputText.trim() || isStreaming) && styles.sendButtonDisabled,
              ]}
              onPress={handleSend}
              disabled={!inputText.trim() || isStreaming}
            >
              {isStreaming ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <Text style={styles.sendButtonText}>→</Text>
              )}
            </Pressable>
          </View>
        )}

        {/* Complete State */}
        {isComplete && (
          <View style={styles.completeContainer}>
            <Text style={styles.completeText}>{t('solve.completed')}</Text>
            <Pressable style={styles.completeButton} onPress={() => router.back()}>
              <Text style={styles.completeButtonText}>{t('common.done')}</Text>
            </Pressable>
          </View>
        )}
      </KeyboardAvoidingView>
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8fafc',
  },
  loadingText: {
    marginTop: 12,
    color: '#64748b',
    fontSize: 16,
  },

  // Progress Bar
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  stepItem: {
    alignItems: 'center',
    flex: 1,
  },
  stepCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e2e8f0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepCompleted: {
    backgroundColor: '#16a34a',
  },
  stepCurrent: {
    backgroundColor: '#1d4ed8',
  },
  stepCheckmark: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  stepNumber: {
    color: '#64748b',
    fontSize: 12,
    fontWeight: '600',
  },
  stepNumberCurrent: {
    color: '#fff',
  },
  stepLabel: {
    marginTop: 4,
    fontSize: 10,
    color: '#94a3b8',
    textAlign: 'center',
  },
  stepLabelCompleted: {
    color: '#16a34a',
  },
  stepLabelCurrent: {
    color: '#1d4ed8',
    fontWeight: '600',
  },
  stepLine: {
    position: 'absolute',
    top: 14,
    right: -20,
    width: 40,
    height: 2,
    backgroundColor: '#e2e8f0',
    zIndex: -1,
  },
  stepLineCompleted: {
    backgroundColor: '#16a34a',
  },

  // Messages
  messageList: {
    flex: 1,
  },
  messageListContent: {
    padding: 16,
    gap: 12,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#1d4ed8',
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderBottomLeftRadius: 4,
    shadowColor: '#0f172a',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
    color: '#0f172a',
  },
  userMessageText: {
    color: '#fff',
  },
  streamingIndicator: {
    marginTop: 8,
  },

  // Error
  errorContainer: {
    padding: 12,
    backgroundColor: '#fef2f2',
    borderTopWidth: 1,
    borderTopColor: '#fecaca',
  },
  errorText: {
    color: '#dc2626',
    fontSize: 14,
    textAlign: 'center',
  },

  // Input
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    gap: 8,
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    backgroundColor: '#f8fafc',
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1d4ed8',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#94a3b8',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },

  // Options
  optionsContainer: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  optionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 12,
  },
  optionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    marginBottom: 8,
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  optionCardDisabled: {
    opacity: 0.5,
  },
  optionLetter: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#1d4ed8',
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
    textAlign: 'center',
    lineHeight: 28,
    marginRight: 12,
  },
  optionText: {
    flex: 1,
    fontSize: 14,
    color: '#0f172a',
    lineHeight: 20,
  },

  // Commit Form
  commitContainer: {
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  commitTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 12,
  },
  commitLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#334155',
    marginBottom: 8,
  },
  commitInput: {
    minHeight: 80,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    padding: 12,
    fontSize: 15,
    backgroundColor: '#f8fafc',
    textAlignVertical: 'top',
  },
  reminderToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#cbd5e1',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  checkboxChecked: {
    backgroundColor: '#1d4ed8',
    borderColor: '#1d4ed8',
  },
  checkboxCheck: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  reminderLabel: {
    fontSize: 14,
    color: '#334155',
  },
  reminderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    gap: 8,
  },
  reminderText: {
    fontSize: 14,
    color: '#64748b',
  },
  reminderInput: {
    width: 60,
    height: 36,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
    textAlign: 'center',
    fontSize: 14,
  },
  commitButton: {
    marginTop: 20,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#16a34a',
    alignItems: 'center',
  },
  commitButtonDisabled: {
    backgroundColor: '#94a3b8',
  },
  commitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },

  // Complete
  completeContainer: {
    padding: 24,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    alignItems: 'center',
  },
  completeText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#16a34a',
    marginBottom: 16,
  },
  completeButton: {
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 12,
    backgroundColor: '#1d4ed8',
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },

  // Crisis
  crisisOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 100,
    padding: 24,
  },
  crisisCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 340,
  },
  crisisTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#dc2626',
    marginBottom: 12,
    textAlign: 'center',
  },
  crisisMessage: {
    fontSize: 15,
    color: '#334155',
    lineHeight: 22,
    textAlign: 'center',
    marginBottom: 20,
  },
  crisisResources: {
    backgroundColor: '#fef2f2',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  crisisResourceLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#dc2626',
    marginBottom: 8,
  },
  crisisResourceItem: {
    fontSize: 16,
    color: '#0f172a',
    marginVertical: 4,
  },
  crisisButton: {
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#1d4ed8',
    alignItems: 'center',
  },
  crisisButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default SessionScreen;
