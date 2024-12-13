import { get, writable } from 'svelte/store';

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
	updateMessages(query, 'user', 'loading');


	try {
		const response = await fetch("http://localhost:8000/query",
			{
				method: "POST",
				body: JSON.stringify({
					text: query,
					collection_name: "study-in-germany",
				}),
				headers: {
					'Content-Type': 'application/json'
				},
			});
		const data = await response.json();
		if (get(answer) === '...') answer.set('');
		answer.update((_a) => _a + data.answer);
		updateMessages(get(answer), 'assistant', 'idle');
		answer.set('');
	} catch (err) {
		console.log(err)
		updateMessages(String(err), 'system', 'error');
	}
	// const eventSource = new SSE('/api/chat', {
	// 	headers: {
	// 		'Content-Type': 'application/json'
	// 	},
	// 	payload: JSON.stringify({ messages: get(chatMessages).messages })
	// });
	//
	// eventSource.addEventListener('error', handleError);
	// eventSource.addEventListener('message', streamMessage);
	// eventSource.stream();
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

const updateMessages = (content: string, role: string, state: string) => {
	chatMessages.update((messages: ChatTranscript) => {
		return { messages: [...messages.messages, { role: role, content: content }], chatState: state };
	});
};


export const chatMessages = { subscribe, set, update, reset, replace };
export const answer = writable<string>('');