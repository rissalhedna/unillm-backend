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

	// Add these arrays to your existing script section
	const popularTopics = [
		{
			icon: "🏛️",
			title: "How do I apply for a German student visa?",
			query: "What are the steps to apply for a student visa in Germany?"
		},
		{
			icon: "🏠",
			title: "Finding accommodation in Germany",
			query: "How can I find an apartment in Germany? What is the process?"
		},

	];

	const gettingStarted = [
		{
			icon: "🗣️",
			title: "Learning German language",
			query: "What are the best ways to learn German? Where should I start?"
		},
		{
			icon: "🎓",
			title: "Study in Germany",
			query: "What are the requirements to study at a German university?"
		},

	];

	function handleImageError(event: Event) {
		const target = event.target as HTMLImageElement;
		target.outerHTML = '<span class="text-4xl">🇩🇪</span>';
	}
</script>

<div class="grid h-screen w-full bg-[#F7F7F8] dark:bg-gray-900 md:grid-cols-[17.5rem_1fr]">
	<!-- Sidebar -->
	<div class="hidden border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 md:block h-screen overflow-hidden">
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
	<div class="flex h-screen flex-col bg-white dark:bg-gray-900">
		<!-- Header -->
		<header class="flex h-14 items-center gap-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 lg:h-[60px] lg:px-6">
		</header>

		<!-- Main Chat Area -->
		<main class="flex h-[calc(100vh-60px)] flex-1 flex-col relative">

			<!-- Scrollable Messages Container -->
			<div 
				class="flex-1 overflow-y-auto scroll-smooth
					   scrollbar scrollbar-w-3 scrollbar-track-transparent 
					   scrollbar-thumb-gray-300 scrollbar-thumb-rounded-lg"
				bind:this={messagesContainer}
			>
				<div class="max-w-5xl mx-auto px-4 py-6">
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
							<!-- Welcome message when no messages -->
			{#if $chatMessages.messages.length === 0}
			<div class="flex-1 justify-center items-center px-4 pt-12">
				<!-- Welcome Header -->
				<div class="text-center mb-8">
					<div class="flex justify-center mb-6">
						<div class="w-16 h-16 rounded-full shadow-lg bg-gray-50 dark:bg-gray-800 flex items-center justify-center">
							{#if !import.meta.env.PROD}
								<!-- Development fallback -->
								<span class="text-4xl">🇩🇪</span>
							{:else}
								<img 
									src="/german-flag-icon.svg" 
									alt="German Assistant"
									class="w-full h-full object-cover rounded-full"
									on:error={handleImageError}
								/>
							{/if}
						</div>
					</div>
					<h1 class="text-4xl font-bold mb-3 text-gray-800 dark:text-white">
						Welcome to uniLLM
					</h1>
					<p class="text-gray-600 dark:text-gray-300 max-w-xl mx-auto">
						Your information source for everything about Germany - from visa applications to daily life
					</p>
				</div>

				<!-- Example Questions Grid -->
				<div class="max-w-3xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 px-4">
					<!-- Popular Topics Column -->
					<div class="space-y-4">
						<h2 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">
							Popular Topics
						</h2>
						<div class="flex flex-col gap-4">
							{#each popularTopics as {icon, title, query: topicQuery}}
								<button 
									class="w-full text-left p-4 rounded-xl bg-gray-50 hover:bg-gray-100 
										   dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors
										   flex items-center gap-3 group"
									on:click={() => {
										query = topicQuery;
										handleSubmit();
									}}
								>
									<span class="text-2xl">{icon}</span>
									<span class="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 
											   dark:group-hover:text-white transition-colors">
										{title}
									</span>
								</button>
							{/each}
						</div>
					</div>

					<!-- Getting Started Column -->
					<div class="space-y-4">
						<h2 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">
							Getting Started
						</h2>
						<div class="flex flex-col gap-4">
							{#each gettingStarted as {icon, title, query: topicQuery}}
								<button 
									class="w-full text-left p-4 rounded-xl bg-gray-50 hover:bg-gray-100 
										   dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors
										   flex items-center gap-3 group"
									on:click={() => {
										query = topicQuery;
										handleSubmit();
									}}
								>
									<span class="text-2xl">{icon}</span>
									<span class="text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 
											   dark:group-hover:text-white transition-colors">
										{title}
									</span>
								</button>
							{/each}
						</div>
					</div>
				</div>
			</div>
		{/if}
			</div>

			<!-- Fixed Input Form -->
			<div>
				<div class="max-w-5xl mx-auto px-4 pb-4">
					<form
						class="flex justify-center items-end gap-4 relative"
						on:submit|preventDefault={handleSubmit}
					>
						<div class="relative w-full max-w-2xl">
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

					<div class="flex items-center justify-center gap-2 mt-5 max-w-2xl mx-auto">
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
