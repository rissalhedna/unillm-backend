<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Send } from 'lucide-svelte';
	import ChatMessage from '$lib/components/ChatMessage.svelte';

	import { chatMessages, answer } from '$lib/stores/chat-messages';
	import ChatHistory from '$lib/components/ChatHistory.svelte';

	let query = '';

	const handleSubmit = async () => {
		answer.set('...');
		await chatMessages.set(query);
		query = '';
	};
</script>

<div class="grid h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
	<!-- Sidebar -->
	<div class="hidden border-r bg-muted/40 md:block">
		<div class="flex h-full flex-col">
			<div class="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
				<a href="/" class="flex items-center gap-2 font-semibold">
					<span class="">UniLLM</span>
				</a>
			</div>
			<div class="flex-1 overflow-y-auto">
				<ChatHistory />
			</div>
			<div class="p-4"></div>
		</div>
	</div>

	<!-- Main Content -->
	<div class="flex h-screen flex-col">
		<!-- Header -->
		<header
			class="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6"
		></header>

		<!-- Main Chat Area -->
		<main class="flex h-[calc(100vh-60px)] flex-1 flex-col">
			<!-- Scrollable Messages Container -->
			<div class="flex-1 overflow-y-auto p-4">
				<div class="flex flex-col gap-4 rounded-md">
					<div class="flex flex-col gap-2">
						{#each $chatMessages.messages as message}
							<ChatMessage type={message.role} message={message.content} />
						{/each}

						{#if $answer}
							<ChatMessage type="assistant" message={$answer} />
						{/if}
					</div>
				</div>
			</div>

			<!-- Fixed Input Form -->
			<form
				class="flex w-full gap-4 rounded-lg border-t bg-white bg-opacity-100 p-4"
				on:submit|preventDefault={handleSubmit}
			>
				<Input type="text" bind:value={query} class="w-full" />
				<Button type="submit">
					<Send />
				</Button>
			</form>
		</main>
	</div>
</div>
