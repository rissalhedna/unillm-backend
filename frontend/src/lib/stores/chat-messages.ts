import { get, writable } from 'svelte/store';
import { activeChat } from './chat-history';
import { get as getStore } from 'svelte/store';

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
		{ role: 'assistant', content: 'Hello, I am your virtual assistant. How can I help you?' },
	],
	chatState: 'idle'
});

const set = async (query: string) => {
	console.log('📝 Processing new message:', query);
	updateMessages(query, 'user', 'loading');
	const currentActiveChat = getStore(activeChat);

	try {
		console.log('🔄 Fetching response from API...');
		const response = await fetch("http://localhost:8000/query", {
			method: "POST",
			body: JSON.stringify({
				text: query,
				collection_name: "study-in-germany",
			}),
			headers: { 'Content-Type': 'application/json' },
		});
		const data = await response.json();
		
		// Update the answer and messages
		if (get(answer) === '...') answer.set('');
		answer.update((_a) => _a + data.answer);
		updateMessages(get(answer), 'assistant', 'idle');
		answer.set('');

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
			{ role: 'assistant', content: 'Hello, I am your virtual assistant. How can I help you?' }
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