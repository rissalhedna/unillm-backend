<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Send } from 'lucide-svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';

	import { chatMessages, answer } from '$lib/stores/chat-messages';
	import ChatHistory from '$lib/components/ChatHistory.svelte';
	import { activeChat, fetchChats } from '$lib/stores/chat-history';

	let query = '';
	let messagesContainer: HTMLDivElement;
	$: isLoading = $chatMessages.chatState === 'loading';
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
		answer.set('');

		// Reset textarea height
		if (textareaElement) {
			textareaElement.style.height = '1.25rem';
		}

		// Add this line to scroll to bottom when loading starts
		setTimeout(scrollToBottom, 0);

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
	};

	$: if ($answer) {
		setTimeout(scrollToBottom, 0);
	}

	// Add this reactive statement to scroll when messages change
	$: if ($chatMessages.messages.length > 0) {
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

<div class="grid h-screen w-full bg-gradient-to-br from-[#f3f4f6] to-[#e5e7eb] dark:from-gray-900 dark:to-gray-800 md:grid-cols-[17.5rem_1fr] relative overflow-hidden">
	<!-- Sidebar - removed border-r -->
	<div class="hidden bg-[#f8f9fa] dark:bg-gray-800/50 md:block h-screen overflow-hidden backdrop-blur-sm border-r border-[#dd1c1a]/10">
		<div class="flex h-full flex-col">
			<div class="flex h-14 items-center px-4 lg:h-[60px] lg:px-6 bg-[#dd1c1a]/5 dark:bg-gray-800/80">
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

	<!-- Main Content - updated background colors -->
	<div class="flex h-screen flex-col bg-white/70 dark:bg-gray-900/70 backdrop-blur-sm">
		<!-- Header - removed border-b -->
		<header class="flex h-14 items-center gap-4 bg-[#f8f9fa]/90 dark:bg-gray-800/90
				   px-4 lg:h-[60px] lg:px-6 border-b border-[#dd1c1a]/10">
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
					<div class="flex flex-col gap-4">
						{#each $chatMessages.messages as message}
							<ChatMessage
								type={message.role}
								message={message.content}
								class="px-4 py-3 rounded-lg
									   {message.role === 'user' ?
									   'bg-[#dd1c1a]/5 ml-auto max-w-[85%] md:max-w-[75%]' :
									   'bg-gray-100 dark:bg-gray-800/50 mr-auto max-w-[85%] md:max-w-[75%]'}
									   border border-[#dd1c1a]/10
									   shadow-sm"
							/>
						{/each}

						{#if $answer}
							<ChatMessage
								type="assistant"
								message={$answer}
								class="px-4 py-3 rounded-lg
									   bg-gray-100 dark:bg-gray-800/50
									   mr-auto max-w-[85%] md:max-w-[75%]
									   border border-[#dd1c1a]/10
									   shadow-sm"
							/>
						{/if}

						{#if isLoading}
							<div class="px-4 py-3 rounded-lg
									  bg-gray-100 dark:bg-gray-800/50
									  mr-auto max-w-[85%] md:max-w-[75%]
									  border border-[#dd1c1a]/10
									  shadow-sm">
								<div class="flex gap-1">
									<span class="w-1 h-1 rounded-full bg-black animate-bounce [animation-delay:-0.3s]"></span>
									<span class="w-1 h-1 rounded-full bg-black animate-bounce [animation-delay:-0.15s]"></span>
									<span class="w-1 h-1 rounded-full bg-black animate-bounce"></span>
								</div>
							</div>
						{/if}
					</div>
				</div>
							<!-- Welcome message when no messages -->
			{#if $chatMessages.messages.length === 0}
			<div class="flex-1 justify-center items-center px-4 pt-12">
				<!-- Welcome Header -->
				<div class="text-center">
					<div class="flex justify-center mb-6">
						<div class="w-16 h-16 rounded-full shadow-lg bg-gray-50 dark:bg-gray-800
									flex items-center justify-center
									border-2 border-[#dd1c1a]/20">
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
					<h1 class="text-4xl font-bold mb-20 text-gray-800 dark:text-white">
						Ask me anything about Germany!
					</h1>
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
									class="w-full text-left p-4 rounded-xl bg-gray-50 hover:bg-[#dd1c1a]/5
										   dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors
										   border border-[#dd1c1a]/10 hover:border-[#dd1c1a]/20
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
									class="w-full text-left p-4 rounded-xl bg-gray-50 hover:bg-[#dd1c1a]/5
										   dark:bg-gray-800 dark:hover:bg-gray-700 transition-colors
										   border border-[#dd1c1a]/10 hover:border-[#dd1c1a]/20
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
									   rounded-2xl border-2 border-[#dd1c1a]/20
									   focus:border-[#dd1c1a]/30 focus:outline-none
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
									   bg-[#dd1c1a] hover:bg-[#dd1c1a]/90
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
								class="text-xs text-[#dd1c1a] hover:text-[#dd1c1a]/80 dark:text-[#dd1c1a]/90
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
