<script lang="ts">
  import { marked } from "marked";
  import DOMPurify from "isomorphic-dompurify";
  import { onMount } from "svelte";

  enum ChatCompletionRequestMessageRoleEnum {
    user = "user",
    assistant = "assistant",
    system = "system",
  }

  export let type: ChatCompletionRequestMessageRoleEnum;
  export let message: string = "";
  export let isLoading: boolean = false;
  export { classes as class };

  let classes = "";
  let scrollToDiv: HTMLDivElement;

  const classSet = {
    user: "justify-end",
    assistant: "justify-start",
    system: "justify-center text-gray-400",
  };

  const messageClasses = {
    user: "bg-blue-500 text-white",
    assistant: "bg-gray-200 dark:bg-gray-700",
    system: "bg-gray-100 dark:bg-gray-800",
  };

  const typeEffect = (node: HTMLDivElement, message: string) => {
    return {
      update(message: string) {
        scrollToDiv.scrollIntoView({
          behavior: "auto",
          block: "end",
          inline: "end",
        });
      },
    };
  };

  onMount(() => {
    scrollToDiv.scrollIntoView({
      behavior: "auto",
      block: "end",
      inline: "end",
    });
  });
</script>

<div class="flex items-center {classSet[type]}">
  <p class="px-2 text-xs text-gray-500">
    {type === "user" ? "Me" : "Assistant"}
  </p>
</div>

<div class="flex {classSet[type]} mb-1">
  <div
    use:typeEffect={message}
    class="max-w-[85%] rounded-lg px-4 py-3 {classes} {messageClasses[type]}"
  >
    {#if isLoading && type === 'assistant'}
      <div class="flex flex-col gap-2 w-[300px]">
        <div class="flex gap-1 mt-2">
          <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" />
          <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]" />
          <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]" />
        </div>
      </div>
    {:else}
      {@html DOMPurify.sanitize(marked.parse(message).toString())}
    {/if}
  </div>
  <div bind:this={scrollToDiv} />
</div>
