<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Send } from 'lucide-svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';

	import { chatMessages, answer } from '$lib/stores/chat-messages';
	import ChatHistory from '$lib/components/ChatHistory.svelte';
	import { activeChat, fetchChats } from '$lib/stores/chat-history';

	let query = '';
	let messagesContainer: HTMLDivElement;
	let isLoading = false;
	let textareaElement: HTMLTextAreaElement;

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

		// Reset textarea height
		if (textareaElement) {
			textareaElement.style.height = '1.25rem';
		}

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
							{ role: 'assistant', content: 'Hello, how can I help you today?' },
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

<div class="grid h-screen w-full bg-[#F7F7F8] dark:bg-gray-900 md:grid-cols-[17.5rem_1fr]">
	<!-- Sidebar -->
	<div class="hidden border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 md:block">
		<div class="flex h-full flex-col">
			<div class="flex h-14 items-center border-b border-gray-200 dark:border-gray-700 px-4 lg:h-[7rem] lg:px-6">
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
	<div class="flex h-screen flex-col bg-white dark:bg-gray-900">
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
				class="flex-1 overflow-y-auto scroll-smooth
					   scrollbar scrollbar-w-3 scrollbar-track-transparent 
					   scrollbar-thumb-gray-300 scrollbar-thumb-rounded-lg"
				bind:this={messagesContainer}
			>
				<div class="max-w-3xl mx-auto px-6 py-6">
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
			<div>
				<div class="max-w-3xl mx-auto px-6 pb-4">
					<form
						class="flex items-end gap-4 relative"
						on:submit|preventDefault={handleSubmit}
					>
						<div class="relative w-full">
							<textarea 
								bind:this={textareaElement}
								bind:value={query} 
								class="w-full min-h-[7rem] max-h-[12.5rem] py-4 px-5 
									   rounded-2xl border border-gray-200 
									   focus:outline-none
									   bg-gray-100 dark:bg-gray-800 
									   text-gray-800 dark:text-white 
									   placeholder:text-gray-400 dark:placeholder:text-gray-400
									   text-sm leading-normal
									   resize-none overflow-y-auto
									   scrollbar-none"
								placeholder="Message UniLLM..."
								disabled={isLoading}
								rows="1"
								on:keydown={(e) => {
									if (e.key === 'Enter' && !e.shiftKey) {
										e.preventDefault();
										handleSubmit();
									}
								}}
								on:input={(e) => {
									if(e && e.target && e.target instanceof HTMLTextAreaElement){
										e.target.style.height = 'auto';
										e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
									}
								}}
							/>
							
							<Button 
								type="submit"
								class="absolute right-2 bottom-3
									   p-2 rounded-full
									   text-white disabled:bg-gray-400 
									   transform hover:scale-105
									   transition-all duration-200
									   disabled:hover:scale-100
									   disabled:opacity-70"
								disabled={isLoading || !query.trim()}
							>
								<Send class="w-5 h-5" />
							</Button>
						</div>
					</form>

					<div class="flex items-center justify-center gap-2 mt-5">
						<p class="text-xs text-[#666666] dark:text-gray-400">
							UniLLM can make mistakes. Consider checking important information.
						</p>
						{#if !isLoading && $chatMessages.messages.length > 0}
							<button 
								class="text-xs text-[#1E88E5] hover:text-[#1565C0] dark:text-blue-400 
									   hover:underline transition-colors duration-200"
								on:click={() => {/* Add regenerate functionality */}}
							>
								Regenerate response
							</button>
						{/if}
					</div>
				</div>
			</div>
		</main>
	</div>
</div>
