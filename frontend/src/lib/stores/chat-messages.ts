import { get, writable } from 'svelte/store';
import { activeChat } from './chat-history';
import { get as getStore } from 'svelte/store';
import { SOURCE_DELIMITER } from '$lib/constants';
export interface ChatTranscript {
	messages: ChatCompletionRequestMessage[];
	chatState: 'idle' | 'loading' | 'error' | 'message';
}

export type ChatCompletionRequestMessage = {
	role: string;
	content: string;
}

const { subscribe, update, ...store } = writable<ChatTranscript>({
	messages: [
	],
	chatState: 'idle'
});

const set = async (query: string) => {
	console.log('📝 Processing new message:', query);
	updateMessages(query, 'user', 'loading');
	const currentActiveChat = getStore(activeChat);
	const currentMessages = get(chatMessages).messages;

	try {
		console.log('🔄 Fetching response from API...');
		const response = await fetch("http://localhost:8000/query", {
			method: "POST",
			body: JSON.stringify({
				messages: currentMessages,
			}),
			headers: { 'Content-Type': 'application/json' },
		});
		const data = await response.json();
		console.log('🔄 Response from API:', data);
		
		// Update the answer and messages
		if (get(answer) === '...') answer.set('');
		
		// Format answer with sources
		const formattedAnswer = `${data.answer}\n${data.sources.map((source: any) => `${SOURCE_DELIMITER}${source.url}${SOURCE_DELIMITER}`).join('')}`;
		
		answer.update((_a) => _a + formattedAnswer);
		updateMessages(get(answer), 'assistant', 'idle');
		answer.set('');
		
		// Update sources store
		sources.set(data.sources);

		// Save to database if we have an active chat
		if (currentActiveChat) {
			console.log('💾 Saving messages to existing chat:', currentActiveChat);
			await updateChatInDatabase(currentActiveChat);
		}
	} catch (err) {
		console.error('❌ Error processing message:', err);
		updateMessages(String(err), 'system', 'error');
	}
};

// New function to update chat in database
const updateChatInDatabase = async (chatId: string) => {
	const currentMessages = get(chatMessages).messages;
	console.log('📤 Sending messages to database:', {
		chatId,
		messageCount: currentMessages.length,
		messages: currentMessages
	});
	
	try {
		const response = await fetch(`/api/chats/${chatId}/messages`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ messages: currentMessages })
		});
		const updatedChat = await response.json();
		console.log('✅ Messages saved successfully:', {
			chatId: updatedChat.id,
			messageCount: updatedChat.messages.length
		});
	} catch (error) {
		console.error('❌ Failed to save messages:', error);
	}
};

const replace = (messages: ChatTranscript) => {
	store.set(messages);
};

const reset = () =>
	store.set({
		messages: [
		],
		chatState: 'idle'
	});
const updateMessages = (content: string, role: string, state: 'idle' | 'loading' | 'error' | 'message') => {
	chatMessages.update((messages: ChatTranscript) => {
		return { messages: [...messages.messages, { role: role, content: content }], chatState: state };
	});
};


export const chatMessages = { subscribe, set, update, reset, replace };
export const answer = writable<string>('');
export const sources = writable<string[]>([]);
