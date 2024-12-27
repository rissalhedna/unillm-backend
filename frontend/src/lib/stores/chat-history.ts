import { writable, get } from 'svelte/store';
import { chatMessages } from './chat-messages';

export const chatHistorySubscription = writable();
export const activeChat = writable<string | null>(null);

export const fetchChats = async () => {
	const response = await fetch('/api/chats');
	const chats = await response.json();
	chatHistorySubscription.set(chats);
};

export const deleteChat = async (id: string) => {
	await fetch(`/api/chats/${id}`, { method: 'DELETE' });
	await fetchChats();
};

export const updateChatTitle = async (id: string, title: string) => {
	await fetch(`/api/chats/${id}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ title })
	});
	await fetchChats();
};

export const loadMessages = async (chatId: string) => {
	if (get(chatMessages).chatState !== 'idle') return;

	const response = await fetch(`/api/chats/${chatId}`);
	const chat = await response.json();

	chatMessages.replace({
		messages: chat.messages.map(({ role, content }: { role: string, content: string }) => ({ role, content })),
		chatState: 'idle'
	});
	activeChat.set(chatId);
};
