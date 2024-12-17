<script lang="ts">
  import { onMount } from "svelte";
  import Ellipsis from "lucide-svelte/icons/ellipsis";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import { Button } from "$lib/components/ui/button";
  import { chatMessages } from "$lib/stores/chat-messages";
  import {
    chatHistory,
    chatHistorySubscription,
    loadMessages,
  } from "../stores/chat-history";
  import { MessageSquare, Pencil, Plus, Trash } from "lucide-svelte";

  let chatHistoryKeys: any = [];
  let activeChat: string | null = null;

  onMount(() => {
    chatHistorySubscription.set($chatHistory);
    chatHistorySubscription.subscribe((value: any) => {
      chatHistoryKeys = Object.keys(value);
    });
  });

  function handleChatSelect(message: string) {
    activeChat = message;
    loadMessages(message);
  }
</script>

<div class="flex flex-col gap-2 overflow-y-auto rounded-md px-2 py-4">
  <button
    on:click={() => {
      chatMessages.reset();
      activeChat = null;
    }}
    class="flex flex-shrink-0 cursor-pointer items-center gap-3 rounded-lg border border-white/20 px-3 py-3 text-sm transition-colors duration-200 hover:bg-gray-500/10"
  >
    <Plus /> New chat
  </button>

  <hr class="border-gray-200 dark:border-gray-800" />

  {#if chatHistoryKeys.length > 0}
    {#each chatHistoryKeys as message (message)}
      <button
        on:click={() => handleChatSelect(message)}
        class="animate-flash group relative flex cursor-pointer items-center gap-3 break-all rounded-lg px-3 py-3 pr-14 text-sm transition-colors
                    {activeChat === message
          ? 'bg-gray-100 dark:bg-gray-800'
          : 'hover:bg-gray-50 dark:hover:bg-gray-900'}"
      >
        <MessageSquare />
        <div
          class="relative max-h-5 flex-1 overflow-hidden text-ellipsis break-all"
        >
          {message}
        </div>
        <div class="visible absolute right-1 z-10 flex text-gray-300">
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild let:builder>
              <Button
                variant="ghost"
                builders={[builder]}
                size="icon"
                class="relative h-8 w-8 rounded-full p-0 hover:bg-gray-200/10"
              >
                <span class="sr-only">Open menu</span>
                <Ellipsis class="h-4 w-4" />
              </Button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Content>
              <DropdownMenu.Group>
                <DropdownMenu.Label>Actions</DropdownMenu.Label>
                <DropdownMenu.Item on:click={() => {}}>Share</DropdownMenu.Item>
              </DropdownMenu.Group>
              <DropdownMenu.Separator />
              <DropdownMenu.Item>Rename</DropdownMenu.Item>
              <DropdownMenu.Item>Delete</DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </button>
    {/each}
  {/if}
</div>
