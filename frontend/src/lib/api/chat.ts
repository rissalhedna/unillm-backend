import type { Chat, ChatCompletionRequestMessage } from '../types';

export async function createChat(title: string, messages: ChatCompletionRequestMessage[]): Promise<Chat> {
    console.log('Creating new chat:', { title, messageCount: messages.length });

    const response = await fetch('/api/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, messages })
    });

    const chat = await response.json();
    console.log('Chat created:', { id: chat.id });
    return chat;
}

export async function updateChatMessages(chatId: string, messages: ChatCompletionRequestMessage[]): Promise<Chat> {
    console.log('Updating messages:', { chatId, messageCount: messages.length });

    const response = await fetch(`/api/chats/${chatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
    });

    const chat = await response.json();
    console.log('Messages updated:', { id: chat.id });
    return chat;
}

export async function fetchChats(): Promise<Chat[]> {
    const response = await fetch('/api/chats');
    return response.json();
}

export async function fetchChat(id: string): Promise<Chat> {
    const response = await fetch(`/api/chats/${id}`);
    return response.json();
}
