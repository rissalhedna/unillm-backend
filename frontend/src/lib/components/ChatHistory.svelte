<script lang="ts">
  import { onMount } from "svelte";
  import Ellipsis from "lucide-svelte/icons/ellipsis";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import { Button } from "$lib/components/ui/button";
  import { chatMessages } from "$lib/stores/chat-messages";
  import {
    chatHistorySubscription,
    loadMessages,
    deleteChat,
    updateChatTitle,
    fetchChats,
    activeChat
  } from "../stores/chat-history";
  import { MessageSquare, Pencil, Plus, Trash2, Share } from "lucide-svelte";

  interface Chat {
    id: string;
    title: string;
    messages: Array<{
      role: string;
      content: string;
    }>;
  }

  let chats: Chat[] = [];
  let editingChatId: string | null = null;
  let newTitle = "";
  let isLoading = false;

  onMount(async () => {
    await fetchChats();
    chatHistorySubscription.subscribe((value) => {
      if (value) {
        chats = value as Chat[];
      }
    });
  });

  async function handleChatSelect(chatId: string) {
    isLoading = true;
    await loadMessages(chatId);
    isLoading = false;
  }

  async function handleDelete(chatId: string, event: Event) {
    event.stopPropagation();
    await deleteChat(chatId);
    if ($activeChat === chatId) {
      chatMessages.reset();
      activeChat.set(null);
    }
  }

  function startEditing(chat: Chat, event: Event) {
    event.stopPropagation();
    editingChatId = chat.id;
    newTitle = chat.title;
  }

  async function handleRename(chatId: string) {
    if (newTitle.trim()) {
      await updateChatTitle(chatId, newTitle.trim());
      editingChatId = null;
    }
  }

  function handleNewChat() {
    chatMessages.reset();
    activeChat.set(null);
  }
</script>

<div class="flex flex-col h-full">
  <div class="flex-none p-4">
    <button
      on:click={handleNewChat}
      class="w-full flex items-center gap-3 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-3 text-sm transition-colors duration-200 hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      <Plus class="h-4 w-4" /> New chat
    </button>
  </div>

  <div class="flex-1 overflow-y-auto px-2">
    <div class="flex flex-col gap-2">
      {#each chats as chat (chat.id)}
        <div
          class="group relative flex items-center gap-3 rounded-lg px-3 py-3 
                {$activeChat === chat.id
            ? 'bg-gray-100 dark:bg-gray-800'
            : 'hover:bg-gray-50 dark:hover:bg-gray-900'}"
        >
          <MessageSquare class="h-4 w-4 flex-none" />
          
          {#if editingChatId === chat.id}
            <!-- svelte-ignore a11y-autofocus -->
            <input
              type="text"
              bind:value={newTitle}
              class="flex-1 bg-transparent border-b border-gray-300 dark:border-gray-600 focus:outline-none focus:border-blue-500"
              on:blur={() => handleRename(chat.id)}
              on:keydown={(e) => e.key === 'Enter' && handleRename(chat.id)}
              autofocus
            />
          {:else}
            <button
              on:click={() => handleChatSelect(chat.id)}
              class="flex-1 text-left text-sm truncate"
            >
              {chat.title}
            </button>
          {/if}

          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild let:builder>
              <Button
                variant="ghost"
                builders={[builder]}
                size="icon"
                class="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <span class="sr-only">Open menu</span>
                <Ellipsis class="h-4 w-4" />
              </Button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="end">
              <DropdownMenu.Item on:click={(e) => startEditing(chat, e)}>
                <Pencil class="h-4 w-4 mr-2" />
                Rename
              </DropdownMenu.Item>
              <DropdownMenu.Item>
                <Share class="h-4 w-4 mr-2" />
                Share
              </DropdownMenu.Item>
              <DropdownMenu.Separator />
              <DropdownMenu.Item 
                class="text-red-600 dark:text-red-400"
                on:click={(e) => handleDelete(chat.id, e)}
              >
                <Trash2 class="h-4 w-4 mr-2" />
                Delete
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      {/each}
    </div>
  </div>
</div>
