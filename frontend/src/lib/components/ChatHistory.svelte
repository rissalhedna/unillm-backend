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
  } from "$lib/stores/chat-history";
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

<div class="flex flex-col h-full overflow-y-scroll">
  <div class="flex-none p-2">
    <button
      on:click={handleNewChat}
      class="w-full flex items-center gap-2 rounded-lg
             border border-[#dd1c1a]/20 px-2 py-2 text-sm
             transition-colors duration-200
             hover:bg-[#dd1c1a]/5 dark:hover:bg-[#dd1c1a]/10"
    >
      <Plus class="h-4 w-4" /> New chat
    </button>
  </div>

  <div class="flex-1 overflow-y-auto px-3">
    <div class="flex flex-col gap-1">
      {#each chats as chat (chat.id)}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div
          on:click={() => handleChatSelect(chat.id)}
          class="group relative flex items-center gap-2 rounded-lg px-2 py-2 cursor-pointer
                {$activeChat === chat.id
            ? 'bg-[#dd1c1a]/10 dark:bg-[#dd1c1a]/20'
            : 'hover:bg-[#dd1c1a]/5 dark:hover:bg-[#dd1c1a]/10'}"
        >
          <MessageSquare class="h-4 w-4 flex-none" />

          {#if editingChatId === chat.id}
            <!-- svelte-ignore a11y-autofocus -->
            <input
              type="text"
              bind:value={newTitle}
              class="flex-1 bg-transparent border-b
                     border-[#dd1c1a]/30
                     focus:outline-none focus:border-[#dd1c1a]"
              on:blur={() => handleRename(chat.id)}
              on:keydown={(e) => e.key === 'Enter' && handleRename(chat.id)}
              autofocus
            />
          {:else}
            <div class="flex-1 text-left text-sm truncate">
              {chat.title}
            </div>
          {/if}

          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild let:builder>
              <Button
                variant="ghost"
                builders={[builder]}
                size="icon"
                class="h-8 w-8 p-0 opacity-0 group-hover:opacity-100
                       transition-opacity hover:bg-[#dd1c1a]/5
                       dark:hover:bg-[#dd1c1a]/10"
                on:click={(e) => e.stopPropagation()}
              >
                <span class="sr-only">Open menu</span>
                <Ellipsis class="h-4 w-4" />
              </Button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="end">
              <DropdownMenu.Item
                on:click={(e) => startEditing(chat, e)}
                class="hover:bg-[#dd1c1a]/5 dark:hover:bg-[#dd1c1a]/10"
              >
                <Pencil class="h-4 w-4 mr-2" />
                Rename
              </DropdownMenu.Item>
              <DropdownMenu.Item
                class="hover:bg-[#dd1c1a]/5 dark:hover:bg-[#dd1c1a]/10"
              >
                <Share class="h-4 w-4 mr-2" />
                Share
              </DropdownMenu.Item>
              <DropdownMenu.Separator />
              <DropdownMenu.Item
                class="text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20"
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
