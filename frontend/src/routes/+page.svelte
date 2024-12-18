<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Send } from 'lucide-svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';

	import { chatMessages, answer } from '$lib/stores/chat-messages';
	import ChatHistory from '$lib/components/ChatHistory.svelte';
	import { activeChat, fetchChats } from '$lib/stores/chat-history';

	let query = '';
	let messagesContainer: HTMLDivElement;
	let isLoading = false;

	const scrollToBottom = () => {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	};

	const handleSubmit = async () => {
		if (!query.trim()) return;
		const currentQuery = query;
		query = '';
		isLoading = true;
		answer.set('');

		// If this is a new chat (no active chat), create it first
		if (!$activeChat) {
			console.log('🆕 Creating new chat with first message:', currentQuery);
			try {
				const response = await fetch('/api/chats', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ 
						title: currentQuery, 
						messages: [
							{ role: 'assistant', content: 'Hello, I am your virtual assistant. How can I help you?' },
							{ role: 'user', content: currentQuery }
						] 
					})
				});
				const chat = await response.json();
				console.log('✅ New chat created:', {
					chatId: chat.id,
					title: chat.title
				});
				activeChat.set(chat.id);
				await fetchChats(); // Update sidebar immediately
			} catch (error) {
				console.error('❌ Failed to create new chat:', error);
			}
		}

		// Process the message
		await chatMessages.set(currentQuery);
		
		scrollToBottom();
		isLoading = false;
	};

	$: if ($answer) {
		setTimeout(scrollToBottom, 0);
	}
</script>

<div class="grid h-screen w-full bg-white dark:bg-gray-800 md:grid-cols-[260px_1fr]">
	<!-- Sidebar -->
	<div class="hidden border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 md:block">
		<div class="flex h-full flex-col">
			<div class="flex h-14 items-center border-b border-gray-200 dark:border-gray-700 px-4 lg:h-[60px] lg:px-6">
				<a href="/" class="flex items-center gap-2 font-semibold text-gray-800 dark:text-white">
					<span class="text-xl">UniLLM</span>
				</a>
			</div>
			<div class="flex-1 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
				<ChatHistory />
			</div>
			<div class="p-4">
				<!-- Add new chat button here if needed -->
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<div class="flex h-screen flex-col bg-white dark:bg-gray-800">
		<!-- Header -->
		<header class="flex h-14 items-center gap-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 lg:h-[60px] lg:px-6">
		</header>

		<!-- Main Chat Area -->
		<main class="flex h-[calc(100vh-60px)] flex-1 flex-col relative">
			<!-- Welcome message when no messages -->
			{#if $chatMessages.messages.length === 0}
				<div class="flex-1 overflow-hidden py-32 px-4 text-center">
					<h1 class="text-4xl font-bold mb-8 text-gray-800 dark:text-white">Welcome to UniLLM</h1>
					<p class="text-gray-600 dark:text-gray-300">How can I help you today?</p>
				</div>
			{/if}

			<!-- Scrollable Messages Container -->
			<div 
				class="flex-1 overflow-y-auto scroll-smooth [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
				bind:this={messagesContainer}
			>
				<div class="max-w-3xl mx-auto px-4 py-6">
					<div class="flex flex-col gap-6">
						{#each $chatMessages.messages as message}
							<ChatMessage type={message.role} message={message.content} />
						{/each}

						{#if $answer}
							<ChatMessage type="assistant" message={$answer} />
						{/if}

						{#if isLoading}
							<ChatMessage type="assistant" isLoading={true} />
						{/if}
					</div>
				</div>
			</div>

			<!-- Fixed Input Form -->
			<div class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
				<div class="max-w-3xl mx-auto px-4 py-4">
					<form
						class="flex items-center gap-4 relative"
						on:submit|preventDefault={handleSubmit}
					>
						<Input 
							type="text" 
							bind:value={query} 
							class="w-full py-3 px-4 rounded-lg border border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-blue-500/20 dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
							placeholder="Message UniLLM..."
							disabled={isLoading}
						/>
						<Button 
							type="submit"
							class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50 transition-colors"
							disabled={isLoading || !query.trim()}
						>
							<Send class="w-5 h-5" />
						</Button>
					</form>
					<p class="mt-2 text-xs text-center text-gray-500 dark:text-gray-400">
						UniLLM can make mistakes. Consider checking important information.
					</p>
				</div>
			</div>
		</main>
	</div>
</div>
